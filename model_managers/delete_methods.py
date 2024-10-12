from models import Vote, Comment, Answer, Question, Tag
from flask import request, jsonify
from src import db


def delete_vote(vote_id):
    vote = Vote.query.filter_by(vote_id=vote_id).first()
    db.session.delete(vote)
    db.session.commit()


def delete_comment(comment_id):
    comment = Comment.query.filter_by(comment_id=comment_id).first()
    votes = Vote.query.filter_by(comment_id=comment_id).all()
    for vote in votes:
        delete_vote(vote.vote_id)
    db.session.delete(comment)
    db.session.commit()


def delete_answer(answer_id):
    answer = Answer.query.filter_by(answer_id=answer_id).first()
    comments = Comment.query.filter_by(answer_id=answer_id).all()
    votes = Vote.query.filter_by(answer_id=answer_id).all()
    for comment in comments:
        delete_comment(comment.comment_id)
    for vote in votes:
        delete_vote(vote.vote_id)
    db.session.delete(answer)
    db.session.commit()


def delete_question(question_id):
    question = Question.query.filter_by(question_id=question_id).first()
    answers = Answer.query.filter_by(question_id=question_id).all()
    comments = Comment.query.filter_by(question_id=question_id).all()
    votes = Vote.query.filter_by(question_id=question_id).all()
    tags = question.tags
    for tag in tags:
        tag.questions = tag.questions.remove(question_id)
    for answer in answers:
        delete_answer(answer.answer_id)
    for comment in comments:
        delete_comment(comment.comment_id)
    for vote in votes:
        delete_vote(vote.vote_id)
    db.session.delete(question)
    db.session.commit()
