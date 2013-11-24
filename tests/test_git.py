import mock
import subprocess
import unittest

from github_repo_mirror.git import Git


class GitTestCase(unittest.TestCase):

    def setUp(self):

        class FakePayload(object):
            username = 'foo'
            repository_name = 'bar'
            repository_path = 'foo/bar.git'
            repository_url = 'https://github.com/foo/bar'

        self.payload = FakePayload()

    def test_repo_path(self):
        git = Git('/tmp', self.payload)
        self.assertEqual(git.repo_path, '/tmp/foo/bar.git')

    @mock.patch('github_repo_mirror.git.subprocess.check_output')
    def test_call_git(self, check_output):
        git = Git('/tmp', self.payload, git_cmd='foo')
        git._call_git(['yay'])
        check_output.assert_called_once_with(['foo', 'yay'],
                                             cwd='/tmp/foo/bar.git',
                                             stderr=subprocess.STDOUT)

    @mock.patch('github_repo_mirror.git.Git._call_git')
    @mock.patch('github_repo_mirror.git.os.path.isdir')
    @mock.patch('github_repo_mirror.git.os.makedirs')
    def test_sync_repo_clone(self, makedirs, isdir, _call_git):
        isdir.return_value = False
        git = Git('/tmp', self.payload)
        git.sync_repo()
        makedirs.assert_called_once_with('/tmp/foo/bar.git')
        self.assertEqual(isdir.call_args_list,
                         [mock.call('/tmp/foo/bar.git/objects'),
                          mock.call('/tmp/foo/bar.git')])
        _call_git.assert_called_once_with(['clone', '--mirror',
                                           'https://github.com/foo/bar', '.'])

    @mock.patch('github_repo_mirror.git.Git._call_git')
    @mock.patch('github_repo_mirror.git.os.path.isdir')
    @mock.patch('github_repo_mirror.git.os.makedirs')
    def test_sync_repo_fetch(self, makedirs, isdir, _call_git):
        isdir.return_value = True
        git = Git('/tmp', self.payload)
        git.sync_repo()
        self.assertFalse(makedirs.called)
        isdir.assert_called_once_with('/tmp/foo/bar.git/objects')
        _call_git.assert_called_once_with(['remote', 'update'])
