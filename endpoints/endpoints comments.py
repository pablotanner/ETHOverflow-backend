from models import User, Question, Answer, Vote, Comment, Tag
from datetime import datetime
from uuid import uuid4
from flask import request, jsonify
import pytz
from sqlalchemy import func



# Define Switzerland timezone
switzerland_tz = pytz.timezone('Europe/Zurich')


# Endpoint to post an answer to a question
@app.route('/api/questions/<string:question_id>/answers/<string:answers_id>/comments', methods=['POST'])
def post_comment(question_id,answers_id):
    data = request.get_json()
    new_comment = Comment(
        comment_id=str(uuid4()),  # Generate unique UUID for the comment ID
        content=data['content'],
        question_id=question_id,
        answer_id=answers_id,
        date_commented=datetime.now(switzerland_tz),  # Automatically set the date when the comment is posted
        date_last_edited=datetime.now(switzerland_tz),  # Initialize with current date and time
        created_by=data['created_by']  # Use created_by instead of user_id as per schema
    )
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({"message": "Comment posted successfully!", "comment_id": new_comment.comment_id}), 201



# Endpoint to get comments for a specific answer
@app.route('/api/questions/<string:question_id>/answers/<string:answer_id>/comments', methods=['GET'])
def get_comments(question_id, answer_id):
    # Fetch all comments for the specified answer ID
    comments = Comment.query.filter_by(question_id=question_id, answer_id=answer_id).all()

    # Prepare a list to hold the answers with their vote counts
    comments_list = []

    current_user = request.args.get('user')  # Assume user identifier passed as query parameter

    # Loop through each answer to get its details and vote count
    for c in comments:
        # Calculate the total vote count
        total_vote_count = db.session.query(func.sum(Vote.vote_type)).filter_by(comment_id=c.comment_id).scalar()
        total_vote_count = total_vote_count if total_vote_count is not None else 0

        # Check if current user has voted on this answer
        user_vote = Vote.query.filter_by(answer_id=a.answer_id, created_by=current_user).first()
        user_vote_type = user_vote.vote_type if user_vote else None

    # Append the comment details and vote count to the comment list
    comments_list.append({
        # "comment_id": c.comment_id,
        "content": c.content,
        "date_commented": c.date_commented,
        "date_last_edited": c.date_last_edited,
        "created_by": c.created_by
        "total_vote_count": total_vote_count,
        "user_vote_type": user_vote_type  # 1 for upvote, -1 for downvote, or None
    })

    return jsonify(comments_list)

# Endpoint to update an existing comment specified by comment_id
@app.route('/api/comments/<string:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    data = request.get_json()
    comment = Comment.query.filter_by(comment_id=comment_id).first()

    if not comment:
        return jsonify({"error": "Comment not found"}), 404

    # Update comment fields based on input
    if 'content' in data:
        comment.content = data['content']
    comment.date_last_edited = datetime.now(switzerland_tz)  # Update with current time

    db.session.commit()
    return jsonify({"message": "Comment updated successfully!"})

# Endpoint to delete an existing comment specified by comment_id
@app.route('/api/comments/<string:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comment = Comment.query.filter_by(comment_id=comment_id).first()

    if not comment:
        return jsonify({"error": "Comment not found"}), 404

    db.session.delete(comment)
    db.session.commit()
    return jsonify({"message": "Comment deleted successfully!"})
