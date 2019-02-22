python aws_interface/manage.py makemigrations
touch aws_interface/db.sqlite3
sudo chown www-data:ubuntu aws_interface/db.sqlite3
python aws_interface/manage.py migrate
python aws_interface/manage.py collectstatic --noinput;
