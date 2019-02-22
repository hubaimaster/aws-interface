git pull;
python aws_interface/manage.py makemigrations;
python aws_interface/manage.py migrate;
python aws_interface/manage.py collectstatic --noinput;
python aws_interface/manage.py test
