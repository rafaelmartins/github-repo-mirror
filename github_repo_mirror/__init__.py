from flask import Flask, Response, abort, request

from github_repo_mirror.git import Git
from github_repo_mirror.payload import GithubPayload
from github_repo_mirror.utils import request_allowed

import traceback

app = Flask(__name__)
app.config.from_envvar('GITHUB_REPO_MIRROR_SETTINGS', True)

app.config.setdefault('GITHUB_HOOK_USERNAME', 'test')
app.config.setdefault('GITHUB_HOOK_PASSWORD', 'test')
app.config.setdefault('GITHUB_AUTH_USERNAME', None)
app.config.setdefault('GITHUB_AUTH_PASSWORD', None)
app.config.setdefault('GITHUB_REPO_ROOT', '/tmp')
app.config.setdefault('GITHUB_PUBLIC_NETWORK', '192.30.252.0/22')


def authenticate():
    return Response('Could not verify your access level for that URL.\n'
                    'You have to login with proper credentials\n', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})


@app.route('/')
def home():
    return 'We are live!!!\n'


@app.route('/github', methods=['POST'])
def github():
    if not request_allowed(request.remote_addr,
                           app.config['GITHUB_PUBLIC_NETWORK'],
                           app.debug):
        abort(403)
    if request.authorization is None:
        return authenticate()
    if request.authorization.username != app.config['GITHUB_HOOK_USERNAME'] or \
       request.authorization.password != app.config['GITHUB_HOOK_PASSWORD']:
        return authenticate()
    if 'payload' not in request.form:
        abort(400)
    try:
        payload = GithubPayload(request.form['payload'])
        git = Git(app.config['GITHUB_REPO_ROOT'], payload)
        app.logger.info('Syncing repo: %s\n%s' %
                        (payload.repository_path,
                         git.sync_repo(app.config['GITHUB_AUTH_USERNAME'],
                                       app.config['GITHUB_AUTH_PASSWORD'])))
        return 'Ok\n'
    except Exception as err:
        app.logger.error('%s: %s\n%s' % (err.__class__.__name__, str(err),
                                         traceback.format_exc()))
        return 'Fail\n', 500
