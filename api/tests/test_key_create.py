import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import sys
from keys_creation.key_create import find_usb_mount, generate_keys, encrypt_identifier, write_to_usb
from keys_creation import USB_LABEL, IDENTIFIER_FILE, PUBLIC_KEY_FILE, KEY_FOLDER
sys.path.append("i:\\crypt_us_bee")

class TestKeyCreate(unittest.TestCase):

    @patch("keys_creation.key_create.psutil.disk_partitions")
    def test_find_usb_mount(self, mock_disk_partitions: MagicMock):
        mock_partition = MagicMock()
        mock_partition.opts = "removable"
        mock_partition.mountpoint = f"/media/{USB_LABEL}"
        mock_disk_partitions.return_value = [mock_partition]

        result = find_usb_mount()
        self.assertEqual(result, Path(f"/media/{USB_LABEL}"))

    def test_generate_keys(self):
        private_key, public_key = generate_keys()
        self.assertIsInstance(private_key, bytes)
        self.assertIsInstance(public_key, bytes)
        self.assertTrue(private_key.startswith(b"-----BEGIN RSA PRIVATE KEY-----"))
        self.assertTrue(public_key.startswith(b"-----BEGIN PUBLIC KEY-----"))

    @patch("keys_creation.key_create.RSA.import_key")
    @patch("keys_creation.key_create.PKCS1_OAEP.new")
    def test_encrypt_identifier(self, mock_cipher_new: MagicMock, mock_import_key: MagicMock):
        mock_cipher = MagicMock()
        mock_cipher.encrypt.return_value = b"encrypted_data"
        mock_cipher_new.return_value = mock_cipher

        public_key = b"public_key"
        result = encrypt_identifier(public_key)
        self.assertEqual(result, b"encrypted_data")

    @patch("keys_creation.key_create.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_to_usb(self, mock_open: MagicMock, mock_mkdir: MagicMock):
        mount_point = Path(f"/media/{USB_LABEL}")
        public_key = b"public_key_content"
        encrypted_id = b"encrypted_id_content"

        write_to_usb(mount_point, public_key, encrypted_id)

        mock_mkdir.assert_called_once_with(exist_ok=True)
        mock_open.assert_any_call(mount_point / KEY_FOLDER / PUBLIC_KEY_FILE, "wb")
        mock_open.assert_any_call(mount_point / KEY_FOLDER / IDENTIFIER_FILE, "wb")

        handle = mock_open()
        handle.write.assert_any_call(public_key)
        handle.write.assert_any_call(encrypted_id)

    def test_write_to_usb_real_files(self):
        # Répertoire temporaire pour les tests
        test_dir = Path("tests/pem")
        test_dir.mkdir(parents=True, exist_ok=True)

        mount_point = test_dir
        public_key = b"public_key_content"
        encrypted_id = b"encrypted_id_content"

        # Appelle la fonction réelle
        write_to_usb(mount_point, public_key, encrypted_id)

        # Vérifie que les fichiers ont été créés
        self.assertTrue((mount_point / KEY_FOLDER / PUBLIC_KEY_FILE).exists())
        self.assertTrue((mount_point / KEY_FOLDER / IDENTIFIER_FILE).exists())

        # Nettoyage des fichiers créés
        for file in (mount_point / KEY_FOLDER).iterdir():
            file.unlink()
        (mount_point / KEY_FOLDER).rmdir()
        test_dir.rmdir()

if __name__ == "__main__":
    unittest.main()
