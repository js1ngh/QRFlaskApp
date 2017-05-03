import os

SECRET_KEY = 'ZmFsbDIwMTdzZWN1cml0eXByb2plY3QK'
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite')

