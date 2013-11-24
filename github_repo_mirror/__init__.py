from flask import Flask, Response, abort, request

from github_repo_mirror.git import Git
from github_repo_mirror.payload import GithubPayload

app = Flask(__name__)
app.config.from_envvar('GITHUB_REPO_MIRROR_SETTINGS', True)

app.config.setdefault('AUTH_USERNAME', 'test')
app.config.setdefault('AUTH_PASSWORD', 'test')
app.config.setdefault('REPOSITORY_ROOT', '/tmp')


def authenticate():
    return Response('Could not verify your access level for that URL.\n'
                    'You have to login with proper credentials\n', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})


@app.route('/', methods=['POST'])
def main():
    if request.authorization is None:
        return authenticate()
    if request.authorization.username != app.config['AUTH_USERNAME'] or \
       request.authorization.password != app.config['AUTH_PASSWORD']:
        return authenticate()
    if 'payload' not in request.form:
        abort(400)
    try:
        payload = GithubPayload(request.form['payload'])
        git = Git(app.config['REPOSITORY_ROOT'], payload)
        git.sync_repo()
        return 'Ok'
    except Exception, err:
        app.logger.error(str(err))
        raise
