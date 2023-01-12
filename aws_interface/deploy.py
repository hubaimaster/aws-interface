import subprocess
import os

# pip install awsebcli
if __name__ == '__main__':
    # if not os.path.exists('../secret.tar.enc'):
    #     subprocess.run('./archive_secret.sh')
    subprocess.run('./deploy.sh')
