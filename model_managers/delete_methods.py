from models import Vote, Comment, Answer, Question, Tag
from flask import request, jsonify
from src import db


def delete_vote(vote_id):
    vote = Vote.query().filterby(vote_id=vote_id).first()
    db.session.delete(vote)
    db.session.commit()


def delete_comment(comment_id):
    comment = Comment.query().filterby(comment_id=comment_id).first()
    votes = Vote.query().filterby(comment_id=comment_id).all()
    for vote in votes:
        delete_vote(vote.vote_id)
    db.session.delete(comment)
    db.session.commit()


def delete_answer(answer_id):
    answer = Answer.query().filterby(answer_id=answer_id).fist()
    comments = Comment.query().filterby(answer_id=answer_id).all()
    votes = Votes.query.filterby(answer_id=answer_id).all()
    for comment in comments:
        delete_comment(comment.comment_id)
    for vote in votes:
        delete_vote(vote.vote_id)
    db.session.delete(answer)
    db.session.commit()


def delete_question(question_id):
    question = Question.query().filterby(question_id=question_id).fist()
    answers = Answer.query().filterby(question_id=question_id).all()
    comments = Comment.query().filterby(question_id=question_id).all()
    votes = Votes.query.filterby(question_id=question_id).all()
    tags = question.tags
    for tag in tags:
        tag.questions = tag.questions.remove(question_id)
        db.session.commit()
    for answer in answers:
        delete_answer(answer.answer_id)
    for comment in comments:
        delete_comment(comment.comment_id)
    for vote in votes:
        delete_vote(vote.vote_id)
    db.session.delete(question)
    db.session.commit()
