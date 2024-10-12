from models import User, Question, Answer, Vote, Comment, Tag
from datetime import datetime
from uuid import uuid4
from flask import request, jsonify, Blueprint
from sqlalchemy import func
from src import db
from endpoints import endpoint_votes, endpoint_users

blueprint_comments = Blueprint("comments", __name__)


# Endpoint to post an answer to a question
@blueprint_comments.route('/api/questions/<string:question_id>/answers/<string:answers_id>/comments', methods=['POST'])
def post_comment(question_id, answers_id):
    data = request.get_json()
    new_comment = Comment(
        comment_id=str(uuid4()),  # Generate unique UUID for the comment ID
        content=data['content'],
        question_id=question_id,
        answer_id=answers_id,
        date_commented=datetime.now(),  # Automatically set the date when the comment is posted
        date_last_edited=datetime.now(),  # Initialize with current date and time
        created_by=data['created_by']  # Use created_by instead of user_id as per schema
    )
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({"message": "Comment posted successfully!", "comment_id": new_comment.comment_id}), 201


# Endpoint to get comments for a specific answer
@blueprint_comments.route('/api/questions/<string:question_id>/answers/<string:answer_id>/comments', methods=['GET'])
def get_comments(question_id, answer_id):
    # Fetch all comments for the specified answer ID
    comments = Comment.query.filter_by(question_id=question_id, answer_id=answer_id).all()

    # Prepare a list to hold the answers with their vote counts
    comments_list = []

    current_user = request.args.get('user')  # Assume user identifier passed as query parameter

    # Loop through each answer to get its details and vote count
    for c in comments:
        # Calculate the total vote count
        total_vote_count = endpoint_votes.get_comment_vote_count(c.comment_id).get_json()['total_vote_count']

        # Check if current user has voted on this answer
        user_vote = Vote.query.filter_by(answer_id=c.answer_id, created_by=current_user).first()
        user_vote_type = user_vote.vote_type if user_vote else None

    # Append the comment details and vote count to the comment list
    comments_list.append({
        "comment_id": c.comment_id,
        "content": c.content,
        "date_commented": c.date_commented,
        "date_last_edited": c.date_last_edited,
        "created_by": c.created_by,
        "total_vote_count": total_vote_count,
        "user_vote_type": user_vote_type  # 1 for upvote, -1 for downvote, or None
    })

    return jsonify(comments_list)


# Endpoint to update an existing comment specified by comment_id
@blueprint_comments.route('/api/comments/<string:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    data = request.get_json()
    comment = Comment.query.filter_by(comment_id=comment_id).first()

    if not comment:
        return jsonify({"error": "Comment not found"}), 404

    # Update comment fields based on input
    if 'content' in data:
        comment.content = data['content']
    comment.date_last_edited = datetime.now()  # Update with current time

    db.session.commit()
    return jsonify({"message": "Comment updated successfully!"})


# Endpoint to delete an existing comment specified by comment_id
@blueprint_comments.route('/api/comments/<string:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comment = Comment.query.filter_by(comment_id=comment_id).first()

    if not comment:
        return jsonify({"error": "Comment not found"}), 404

    if endpoint_users.get_current_user().get_json()['email'] == comment.created_by:

        db.session.delete(comment)
        db.session.commit()
        return jsonify({"message": "Comment deleted successfully!"})

    else:
        return jsonify({"error": "User does not have permission to delete answer!"}), 403
