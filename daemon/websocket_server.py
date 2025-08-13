"""
Serveur WebSocket pour la communication avec le navigateur
"""

import asyncio
import json
import logging
import ssl
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List

import jwt
import websockets

from config_manager import ConfigManager
from usb_monitor import USBEvent


class WebSocketServer:
    """Serveur WebSocket pour communiquer avec le navigateur."""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.server = None
        self.connected_clients: set[Any] = set()
        self.client_tokens: Dict[str, Dict[str, Any]] = {}
        self.running = False
    
    async def start(self):
        """Démarre le serveur WebSocket."""
        self.running = True
        self.logger.info(f"🚀 Démarrage du serveur WebSocket sur {self.config.websocket.host}:{self.config.websocket.port}")
        
        try:
            # Configuration SSL si activée
            ssl_context = self._create_ssl_context()
            
            # Démarrage du serveur avec la nouvelle API
            self.server = await websockets.serve(
                self.handle_client, # pyright: ignore[reportArgumentType]
                self.config.websocket.host,
                self.config.websocket.port,
                ssl=ssl_context
            )
            
            self.logger.info("✅ Serveur WebSocket démarré")
            
            # Maintenir le serveur en vie en attendant qu'il soit fermé
            await self.server.wait_closed()
                
        except Exception as e:
            self.logger.error(f"Erreur lors du démarrage du serveur WebSocket : {e}")
            self.running = False
    
    async def stop(self):
        """Arrête le serveur WebSocket."""
        self.running = False
        
        self.logger.info("Arrêt du serveur WebSocket")
        
        # Fermeture des connexions clients
        if self.connected_clients:
            self.logger.info(f"Fermeture de {len(self.connected_clients)} connexions clients")
            await asyncio.gather(
                *[client.close() for client in self.connected_clients.copy()],
                return_exceptions=True
            )
            self.connected_clients.clear()
        
        # Fermeture du serveur
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            
        self.logger.info("✅ Serveur WebSocket arrêté")
    
    def _create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Crée le contexte SSL si activé."""
        if not self.config.websocket.ssl_enabled:
            return None
        
        ssl_config = self.config.get_ssl_context()
        if not ssl_config:
            self.logger.warning("SSL activé mais certificats manquants")
            return None
        
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.minimum_version = ssl.TLSVersion.TLSv1_2  # Version sécurisée minimum
            context.load_cert_chain(ssl_config[0], ssl_config[1])
            return context
        except Exception as e:
            self.logger.error(f"Erreur lors de la création du contexte SSL : {e}")
            return None
    
    async def handle_client(self, websocket: Any, path: str) -> None:
        """Gère une connexion client WebSocket."""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self.logger.info(f"Nouvelle connexion WebSocket : {path} ({client_id})")
        
        # Ajouter le client à la liste des connectés
        self.connected_clients.add(websocket)
        
        try:
            # Traitement des messages
            async for message in websocket:
                self.logger.debug(f"📨 Message reçu de {client_id}: {message}")
                await self.handle_message(websocket, message, client_id)
                
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"🔌 Connexion fermée proprement : {client_id}")
        except Exception as e:
            self.logger.error(f"❌ Erreur avec le client WebSocket {client_id}: {e}")
        finally:
            # Retirer le client de la liste des connectés
            self.connected_clients.discard(websocket)
            # Nettoyer les tokens du client
            self.client_tokens.pop(client_id, None)
            self.logger.info(f"🗑️ Client {client_id} déconnecté et nettoyé")
    
    async def handle_message(self, websocket: Any, message: str, client_id: str):
        """Traite un message reçu d'un client."""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'auth':
                await self.handle_auth(websocket, data, client_id)
            elif message_type == 'ping':
                await self.send_message(websocket, {'type': 'pong', 'timestamp': datetime.now().isoformat()})
            elif message_type == 'get_status':
                await self.handle_status_request(websocket, client_id)
            else:
                await self.send_error(websocket, f"Type de message inconnu : {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error(websocket, "Message JSON invalide")
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement du message : {e}")
            await self.send_error(websocket, "Erreur interne du serveur")
    
    async def handle_auth(self, websocket: Any, data: Dict[str, Any], client_id: str):
        """Gère l'authentification d'un client."""
        try:
            # Validation du token s'il est fourni
            provided_token = data.get('token')
            if provided_token and self.validate_token(provided_token):
                self.client_tokens[client_id] = {
                    'token': provided_token,
                    'authenticated': True,
                    'timestamp': datetime.now()
                }
                await self.send_message(websocket, {
                    'type': 'auth_success',
                    'message': 'Authentification réussie'
                })
                return
            
            # Génération d'un nouveau token
            new_token = self.generate_token(client_id)
            self.client_tokens[client_id] = {
                'token': new_token,
                'authenticated': True,
                'timestamp': datetime.now()
            }
            
            await self.send_message(websocket, {
                'type': 'auth_token',
                'token': new_token,
                'expires_in': self.config.security.token_expiry
            })
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'authentification : {e}")
            await self.send_error(websocket, "Erreur d'authentification")
    
    async def handle_status_request(self, websocket: Any, client_id: str):
        """Gère une demande de statut."""
        if not self.is_client_authenticated(client_id):
            await self.send_error(websocket, "Client non authentifié")
            return
        
        # Récupération du statut des clés USB connectées
        # Cette information viendra du USBMonitor via le daemon principal
        status: Dict[str, Any] = {
            'type': 'status',
            'connected_keys': [],  # Sera rempli par le daemon principal
            'daemon_status': 'running' if self.running else 'stopped',
            'clients_count': self.get_connected_clients_count(),
            'authenticated_clients': self.get_authenticated_clients_count(),
            'timestamp': datetime.now().isoformat()
        }
        
        await self.send_message(websocket, status)
    
    def generate_token(self, client_id: str) -> str:
        """Génère un token JWT pour un client."""
        payload: Dict[str, Any] = {
            'client_id': client_id,
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc) + timedelta(seconds=self.config.security.token_expiry)
        }
        
        return jwt.encode(payload, self.config.security.jwt_secret, algorithm='HS256')
    
    def validate_token(self, token: str) -> bool:
        """Valide un token JWT."""
        try:
            jwt.decode(token, self.config.security.jwt_secret, algorithms=['HS256'])
            return True
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expiré")
            return False
        except jwt.InvalidTokenError:
            self.logger.warning("Token invalide")
            return False
    
    def is_client_authenticated(self, client_id: str) -> bool:
        """Vérifie si un client est authentifié."""
        client_info = self.client_tokens.get(client_id)
        if not client_info:
            return False
        
        return (
            client_info.get('authenticated', False) and
            self.validate_token(client_info.get('token', ''))
        )
    
    async def send_message(self, websocket: Any, message: Dict[str, Any]):
        """Envoie un message à un client."""
        try:
            await websocket.send(json.dumps(message))
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message : {e}")
    
    async def send_error(self, websocket: Any, error_message: str):
        """Envoie un message d'erreur à un client."""
        await self.send_message(websocket, {
            'type': 'error',
            'message': error_message,
            'timestamp': datetime.now().isoformat()
        })
    
    async def broadcast_event(self, event: USBEvent):
        """Diffuse un événement USB à tous les clients authentifiés."""
        if not self.connected_clients:
            return
        
        message: Dict[str, Any] = {
            'type': 'usb_event',
            'event_type': event.event_type,
            'device_path': event.device_path,
            'is_cryptusbee': event.is_cryptusbee,
            'timestamp': event.timestamp,
            'validation_status': event.validation_status
        }
        
        self.logger.info(f"📡 Diffusion d'événement USB : {event.event_type}")
        
        # Envoi aux clients authentifiés
        authenticated_clients: List[Any] = []
        for websocket in self.connected_clients.copy():
            try:
                client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
                if self.is_client_authenticated(client_id):
                    authenticated_clients.append(websocket)
            except Exception:
                # Connexion fermée ou adresse non disponible
                self.connected_clients.discard(websocket)
        
        if authenticated_clients:
            await asyncio.gather(
                *[self.send_message(client, message) for client in authenticated_clients],
                return_exceptions=True
            )
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Diffuse un message à tous les clients connectés."""
        if self.connected_clients:
            await asyncio.gather(
                *[self.send_message(client, message) for client in self.connected_clients],
                return_exceptions=True
            )
    
    def get_connected_clients_count(self) -> int:
        """Retourne le nombre de clients connectés."""
        return len(self.connected_clients)
    
    def get_authenticated_clients_count(self) -> int:
        """Retourne le nombre de clients authentifiés."""
        return len([
            client_id for client_id in self.client_tokens
            if self.is_client_authenticated(client_id)
        ])
