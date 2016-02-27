import os

# Database

basedir = os.path.abspath(os.path.dirname(__file__))
# database file path
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
# store the SQLAlchemy-migrate data files
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
