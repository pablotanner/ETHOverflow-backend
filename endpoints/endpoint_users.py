from models import User, Question, Answer, Vote, Comment, Tag
from datetime import datetime
from uuid import uuid4
from flask import request, jsonify, Blueprint
from src import db

def get_user_vote_count(username):
    total_vote_count = db.session.query(db.func.sum(Vote.vote_type)).filter_by(created_by=username).scalar()
    total_vote_count = total_vote_count if total_vote_count is not None else 0

    return jsonify({"total_vote_count": total_vote_count})


blueprint_users = Blueprint("users", __name__)

# Endpoint to get user(s) specified by username, email and/or limit
@blueprint_users.route('/api/users', methods=['GET'])
def get_users():
    # Get query parameters
    limit = request.args.get('limit', default=10, type=int)
    username = request.args.get('username', type=str)
    email = request.args.get('email', type=str)

    # Base query
    query = User.query

    # Filter by specific username from database
    if username:
        query = query.filter_by(username=username)

    if email:
        query = query.filter_by(email=email)

    # Limit the number of questions returned
    users = query.limit(limit).all()

    # Convert results to JSON
    users_list = [{
        "username": q.username,
        "email": q.email,
        "display_name": q.display_name,
        "date_joined": q.date_joined,
        "date_last_login": q.date_last_login,
        "reputation": get_user_vote_count(q.email).get_json()['total_vote_count'],
    } for q in users]

    return jsonify(users_list)


# Endpoint to create a new user
# @blueprint_users.route('/api/users', methods=['POST'])
# def create_user():
#     data = request.get_json()
#     new_user = User(
#         username=data['username'],
#         email=data['email'],
#         display_name=data['display_name'],
#         date_joined=datetime.now(),  # Automatically set the join date
#         date_last_login=datetime.now(),  # Set last login to current time on account creation
#         reputation=0,  # Start with default reputation
#         total_questions=0,
#         total_answers=0,
#         total_comments=0,
#         total_votes=0
#     )
#     db.session.add(new_user)
#     db.session.commit()
#     return jsonify({"message": "User created successfully!", "username": new_user.username}), 201


# Endpoint to update an existing user specified by username
@blueprint_users.route('/api/users/<string:username>', methods=['PUT'])
def update_user(username):
    data = request.get_json()
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Update user fields based on input
    if 'email' in data:
        user.email = data['email']
    if 'display_name' in data:
        user.display_name = data['display_name']
    if 'reputation' in data:
        user.reputation = data['reputation']
    if 'date_last_login' in data:
        user.date_last_login = datetime.now()  # Update last login time

    db.session.commit()
    return jsonify({"message": "User updated successfully!"})


# Endpoint to delete an existing user specified by username
@blueprint_users.route('/api/users/<string:username>', methods=['DELETE'])
def delete_user(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully!"})

@blueprint_users.route('/api/users/current_user', methods=['GET'])
def get_current_user():
    user = User.query.filter_by(email=request.headers['X-authentik-email']).first()
    if not user:
        user = User(
            username=request.headers['X-authentik-username'],
            email=request.headers['X-authentik-email'],
            display_name=request.headers['X-authentik-name'],
            date_joined=datetime.now(),  # Automatically set the join date
            date_last_login=datetime.now(),  # Set last login to current time on account creation
        )
        try:
            db.session.add(user)
            db.session.commit()
        except:
            pass
        
    user_json = {
        "username": user.username,
        "email": user.email,
        "display_name": user.display_name,
        "date_joined": user.date_joined,
        "date_last_login": user.date_last_login,
        "reputation": get_user_vote_count(user.email).get_json()['total_vote_count'],
    }
    return jsonify(user_json)