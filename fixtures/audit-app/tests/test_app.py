"""Tests that fail until the crypto misuse in app.py is fixed."""

import hashlib
import importlib
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CryptoHygiene(unittest.TestCase):
    def setUp(self):
        import app
        self.app = importlib.reload(app)

    def test_rsa_key_bits_at_least_2048(self):
        self.assertGreaterEqual(self.app.KEY_BITS, 2048)

    def test_key_comes_from_environment(self):
        os.environ["APP_KEY"] = "x" * 32
        try:
            self.assertEqual(self.app.get_key(), b"x" * 32)
        finally:
            del os.environ["APP_KEY"]
        with self.assertRaises(RuntimeError):
            self.app.get_key()

    def test_password_hash_is_sha256(self):
        self.assertEqual(self.app.hash_password("abc"),
                         hashlib.sha256(b"abc").hexdigest())


if __name__ == "__main__":
    unittest.main()
