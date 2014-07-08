import os
import unittest

from github_repo_mirror.payload import GithubPayload


class GithubPayloadTestCase(unittest.TestCase):

    def setUp(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        samples_dir = os.path.join(current_dir, 'samples')
        with open(os.path.join(samples_dir, 'sample_payload.json')) as fp:
            self.sample_payload = fp.read()
        with open(os.path.join(samples_dir,
                               'sample_payload_private.json')) as fp:
            self.sample_payload_private = fp.read()

    def test_username(self):
        payload = GithubPayload(self.sample_payload)
        self.assertEqual(payload.username, 'octokitty')

    def test_repository_name(self):
        payload = GithubPayload(self.sample_payload)
        self.assertEqual(payload.repository_name, 'testing')

    def test_repository_path(self):
        payload = GithubPayload(self.sample_payload)
        self.assertEqual(payload.repository_path,
                         os.path.join('octokitty', 'testing.git'))

    def test_repository_url(self):
        payload = GithubPayload(self.sample_payload)
        self.assertEqual(payload.repository_url,
                         'https://github.com/octokitty/testing')

    def test_public(self):
        payload = GithubPayload(self.sample_payload)
        self.assertFalse(payload.private)

    def test_private(self):
        payload = GithubPayload(self.sample_payload_private)
        self.assertTrue(payload.private)

    def test_parse_url(self):
        payload = GithubPayload('{}')
        url_pieces = payload._parse_url('https://github.com/foo/bar.baz.lol')
        self.assertEqual(url_pieces['username'], 'foo')
        self.assertEqual(url_pieces['repository_name'], 'bar.baz.lol')

    def test_get_remote_url(self):
        payload = GithubPayload(self.sample_payload)
        self.assertEqual(payload.get_remote_url(),
                         'https://github.com/octokitty/testing.git')
        self.assertEqual(payload.get_remote_url('bola'),
                         'https://github.com/octokitty/testing.git')
        self.assertEqual(payload.get_remote_url('bola', 'guda'),
                         'https://github.com/octokitty/testing.git')
        self.assertEqual(payload.get_remote_url('bola@guda', '@@'),
                         'https://github.com/octokitty/testing.git')

    def test_get_remote_url_private(self):
        payload = GithubPayload(self.sample_payload_private)
        self.assertEqual(payload.get_remote_url(),
                         'https://github.com/octokitty/testing.git')
        self.assertEqual(payload.get_remote_url('bola'),
                         'https://bola@github.com/octokitty/testing.git')
        self.assertEqual(payload.get_remote_url('bola', 'guda'),
                         'https://bola:guda@github.com/octokitty/testing.git')
        self.assertEqual(payload.get_remote_url('bola@guda', '@@'),
                         'https://bola%40guda:%40%40@github.com/octokitty/'
                         'testing.git')
