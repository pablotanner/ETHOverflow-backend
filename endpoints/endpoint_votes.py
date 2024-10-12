from models import User, Question, Answer, Vote, Comment, Tag
from datetime import datetime
from uuid import uuid4
from flask import request, jsonify, Blueprint
from src import db
from endpoints.endpoint_users import get_current_user

blueprint_votes = Blueprint("votes", __name__)

# Endpoint to add or update a vote on an answer
@blueprint_votes.route('/api/answers/<string:answer_id>/vote', methods=['POST'])
def vote_on_answer(answer_id):
    data = request.get_json()
    vote_type = data.get('vote_type')  # Should be 1 (upvote) or -1 (downvote)
    created_by = get_current_user().get_json()['email']  # User who cast the vote

    # Check if a vote by this user on this answer already exists
    vote = Vote.query.filter_by(answer_id=answer_id, created_by=created_by).first()

    if vote:
        # If vote exists, update the vote type
        vote.vote_type = vote_type
        vote.date_voted = datetime.now()
    else:
        # If no vote exists, create a new vote
        new_vote = Vote(
            vote_id=str(uuid4()),
            answer_id=answer_id,
            vote_type=vote_type,
            created_by=created_by,
            date_voted=datetime.now()
        )
        db.session.add(new_vote)

    db.session.commit()
    return jsonify({"message": "Vote recorded successfully!"}), 201

# Endpoint to add or update a vote on a comment
@blueprint_votes.route('/api/comments/<string:comment_id>/vote', methods=['POST'])
def vote_on_comment(comment_id):
    data = request.get_json()
    vote_type = data.get('vote_type')  # Should be 1 (upvote) or -1 (downvote)
    created_by = get_current_user().get_json()['email']  # User who cast the vote

    # Check if a vote by this user on this answer already exists
    vote = Vote.query.filter_by(comment_id=comment_id, created_by=created_by).first()

    if vote:
        # If vote exists, update the vote type
        vote.vote_type = vote_type
        vote.date_voted = datetime.now()
    else:
        # If no vote exists, create a new vote
        new_vote = Vote(
            vote_id=str(uuid4()),
            comment_id=comment_id,
            vote_type=vote_type,
            created_by=created_by,
            date_voted=datetime.now()
        )
        db.session.add(new_vote)

    db.session.commit()
    return jsonify({"message": "Vote recorded successfully!"}), 201

# Endpoint to add or update a vote on a question
@blueprint_votes.route('/api/questions/<string:question_id>/vote', methods=['POST'])
def vote_on_question(question_id):
    data = request.get_json()
    vote_type = data.get('vote_type')  # Should be 1 (upvote) or -1 (downvote)
    created_by = get_current_user().get_json()['email']  # User who cast the vote

    # Check if a vote by this user on this answer already exists
    vote = Vote.query.filter_by(question_id=question_id, created_by=created_by).first()

    if vote:
        # If vote exists, update the vote type
        vote.vote_type = vote_type
        vote.date_voted = datetime.now()
    else:
        # If no vote exists, create a new vote
        new_vote = Vote(
            vote_id=str(uuid4()),
            question_id=question_id,
            vote_type=vote_type,
            created_by=created_by,
            date_voted=datetime.now()
        )
        db.session.add(new_vote)

    db.session.commit()
    return jsonify({"message": "Vote recorded successfully!"}), 201

# Endpoint to get the total vote count for a question
@blueprint_votes.route('/api/questions/<string:question_id>/votes', methods=['GET'])
def get_question_vote_count(question_id):
    total_vote_count = db.session.query(db.func.sum(Vote.vote_type)).filter_by(question_id=question_id).scalar()
    total_vote_count = total_vote_count if total_vote_count is not None else 0

    return jsonify({"total_vote_count": total_vote_count})

# Endpoint to get the total vote count for an answer
@blueprint_votes.route('/api/answers/<string:answer_id>/votes', methods=['GET'])
def get_answer_vote_count(answer_id):
    total_vote_count = db.session.query(db.func.sum(Vote.vote_type)).filter_by(answer_id=answer_id).scalar()
    total_vote_count = total_vote_count if total_vote_count is not None else 0

    return jsonify({"total_vote_count": total_vote_count})

# Endpoint to get the total vote count for a comment
@blueprint_votes.route('/api/comments/<string:comment_id>/votes', methods=['GET'])
def get_comment_vote_count(comment_id):
    total_vote_count = db.session.query(db.func.sum(Vote.vote_type)).filter_by(comment_id=comment_id).scalar()
    total_vote_count = total_vote_count if total_vote_count is not None else 0

    return jsonify({"total_vote_count": total_vote_count})


# Endpoint to get the total vote count for a user
@blueprint_votes.route('/api/users/<string:username>/votes', methods=['GET'])
def get_user_vote_count(username):
    
    reputation = 0
    
    # +10 for each voted up question
    # -2 for answer voted down
    
    questions = Question.query.filter_by(created_by=username).all()
    for q in questions:
        positive_votes = Vote.query.filter_by(question_id=q.question_id, vote_type=1).count()
        negative_votes = Vote.query.filter_by(question_id=q.question_id, vote_type=-1).count()
        negative_votes = negative_votes if negative_votes is not None else 0
        reputation += positive_votes * 10 - negative_votes * 2
    
    # +10 for each voted up answer
    # -2 for question voted down
    
    answers = Answer.query.filter_by(created_by=username).all()
    for a in answers:
        positive_votes = Vote.query.filter_by(answer_id=a.answer_id, vote_type=1).count()
        negative_votes = Vote.query.filter_by(answer_id=a.answer_id, vote_type=-1).count()
        reputation += positive_votes * 10 - negative_votes * 2
    
    # +15 for each accepted answer
    
    accepted_answers = Answer.query.filter_by(created_by=username, accepted=True).count()
    reputation += accepted_answers * 15
    
    # -1 for downvoting an answer
    
    downvoted_answers = Vote.query.filter_by(created_by=username, vote_type=-1).count()
    reputation -= downvoted_answers
    
    return jsonify({"total_vote_count": reputation})    
