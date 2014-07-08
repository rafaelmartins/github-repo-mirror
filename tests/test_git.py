import mock
import os
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

            def get_remote_url(self, username=None, password=None):
                return self.repository_url

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

    @mock.patch('github_repo_mirror.git.subprocess.check_output')
    @mock.patch('github_repo_mirror.git.os.path.isfile')
    @mock.patch('github_repo_mirror.git.os.access')
    def test_call_hook(self, access, isfile, check_output):
        access.return_value = True
        isfile.return_value = True
        git = Git('/tmp', self.payload, git_cmd='foo')
        git._call_hook()
        access.assert_called_once_with(
            '/tmp/foo/bar.git/hooks/github-repo-mirror', os.X_OK)
        isfile.assert_called_once_with(
            '/tmp/foo/bar.git/hooks/github-repo-mirror')
        check_output.assert_called_once_with('./hooks/github-repo-mirror',
                                             shell=True,
                                             cwd='/tmp/foo/bar.git',
                                             stderr=-2)

    @mock.patch('github_repo_mirror.git.Git._call_hook')
    @mock.patch('github_repo_mirror.git.Git._call_git')
    @mock.patch('github_repo_mirror.git.os.path.isdir')
    @mock.patch('github_repo_mirror.git.os.makedirs')
    def test_sync_repo_clone(self, makedirs, isdir, _call_git, _call_hook):
        isdir.return_value = False
        git = Git('/tmp', self.payload)
        git.sync_repo()
        makedirs.assert_called_once_with('/tmp/foo/bar.git', 0755)
        self.assertEqual(isdir.call_args_list,
                         [mock.call('/tmp/foo/bar.git/objects'),
                          mock.call('/tmp/foo/bar.git')])
        _call_git.assert_called_once_with(['clone', '--bare',
                                           'https://github.com/foo/bar', '.'])
        _call_hook.assert_called_once_with()

    @mock.patch('github_repo_mirror.git.Git._call_hook')
    @mock.patch('github_repo_mirror.git.Git._call_git')
    @mock.patch('github_repo_mirror.git.os.path.isdir')
    @mock.patch('github_repo_mirror.git.os.makedirs')
    def test_sync_repo_fetch(self, makedirs, isdir, _call_git, _call_hook):
        isdir.return_value = True
        git = Git('/tmp', self.payload)
        git.sync_repo()
        self.assertFalse(makedirs.called)
        isdir.assert_called_once_with('/tmp/foo/bar.git/objects')
        self.assertEqual(_call_git.call_args_list, [
            mock.call(['remote', 'set-url', 'origin',
                       'https://github.com/foo/bar']),
            mock.call(['fetch', 'origin', '+refs/heads/*:refs/heads/*']),
            mock.call(['fetch', 'origin', '+refs/tags/*:refs/tags/*'])])
        _call_hook.assert_called_once_with()

    @mock.patch('github_repo_mirror.git.Git._call_hook')
    @mock.patch('github_repo_mirror.git.Git._call_git')
    @mock.patch('github_repo_mirror.git.os.path.isdir')
    @mock.patch('github_repo_mirror.git.os.makedirs')
    def test_sync_repo_fetch_without_origin(self, makedirs, isdir, _call_git,
                                            _call_hook):
        def _call_git_side_effect(args):
            if 'set-url' in args:
                raise RuntimeError('bola')
            return ''
        _call_git.side_effect = _call_git_side_effect
        isdir.return_value = True
        git = Git('/tmp', self.payload)
        git.sync_repo()
        self.assertFalse(makedirs.called)
        isdir.assert_called_once_with('/tmp/foo/bar.git/objects')
        self.assertEqual(_call_git.call_args_list, [
            mock.call(['remote', 'set-url', 'origin',
                       'https://github.com/foo/bar']),
            mock.call(['remote', 'add', '--mirror=fetch', 'origin',
                       'https://github.com/foo/bar']),
            mock.call(['fetch', 'origin', '+refs/heads/*:refs/heads/*']),
            mock.call(['fetch', 'origin', '+refs/tags/*:refs/tags/*'])])
        _call_hook.assert_called_once_with()
