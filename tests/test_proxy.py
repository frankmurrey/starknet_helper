import unittest
from typing import Union

from utils.proxy import parse_proxy_data


class TestProxyDataParsing(unittest.TestCase):
    TEST_USER = "user"
    TEST_PASSWORD = "pass"
    TEST_HOST = "127.0.0.1"
    TEST_PORT = 8080

    def test_empty_string(self):
        self.assertIsNone(parse_proxy_data(''))

    def test_mobile_proxy_without_auth(self):
        proxy = parse_proxy_data(f"m$http://{self.TEST_HOST}:{self.TEST_PORT}")
        self.assertIsNotNone(proxy)
        self.assertTrue(proxy.is_mobile)
        self.assertEqual(proxy.host, self.TEST_HOST)
        self.assertEqual(proxy.port, self.TEST_PORT)
        self.assertEqual(proxy.proxy_type, "http")

    def test_non_mobile_proxy_without_auth(self):
        proxy = parse_proxy_data(f"http://{self.TEST_HOST}:{self.TEST_PORT}")
        self.assertIsNotNone(proxy)
        self.assertFalse(proxy.is_mobile)
        self.assertEqual(proxy.host, self.TEST_HOST)
        self.assertEqual(proxy.port, self.TEST_PORT)
        self.assertEqual(proxy.proxy_type, "http")

    def test_proxy_with_auth(self):
        proxy = parse_proxy_data(f"https://{self.TEST_HOST}:{self.TEST_PORT}:{self.TEST_USER}:{self.TEST_PASSWORD}")
        self.assertIsNotNone(proxy)
        self.assertTrue(proxy.auth)
        self.assertEqual(proxy.username, self.TEST_USER)
        self.assertEqual(proxy.password, self.TEST_PASSWORD)
        self.assertEqual(proxy.proxy_type, "https")

    def test_invalid_proxy_format(self):
        self.assertIsNone(parse_proxy_data(self.TEST_HOST))

    def test_incomplete_proxy_format(self):
        self.assertIsNone(parse_proxy_data(f"http://{self.TEST_HOST}"))

    def test_empty_proxy_string(self):
        self.assertIsNone(parse_proxy_data(""))

    def test_proxy_with_embedded_auth(self):
        proxy_str = f"{self.TEST_USER}:{self.TEST_PASSWORD}@{self.TEST_HOST}:{self.TEST_PORT}"
        proxy = parse_proxy_data(f"http://{proxy_str}")
        self.assertIsNotNone(proxy)
        self.assertTrue(proxy.auth)
        self.assertEqual(proxy.username, self.TEST_USER)
        self.assertEqual(proxy.password, self.TEST_PASSWORD)
        self.assertEqual(proxy.host, self.TEST_HOST)
        self.assertEqual(proxy.port, self.TEST_PORT)

    def test_mobile_proxy_with_embedded_auth(self):
        proxy_str = f"m$http://{self.TEST_USER}:{self.TEST_PASSWORD}@{self.TEST_HOST}:{self.TEST_PORT}"
        proxy = parse_proxy_data(proxy_str)
        self.assertIsNotNone(proxy)
        self.assertTrue(proxy.is_mobile)
        self.assertTrue(proxy.auth)
        self.assertEqual(proxy.username, self.TEST_USER)
        self.assertEqual(proxy.password, self.TEST_PASSWORD)
        self.assertEqual(proxy.host, self.TEST_HOST)
        self.assertEqual(proxy.port, self.TEST_PORT)

    def test_proxy_with_embedded_auth_and_incorrect_format(self):
        proxy_str = f"{self.TEST_USER}@{self.TEST_HOST}:{self.TEST_PORT}"
        self.assertIsNone(parse_proxy_data(f"http://{proxy_str}"))

    def test_proxy_with_embedded_auth_missing_port(self):
        proxy_str = f"{self.TEST_USER}:{self.TEST_PASSWORD}@{self.TEST_HOST}"
        self.assertIsNone(parse_proxy_data(f"http://{proxy_str}"))
