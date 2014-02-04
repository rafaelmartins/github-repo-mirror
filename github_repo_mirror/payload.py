import json
import os
import re

from flask.helpers import locked_cached_property


class GithubPayload(object):

    _re_url = re.compile(r'^https?://github\.com/(?P<username>[^/]+)/'
                         r'(?P<repository_name>[a-zA-Z0-9\.-]+)$')

    def __init__(self, payload):
        self.payload = json.loads(payload)

    def _parse_url(self, url):
        rv = self._re_url.match(url)
        if rv is None:
            raise RuntimeError('Failed to parse url: %s' % url)
        return rv.groupdict()

    @locked_cached_property
    def username(self):
        pieces = self._parse_url(self.repository_url)
        return pieces['username']

    @locked_cached_property
    def repository_name(self):
        pieces = self._parse_url(self.payload['repository']['url'])
        return pieces['repository_name']

    @locked_cached_property
    def repository_path(self):
        return os.path.join(self.username, self.repository_name) + '.git'

    @locked_cached_property
    def repository_url(self):
        return self.payload['repository']['url']

    @locked_cached_property
    def repository_git_url(self):
        return 'git@github.com:%s/%s.git' % (self.username,
                                             self.repository_name)

    @locked_cached_property
    def private(self):
        return self.payload['repository']['private']

    @locked_cached_property
    def repository_remote_url(self):
        if self.private:
            return self.repository_git_url
        return self.repository_url
