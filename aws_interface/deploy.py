import settings
import subprocess
import os

if __name__ == '__main__':
    if settings.DEBUG:
        raise BaseException("settings.DEBUG is not False -> Can't run deploy")
    if not os.path.exists('../secret.tar.enc'):
        subprocess.run('./archive_secret.sh')
    subprocess.run('./deploy.sh')
