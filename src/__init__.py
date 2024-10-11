from flask import Flask
from config import Config
from src.database import init_db, db
from models import User, Question, Tag, Answer, Comment, Vote
import logging


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database and migration
    init_db(app)

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    app.logger.info("Application initialized")

    # @app.before_first_request
    # def setup_database():
    # 	 db.drop_all()
    # 	 db.create_all()
    # 	 app.logger.info("Database tables re-created")
    with app.app_context():
        db.drop_all()
        db.create_all()
        app.logger.info("Database tables re-created")

    return app
