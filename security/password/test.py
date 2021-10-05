import unittest

from faker import Faker

from security.password import PasswordUtils


class TestPasswordUtils(unittest.TestCase):

    def setUp(self):
        self.fake = Faker()

    def test_ability_to_encrypt_and_decrypt(self):
        password = self.fake.password()

        encrypted = PasswordUtils().encrypt(password)
        assert encrypted != password

        decrypted = PasswordUtils().decrypt(encrypted)
        assert decrypted == password
