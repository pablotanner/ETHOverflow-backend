from models import User, Question, Answer, Vote, Comment, Tag
from datetime import datetime
from uuid import uuid4
from flask import request, jsonify, Blueprint
from sqlalchemy import func


blueprint_user_activity = Blueprint("user_activity", __name__)
# User activity summary endpoint
@blueprint_user_activity.route('/api/users/<string:username>/activity', methods=['GET'])
def get_user_activity(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Retrieve questions, answers, comments, and votes by the user
    questions = Question.query.filter_by(created_by=username).all()
    answers = Answer.query.filter_by(created_by=username).all()
    comments = Comment.query.filter_by(created_by=username).all()
    votes = Vote.query.filter_by(created_by=username).all()

    return jsonify({
        "questions": [q.question_id for q in questions],
        "answers": [a.answer_id for a in answers],
        "comments": [c.comment_id for c in comments],
        "votes": [v.vote_id for v in votes],
        "reputation": user.reputation
    })
