#!/usr/bin/env python3
"""
CryptUSBee Daemon - Service principal de surveillance USB
Point d'entrée principal du daemon CryptUSBee
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

from config_manager import ConfigManager
from usb_monitor import USBMonitor
from websocket_server import WebSocketServer


class CryptUSBeeDaemon:
    """Daemon principal de CryptUSBee pour la surveillance USB."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialise le daemon CryptUSBee.
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config = ConfigManager(config_path)
        self.logger = self._setup_logging()
        self.usb_monitor: Optional[USBMonitor] = None
        self.websocket_server: Optional[WebSocketServer] = None
        self._shutdown_event = asyncio.Event()
        
    def _setup_logging(self) -> logging.Logger:
        """Configure le système de logging."""
        logging.basicConfig(
            level=getattr(logging, self.config.logging.level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.logging.file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
    
    async def start(self):
        """Démarre le daemon et tous ses composants."""
        self.logger.info("🚀 Démarrage du daemon CryptUSBee")
        
        try:
            # Initialisation du serveur WebSocket
            self.websocket_server = WebSocketServer(self.config)
            
            # Initialisation du moniteur USB
            self.usb_monitor = USBMonitor(
                config=self.config,
                event_callback=self.websocket_server.broadcast_event
            )
            
            # Démarrage des services
            await asyncio.gather(
                self.websocket_server.start(),
                self.usb_monitor.start(),
                self._wait_for_shutdown()
            )
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du démarrage : {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Arrête proprement le daemon."""
        self.logger.info("🛑 Arrêt du daemon CryptUSBee")
        
        # Arrêt des composants
        if self.usb_monitor:
            await self.usb_monitor.stop()
        
        if self.websocket_server:
            await self.websocket_server.stop()
        
        self._shutdown_event.set()
    
    async def _wait_for_shutdown(self):
        """Attend le signal d'arrêt."""
        await self._shutdown_event.wait()
    
    def _signal_handler(self, signum, frame):
        """Gestionnaire de signaux pour arrêt propre."""
        self.logger.info(f"📡 Signal reçu: {signum}")
        asyncio.create_task(self.stop())


def main():
    """Point d'entrée principal."""
    daemon = CryptUSBeeDaemon()
    
    # Configuration des gestionnaires de signaux
    signal.signal(signal.SIGINT, daemon._signal_handler)
    signal.signal(signal.SIGTERM, daemon._signal_handler)
    
    try:
        # Démarrage du daemon
        asyncio.run(daemon.start())
    except KeyboardInterrupt:
        daemon.logger.info("⌨️ Interruption clavier détectée")
    except Exception as e:
        daemon.logger.error(f"💥 Erreur fatale : {e}")
        sys.exit(1)
    finally:
        daemon.logger.info("✅ Daemon arrêté proprement")


if __name__ == "__main__":
    main()
