import os
import subprocess

from flask.helpers import locked_cached_property


class Git(object):

    def __init__(self, base_path, payload, git_cmd=None):
        self.base_path = base_path
        self.payload = payload
        self.git_cmd = git_cmd
        if self.git_cmd is None:
            try:
                self.git_cmd = subprocess.check_output(['which', 'git'])
            except subprocess.CalledProcessError:
                raise RuntimeError('git binary not found!')
        self.git_cmd = self.git_cmd.strip()

    @locked_cached_property
    def repo_path(self):
        return os.path.join(self.base_path, self.payload.repository_path)

    def _call_git(self, args):
        try:
            return subprocess.check_output([self.git_cmd] + args,
                                           cwd=self.repo_path,
                                           stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, err:
            raise RuntimeError(str(err))

    def sync_repo(self):
        os.umask(022)
        if not os.path.isdir(os.path.join(self.repo_path, 'objects')):
            if not os.path.isdir(self.repo_path):
                os.makedirs(self.repo_path, 0755)
            return self._call_git(['clone', '--mirror',
                                   self.payload.repository_url, '.'])
        else:
            return self._call_git(['remote', 'update'])
