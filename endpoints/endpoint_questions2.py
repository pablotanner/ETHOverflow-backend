from models import User, Question, Answer, Vote, Comment, Tag
from datetime import datetime
from uuid import uuid4
from flask import request, jsonify, Blueprint
from src import db

blueprint_questions = Blueprint("questions", __name__)

# Endpoint to get questions or a specific question by question_id
@blueprint_questions.route('/api/questions/<string:question_id>', methods=['GET'])
def get_questions():

    # Base query
    query = Question.query
    current_user = request.args.get('user')  # Assume user identifier passed as query parameter


    # Get query parameters
    limit = request.args.get('limit', default=10, type=int)
    question_id = request.args.get('question_id', type=str)  # UUID is a string
    if question_id:
        query = query.filter_by(question_id=question_id)
    else:
        return jsonify({"error": "Question not found"}), 404

    comments = Comment.query.filter_by(question_id=question_id).all()
    comments_of_questions_list = []

    # Loop through each answer to get its details and vote count
    for c in comments:
        # Calculate the total vote count
        total_vote_count = db.session.query(func.sum(Vote.vote_type)).filter_by(comment_id=c.comment_id).scalar()
        total_vote_count = total_vote_count if total_vote_count is not None else 0

        # Check if current user has voted on this answer
        user_vote = Vote.query.filter_by(answer_id=c.answer_id, created_by=current_user).first()
        user_vote_type = user_vote.vote_type if user_vote else None

        # Append the comment details and vote count to the comment list
        comments_of_questions_list.append({
            "comment_id": c.comment_id,
            "content": c.content,
            "date_commented": c.date_commented,
            "date_last_edited": c.date_last_edited,
            "created_by": c.created_by,
            "total_vote_count": total_vote_count,
            "user_vote_type": user_vote_type  # 1 for upvote, -1 for downvote, or None
        })

    answers = Answer.query.filter_by(question_id=question_id).all()

    answers_list = []


    for a in answers:
        # Calculate the total vote count
        total_vote_count = db.session.query(func.sum(Vote.vote_type)).filter_by(answer_id=a.answer_id).scalar()
        total_vote_count = total_vote_count if total_vote_count is not None else 0

        # Check if current user has voted on this answer
        user_vote = Vote.query.filter_by(answer_id=a.answer_id).first()
        user_vote_type = user_vote.vote_type if user_vote else None

        comments = Comment.query.filter_by(question_id=question_id, answer_id=answer_id).all()
        comments_list = []


        # Loop through each answer to get its details and vote count
        for c in comments:
            # Calculate the total vote count
            total_vote_count = db.session.query(func.sum(Vote.vote_type)).filter_by(comment_id=c.comment_id).scalar()
            total_vote_count = total_vote_count if total_vote_count is not None else 0

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

        answers_list.append({
            "answer_id": a.answer_id,
            "content": a.content,
            "date_answered": a.date_answered,
            "date_last_edited": a.date_last_edited,
            "created_by": a.created_by,
            "total_vote_count": total_vote_count,
            "user_vote_type": user_vote_type  # 1 for upvote, -1 for downvote, or None
            "comments_list": comments_list
        })

    # Prepare a list to hold the answers with their vote counts

    # Filter by specific question ID from database
    if question_id:
        query = query.filter_by(question_id=question_id)

    # Limit the number of questions returned
    questions = query.limit(limit).all()

    # Convert results to JSON

    # Convert results to JSON
    questions_list = [{
        "id": q.question_id,
        "title": q.title,
        "content": q.content,
        "date_asked": q.date_asked,
        "date_last_edited": q.date_last_edited,
        "date_closed": q.date_closed,
        "created_by": q.created_by,
        "reputation": q.reputation,
        "email": q.email,
        "tags": [Tag.query.get(tag).name for tag in q.tags]
        "comments_of_questions_list": comments_of_questions_list
        "answers_list": answers_list
    } for q in questions]

    return jsonify(questions_list)
