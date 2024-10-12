from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime
from models import User

db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_db()
        app.logger.info("Database tables re-created")


def seed_db():
    # Define some initial users
    users = [
        {
            "username": "jdoe",
            "email": "jdoe@example.com",
            "display_name": "John Doe",
            "date_joined": datetime.datetime.utcnow(),
            "date_last_login": datetime.datetime.utcnow(),
            "reputation": 100,
        },
        {
            "username": "asmith",
            "email": "asmith@example.com",
            "display_name": "Alice Smith",
            "date_joined": datetime.datetime.utcnow(),
            "date_last_login": datetime.datetime.utcnow(),
            "reputation": 150,
        },
        {
            "username": "bwilliams",
            "email": "bwilliams@example.com",
            "display_name": "Bob Williams",
            "date_joined": datetime.datetime.utcnow(),
            "date_last_login": datetime.datetime.utcnow(),
            "reputation": 200,
        },
    ]

    # Insert users into the database
    for user_data in users:
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            display_name=user_data["display_name"],
            date_joined=user_data["date_joined"],
            date_last_login=user_data["date_last_login"],
            reputation=user_data["reputation"],
        )
        db.session.add(user)

    db.session.commit()
