import os
import unittest

from github_repo_mirror.payload import GithubPayload


class GithubPayloadTestCase(unittest.TestCase):

    def setUp(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        samples_dir = os.path.join(current_dir, 'samples')
        with open(os.path.join(samples_dir, 'sample_payload.json')) as fp:
            self.sample_payload = fp.read()

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

    def test_parse_url(self):
        payload = GithubPayload('{}')
        url_pieces = payload._parse_url('https://github.com/foo/bar.git')
        self.assertEqual(url_pieces['username'], 'foo')
        self.assertEqual(url_pieces['repository_name'], 'bar')

