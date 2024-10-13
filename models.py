from src.database import db
import uuid
import datetime
from sqlalchemy.dialects.postgresql import UUID, ARRAY, TSVECTOR


class User(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    display_name = db.Column(db.String, nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_last_login = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Question(db.Model):
    __tablename__ = "questions"

    question_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_asked = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_last_edited = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_closed = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.String, db.ForeignKey("users.email"), nullable=False)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(ARRAY(db.String), nullable=False)
    correct_answer_id = db.Column(UUID(as_uuid=True), nullable=True, default=None)
    embedding =db.Column(ARRAY(db.Float))
    search_vector = db.Column(TSVECTOR)  # Store the search vector

    __table_args__ = (
        db.Index('ix_question_search', 'search_vector', postgresql_using='gin'),
    )


class Tag(db.Model):
    __tablename__ = "tags"

    name = db.Column(db.String, primary_key=True)
    questions = db.Column(ARRAY(UUID(as_uuid=True)))


class Answer(db.Model):
    __tablename__ = "answers"

    answer_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_answered = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_last_edited = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    created_by = db.Column(db.String, db.ForeignKey("users.email"), nullable=False)
    question_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("questions.question_id"), nullable=False
    )
    content = db.Column(db.Text, nullable=False)
    accepted = db.Column(db.Boolean, default=False)


class Comment(db.Model):
    __tablename__ = "comments"

    comment_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_commented = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_last_edited = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    question_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("questions.question_id"), nullable=True
    )
    answer_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("answers.answer_id"), nullable=True
    )
    created_by = db.Column(db.String, db.ForeignKey("users.email"), nullable=False)
    content = db.Column(db.Text, nullable=False)


class Vote(db.Model):
    __tablename__ = "votes"

    vote_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_voted = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    created_by = db.Column(db.String, db.ForeignKey("users.email"), nullable=False)
    question_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("questions.question_id"), nullable=True
    )
    answer_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("answers.answer_id"), nullable=True
    )
    comment_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("comments.comment_id"), nullable=True
    )
    vote_type = db.Column(db.Integer, nullable=False)
