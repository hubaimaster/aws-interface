import settings
import subprocess

if __name__ == '__main__':
    if settings.DEBUG:
        raise BaseException("settings.DEBUG is not False -> Can't run deploy")

    subprocess.run('./pre_deploy.sh')
    subprocess.run('eb deploy aws-interface-prod')
