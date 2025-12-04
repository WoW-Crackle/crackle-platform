from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# SQLAlchemy ORM 객체 생성 
db = SQLAlchemy()

# Flask-Migrate 객체 생성
migrate = Migrate()