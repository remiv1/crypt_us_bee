"""
Tests unitaires pour le daemon CryptUSBee
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any

import pytest

# Import des modules du daemon
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config_manager import ConfigManager
from usb_monitor import USBEvent, USBValidator
from websocket_server import WebSocketServer


class TestConfigManager(unittest.TestCase):
    """Tests pour le gestionnaire de configuration."""
    
    def setUp(self):
        """Préparation des tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
    
    def tearDown(self):
        """Nettoyage après les tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_config_creation(self):
        """Test de création d'une configuration par défaut."""
        config = ConfigManager(self.config_path)
        
        # Vérification des valeurs par défaut
        self.assertEqual(config.websocket.host, "localhost")
        self.assertEqual(config.websocket.port, 8765)
        self.assertEqual(config.usb.label, "CRYPTUSB")
        self.assertEqual(config.security.token_expiry, 3600)
        self.assertEqual(config.logging.level, "INFO")
    
    def test_config_loading(self):
        """Test de chargement d'une configuration existante."""
        # Création d'un fichier de configuration
        test_config: Dict[str, Any] = {
            "websocket": {"host": "127.0.0.1", "port": 9000},
            "usb": {"label": "TESTKEY", "poll_interval": 2000},
            "security": {"token_expiry": 7200},
            "logging": {"level": "DEBUG"}
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        # Chargement et vérification
        config = ConfigManager(self.config_path)
        self.assertEqual(config.websocket.host, "127.0.0.1")
        self.assertEqual(config.websocket.port, 9000)
        self.assertEqual(config.usb.label, "TESTKEY")
        self.assertEqual(config.usb.poll_interval, 2000)
    
    def test_config_update(self):
        """Test de mise à jour de configuration."""
        config = ConfigManager(self.config_path)
        
        # Mise à jour d'une valeur
        config.update_config("websocket", "port", 9999)
        
        # Vérification
        self.assertEqual(config.websocket.port, 9999)
        
        # Vérification de la persistance
        config2 = ConfigManager(self.config_path)
        self.assertEqual(config2.websocket.port, 9999)
    
    def test_invalid_config_update(self):
        """Test de mise à jour avec des paramètres invalides."""
        config = ConfigManager(self.config_path)
        
        with self.assertRaises(ValueError):
            config.update_config("invalid_section", "key", "value")
        
        with self.assertRaises(ValueError):
            config.update_config("websocket", "invalid_key", "value")


class TestUSBValidator(unittest.TestCase):
    """Tests pour le validateur USB."""
    
    def setUp(self):
        """Préparation des tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ConfigManager()
        self.validator = USBValidator(self.config)
    
    def tearDown(self):
        """Nettoyage après les tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_invalid_label(self):
        """Test avec un label incorrect."""
        device_path = Path(self.temp_dir) / "WRONGLABEL"
        device_path.mkdir()
        
        result = self.validator.validate_cryptusbee_key(device_path)
        self.assertFalse(result["valid"])
        self.assertIn("Label incorrect", result["reason"])
    
    def test_missing_key_folder(self):
        """Test avec un dossier de clé manquant."""
        device_path = Path(self.temp_dir) / "CRYPTUSB"
        device_path.mkdir()
        
        result = self.validator.validate_cryptusbee_key(device_path)
        self.assertFalse(result["valid"])
        self.assertIn("Dossier clé manquant", result["reason"])
    
    def test_missing_key_files(self):
        """Test avec des fichiers de clé manquants."""
        device_path = Path(self.temp_dir) / "CRYPTUSB"
        device_path.mkdir()
        
        key_folder = device_path / self.config.usb.key_folder
        key_folder.mkdir()
        
        result = self.validator.validate_cryptusbee_key(device_path)
        self.assertFalse(result["valid"])
        self.assertIn("Fichiers de clé manquants", result["reason"])
    
    @patch('Crypto.PublicKey.RSA.import_key')
    def test_valid_cryptusbee_key(self, mock_import_key: Mock):
        """Test avec une clé CryptUSBee valide."""
        # Préparation de la structure
        device_path = Path(self.temp_dir) / "CRYPTUSB"
        device_path.mkdir()
        
        key_folder = device_path / self.config.usb.key_folder
        key_folder.mkdir()
        
        id_file = key_folder / "id_bee.key"
        public_key_file = key_folder / "public_bee.pem"
        
        # Création de fichiers factices
        id_file.write_bytes(b"encrypted_id_data")
        public_key_file.write_bytes(b"public_key_data")
        
        # Mock de la clé RSA
        mock_key = Mock()
        mock_key.n = 123456789
        mock_import_key.return_value = mock_key
        
        result = self.validator.validate_cryptusbee_key(device_path)
        self.assertTrue(result["valid"])
        self.assertIn("key_id", result)
        self.assertIn("public_key_fingerprint", result)


class TestUSBEvent(unittest.TestCase):
    """Tests pour les événements USB."""
    
    def test_usb_event_creation(self):
        """Test de création d'un événement USB."""
        device_info = {"mountpoint": "/dev/sdb1", "fstype": "vfat"}
        event = USBEvent("inserted", "/media/CRYPTUSB", device_info)
        
        self.assertEqual(event.event_type, "inserted")
        self.assertEqual(event.device_path, "/media/CRYPTUSB")
        self.assertEqual(event.device_info, device_info)
        self.assertFalse(event.is_cryptusbee)
        self.assertEqual(event.validation_status, "unknown")
        self.assertIsInstance(event.timestamp, float)


@pytest.mark.asyncio
class TestWebSocketServer:
    """Tests pour le serveur WebSocket."""
    
    @pytest.fixture
    def config(self):
        """Configuration de test."""
        return ConfigManager()
    
    @pytest.fixture
    def websocket_server(self, config):
        """Instance de serveur WebSocket pour les tests."""
        return WebSocketServer(config)
    
    def test_websocket_server_initialization(self, websocket_server: WebSocketServer):
        """Test d'initialisation du serveur WebSocket."""
        assert websocket_server.config is not None
        assert websocket_server.connected_clients == set()  # type: ignore
        assert websocket_server.client_tokens == {}
        assert not websocket_server.running

    def test_jwt_token_generation(self, websocket_server: WebSocketServer):
        """Test de génération de token JWT."""
        client_id = "test_client"
        token = websocket_server.generate_token(client_id)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Validation du token
        assert websocket_server.validate_token(token)

    def test_jwt_token_validation(self, websocket_server: WebSocketServer):
        """Test de validation de token JWT."""
        # Token valide
        client_id = "test_client"
        valid_token = websocket_server.generate_token(client_id)
        assert websocket_server.validate_token(valid_token)
        
        # Token invalide
        invalid_token = "invalid.token.string"
        assert not websocket_server.validate_token(invalid_token)

    async def test_message_handling(self, websocket_server: WebSocketServer):
        """Test de traitement des messages."""
        # Mock WebSocket
        mock_websocket = Mock()
        mock_websocket.remote_address = ("127.0.0.1", 12345)
        
        client_id = "127.0.0.1:12345"
        
        # Test message d'authentification
        auth_message = json.dumps({"type": "auth"})
        await websocket_server.handle_message(mock_websocket, auth_message, client_id)
        
        # Vérification que le client est authentifié
        assert client_id in websocket_server.client_tokens
        assert websocket_server.is_client_authenticated(client_id)
    
    async def test_broadcast_event(self, websocket_server: WebSocketServer):
        """Test de diffusion d'événements."""
        # Création d'un événement USB
        device_info = {"mountpoint": "/media/CRYPTUSB"}
        usb_event = USBEvent("inserted", "/media/CRYPTUSB", device_info)
        usb_event.is_cryptusbee = True
        usb_event.validation_status = {"valid": True, "key_id": "test123"}
        
        # Mock des clients connectés
        mock_client1 = Mock()
        mock_client1.remote_address = ("127.0.0.1", 12345)
        mock_client2 = Mock()
        mock_client2.remote_address = ("127.0.0.1", 12346)
        
        websocket_server.connected_clients.add(mock_client1)
        websocket_server.connected_clients.add(mock_client2)
        
        # Authentification des clients
        websocket_server.client_tokens["127.0.0.1:12345"] = {
            'token': websocket_server.generate_token("127.0.0.1:12345"),
            'authenticated': True
        }
        websocket_server.client_tokens["127.0.0.1:12346"] = {
            'token': websocket_server.generate_token("127.0.0.1:12346"),
            'authenticated': True
        }
        
        # Test de diffusion
        await websocket_server.broadcast_event(usb_event)
        
        # Vérification que les messages ont été envoyés
        # (Dans un vrai test, on vérifierait les appels à websocket.send())


class TestIntegration(unittest.TestCase):
    """Tests d'intégration pour le daemon."""
    
    def setUp(self):
        """Préparation des tests d'intégration."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "integration_config.json"
    
    def tearDown(self):
        """Nettoyage après les tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('psutil.disk_partitions')
    def test_usb_detection_workflow(self, mock_partitions):
        """Test du workflow complet de détection USB."""
        # Mock des partitions système
        mock_partition = Mock()
        mock_partition.mountpoint = str(Path(self.temp_dir) / "CRYPTUSB")
        mock_partition.opts = "rw,removable"
        mock_partition.fstype = "vfat"
        mock_partitions.return_value = [mock_partition]
        
        # Création de la structure de clé factice
        cryptusb_path = Path(self.temp_dir) / "CRYPTUSB"
        cryptusb_path.mkdir()
        
        key_folder = cryptusb_path / ".cryptusbee"
        key_folder.mkdir()
        
        (key_folder / "id_bee.key").write_bytes(b"fake_encrypted_id")
        (key_folder / "public_bee.pem").write_bytes(b"fake_public_key")
        
        # Configuration et validation
        config = ConfigManager(self.config_path)
        validator = USBValidator(config)
        
        # Test de validation
        result = validator.validate_cryptusbee_key(cryptusb_path)
        
        # Vérification (devrait échouer car les clés sont factices)
        self.assertFalse(result["valid"])
        self.assertIn("Erreur cryptographique", result["reason"])


if __name__ == "__main__":
    # Exécution des tests
    unittest.main(verbosity=2)
