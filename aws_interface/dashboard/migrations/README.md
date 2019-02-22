## Managing Migrations
Refrain from uploading migrations to the server, for now.

Migrations should be part of the source code of a Django project.
They should not be made via `makemigrations` on every deployment.
However during heavy development, we are currently not considering
this, due to the overhead of managing the continuity of migrations.


### CAUTION
Note that __init__.py in this folder is required for Django to recognize that the `dashboard` app uses migrations.
