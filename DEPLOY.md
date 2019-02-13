# Deploy On Apache2

### Install Dev Packages

```
sudo apt install apache2
sudo apt install python3.6-dev
sudo apt install apache2-dev
```

### Install Pip Packages

```
# activate virtual environment
pip install -r requirements.txt
```

### Check MOD WSGI Path

```
mod_wsgi-express module-config
```
```
# OUTPUT:
LoadModule wsgi_module "/home/ubuntu/aws-interface/venv/lib/python3.6/site-packages/mod_wsgi/server/mod_wsgi-py36.cpython-36m-x86_64-linux-gnu.so"
WSGIPythonHome "/home/ubuntu/aws-interface/venv"
```

### Configure Apache2

```apache2
<VirtualHost *:80>
	ServerName aws-interface.com
	ServerAlias www.aws-interface.com
	ServerAdmin support@aws-interface.com

	# Serving static files
	Alias /robots.txt /var/www/aws-interface.com/static/robots.txt
	Alias /favicon.ico /var/www/aws-interface.com/static/favicon.ico

	Alias /static/ /var/www/aws-interface.com/static/

	<Directory /var/www/aws-interface.com/static>
	Require all granted
	</Directory>

	<Directory /home/ubuntu/aws-interface/aws_interface>
	<Files wsgi.py>
	Require all granted
	</Files>
	</Directory>

	LoadModule wsgi_module "/home/ubuntu/aws-interface/venv/lib/python3.6/site-packages/mod_wsgi/server/mod_wsgi-py36.cpython-36m-x86_64-linux-gnu.so"
	WSGIDaemonProcess aws-interface.com processes=2 threads=15 display-name=%{GROUP} python-path=/home/ubuntu/aws-interface/aws_interface python-home=/home/ubuntu/aws-interface/venv
	WSGIProcessGroup aws-interface.com

	WSGIScriptAlias / /home/ubuntu/aws-interface/aws_interface/wsgi.py
</VirtualHost>
```

Mind the arguments `python-path`, `python-home` and the `WSGIScriptAlias` directive.

### Permissions

Let Apache access the db (should use MySQL later)

```bash
sudo chown www-data db.sqlite3
sudo chmod g+w db.sqlite3  # for pythoh manage.py migrate
```

### Static Files

Create static files folder w/ permissions

```
sudo mkdir -p /var/www/aws-interface/
sudo chown `whoami` /var/www/aws-interface/
```

### Collect Static!

```
python manage.py collectstatic
```
