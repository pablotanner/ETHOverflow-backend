from src.database import db
import uuid
import datetime
from sqlalchemy.dialects.postgresql import UUID, ARRAY


class User(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    email = db.Column(db.String, nullable=False)
    display_name = db.Column(db.String, nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_last_login = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    reputation = db.Column(db.Integer, nullable=False, default=0)
    total_questions = db.Column(db.Integer, nullable=False, default=0)
    total_answers = db.Column(db.Integer, nullable=False, default=0)
    total_comments = db.Column(db.Integer, nullable=False, default=0)
    total_votes = db.Column(db.Integer, nullable=False, default=0)


class Question(db.Model):
    __tablename__ = "questions"

    question_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_asked = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_last_edited = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_closed = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.String, db.ForeignKey("users.username"), nullable=False)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(ARRAY(db.Integer), nullable=False)


class Tag(db.Model):
    __tablename__ = "tags"

    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)


class Answer(db.Model):
    __tablename__ = "answers"

    answer_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_answered = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    date_last_edited = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    created_by = db.Column(db.String, db.ForeignKey("users.username"), nullable=False)
    question_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("questions.question_id"), nullable=False
    )
    content = db.Column(db.Text, nullable=False)


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
    created_by = db.Column(db.String, db.ForeignKey("users.username"), nullable=False)
    content = db.Column(db.Text, nullable=False)


class Vote(db.Model):
    __tablename__ = "votes"

    vote_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_voted = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    created_by = db.Column(db.String, db.ForeignKey("users.username"), nullable=False)
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
