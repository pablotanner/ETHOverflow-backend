from models import User, Question, Answer, Vote, Comment, Tag
from datetime import datetime
from uuid import uuid4
from flask import request, jsonify, Blueprint
from sqlalchemy import func
from src import db
from endpoints import endpoint_votes, endpoint_users
from model_managers import delete_methods

blueprint_answers = Blueprint("answers", __name__)

# Endpoint to post an answer to a question
@blueprint_answers.route('/api/questions/<string:question_id>/answers', methods=['POST'])
def post_answer(question_id):
    data = request.get_json()
    new_answer = Answer(
        answer_id=str(uuid4()),  # Generate unique UUID for the answer ID
        content=data['content'],
        question_id=question_id,
        date_answered=datetime.now(),  # Automatically set the date when the answer is posted
        date_last_edited=datetime.now(),  # Initialize with current date and time
        created_by=endpoint_users.get_current_user().get_json()['email']  # Use created_by instead of user_id as per schema
    )

    if not data['content']:
        return jsonify({'error': 'Content cannot be empty'}), 400

    question = Question.query.filter_by(question_id=question_id).first()
    question.date_last_edited = datetime.now()

    db.session.add(new_answer)
    db.session.commit()
    return jsonify({"message": "Answer posted successfully!", "answer_id": new_answer.answer_id}), 201


# Adjusted get_answers to include total vote count and user vote
@blueprint_answers.route('/api/questions/<string:question_id>/answers', methods=['GET'])
def get_answers(question_id):
    answers = Answer.query.filter_by(question_id=question_id).all()
    answers_list = []

    current_user = request.args.get('user')  # Assume user identifier passed as query parameter

    for a in answers:
        # Calculate the total vote count
        total_vote_count = endpoint_votes.get_answer_vote_count(a.answer_id).get_json()['total_vote_count']

        # Check if current user has voted on this answer
        user_vote = Vote.query.filter_by(answer_id=a.answer_id, created_by=current_user).first()
        user_vote_type = user_vote.vote_type if user_vote else None

        answers_list.append({
            "answer_id": a.answer_id,
            "content": a.content,
            "date_answered": a.date_answered,
            "date_last_edited": a.date_last_edited,
            "created_by": a.created_by,
            "total_vote_count": total_vote_count,
            "user_vote_type": user_vote_type,  # 1 for upvote, -1 for downvote, or None
            "accepted": a.accepted
        })

    return jsonify(answers_list)


# Endpoint to update an existing answer specified by answer_id
@blueprint_answers.route('/api/answers/<string:answer_id>', methods=['PUT'])
def update_answer(answer_id):
    data = request.get_json()
    answer = Answer.query.filter_by(answer_id=answer_id).first()

    if not answer:
        return jsonify({"error": "Answer not found"}), 404

    # Update answer fields based on input
    if 'content' in data:
        answer.content = data['content']
    answer.date_last_edited = datetime.now()  # Update with current time

    question = Question.query.filter_by(question_id=answer.question_id).first()
    question.date_last_edited = datetime.now()

    db.session.commit()
    return jsonify({"message": "Answer updated successfully!"})


# Endpoint to delete an existing answer specified by answer_id
@blueprint_answers.route('/api/answers/<string:answer_id>', methods=['DELETE'])
def delete_answer(answer_id):
    answer = Answer.query.filter_by(answer_id=answer_id).first()

    if not answer:
        return jsonify({"error": "Answer not found"}), 404

    if endpoint_users.get_current_user().get_json()['email'] == answer.created_by:
        delete_methods.delete_answer(answer_id)
        return jsonify({"message": "Answer deleted successfully!"})
    else:
        return jsonify({"error": "User does not have permission to delete answer!"}), 403
