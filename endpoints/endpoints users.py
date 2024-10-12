from models import User, Question, Answer, Vote, Comment, Tag
from datetime import datetime
from uuid import uuid4
from flask import request, jsonify
import pytz

# Define Switzerland timezone
switzerland_tz = pytz.timezone('Europe/Zurich')



# Endpoint to get user(s) specified by username or limit
@app.route('/users', methods=['GET'])
def get_users():
    # Get query parameters
    limit = request.args.get('limit', default=10, type=int)
    username = request.args.get('username', type=str)

    # Base query
    query = User.query

    # Filter by specific username from database
    if username:
        query = query.filter_by(username=username)

    # Limit the number of questions returned
    users = query.limit(limit).all()

    # Convert results to JSON
    users_list = [{
        "username": q.username,
        "email": q.email,
        "display_name": q.display_name,
        "date_joined": q.date_joined,
        "date_last_login": q.date_last_login,
        "reputation": q.reputation,
        "total_questions": q.total_questions,
        "total_answers": q.total_answers,
        "total_comments": q.total_comments,
        "total_votes": q.total_votes,
    } for q in users]

    return jsonify(users_list)


# Endpoint to create a new user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(
        username=data['username'],
        email=data['email'],
        display_name=data['display_name'],
        date_joined=datetime.now(switzerland_tz),  # Automatically set the join date
        date_last_login=datetime.now(switzerland_tz),  # Set last login to current time on account creation
        reputation=0,  # Start with default reputation
        total_questions=0,
        total_answers=0,
        total_comments=0,
        total_votes=0
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully!", "username": new_user.username}), 201


# Endpoint to update an existing user specified by username
@app.route('/users/<string:username>', methods=['PUT'])
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
        user.date_last_login = datetime.now(switzerland_tz)  # Update last login time

    db.session.commit()
    return jsonify({"message": "User updated successfully!"})


# Endpoint to delete an existing user specified by username
@app.route('/users/<string:username>', methods=['DELETE'])
def delete_user(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully!"})
