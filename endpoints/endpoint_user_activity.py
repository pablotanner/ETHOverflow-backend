from models import User, Question, Answer, Vote, Comment, Tag
from datetime import datetime
from uuid import uuid4
from flask import request, jsonify, Blueprint
from sqlalchemy import func
from endpoints.endpoint_users import get_current_user


blueprint_user_activity = Blueprint("user_activity", __name__)
# User activity summary endpoint
@blueprint_user_activity.route('/api/users/<string:email>/activity', methods=['GET'])
def get_user_activity(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Retrieve questions, answers, comments, and votes by the user
    questions = Question.query.filter_by(created_by=email).all()
    answers = Answer.query.filter_by(created_by=email).all()
    comments = Comment.query.filter_by(created_by=email).all()
    votes = Vote.query.filter_by(created_by=email).all()

    return jsonify({
        "questions": [q.question_id for q in questions],
        "answers": [a.answer_id for a in answers],
        "comments": [c.comment_id for c in comments],
        "votes": [v.vote_id for v in votes],
        "reputation": user.reputation,
        "username": user.username,
        "email": user.email,
        "display_name": user.display_name,
        "date_joined": user.date_joined,
        "date_last_login": user.date_last_login,
        "total_questions": user.total_questions,
        "total_answers": user.total_answers,
        "total_comments": user.total_comments,
        "total_votes": user.total_votes
    })
    
@blueprint_user_activity.route('/api/users/activity', methods=['GET'])
def get_current_user_activity():
    email = get_current_user().get_json()['email']
    
    return get_user_activity(email)
