#!venv/bin/python

'''
Creates the server's database in the folder SQLALCHEMY_MIGRATE_REPO, 
as defined in config.py.

To run: 
	./db_create.py

Run this only once, at installation! To update the database after 
schema changes, commit the changes as a migration using db_migrate 
instead.

'''

from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
from app import db
import os.path
db.create_all()
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))