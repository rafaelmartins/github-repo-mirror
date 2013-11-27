import unittest
from ipaddress import AddressValueError

from github_repo_mirror.utils import request_allowed


class RequestAllowedTestCase(unittest.TestCase):

    def test_valid_ip(self):
        self.assertTrue(request_allowed('192.30.254.123', '192.30.252.0/22'))

    def test_invalid_ip(self):
        self.assertFalse(request_allowed('192.30.251.123', '192.30.252.0/22'))

    def test_ipv6(self):
        self.assertRaises(AddressValueError,
                          request_allowed,
                          '1050::5:600:300c:326b', '192.30.252.0/22')

    def test_private_ip(self):
        self.assertTrue(request_allowed('192.168.0.1', '192.30.252.0/22',
                                        True))

    def test_private_ip_without_debug(self):
        self.assertFalse(request_allowed('192.168.0.1', '192.30.252.0/22',
                                         False))

