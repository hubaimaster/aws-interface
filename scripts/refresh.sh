git pull;
source venv/bin/activate;  # venv based virtual environment
python aws_interface/manage.py makemigrations;
python aws_interface/manage.py migrate;
python aws_interface/manage.py collectstatic --noinput;
sudo apachectl restart;
