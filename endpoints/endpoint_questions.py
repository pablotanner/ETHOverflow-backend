from models import User, Question, Answer, Vote, Comment, Tag
from datetime import datetime
from uuid import uuid4
from flask import request, jsonify, Blueprint
from src import db
from endpoints import endpoint_users

blueprint_questions = Blueprint("questions", __name__)


# Endpoint to get questions or a specific question by question_id
@blueprint_questions.route('/api/questions/<string:question_id>', methods=['GET'])
def get_question(question_id):

    # Base query
    query = Question.query
    current_user = endpoint_users.get_current_user().get_json()['email']  # Assume user identifier passed as query parameter

    query = query.filter_by(question_id=question_id).first()
    
    if not query:
        return jsonify({"error": "Question not found"}), 404

    comments = Comment.query.filter_by(question_id=question_id).all()
    comments_of_questions_list = []

    # Loop through each answer to get its details and vote count
    for c in comments:
        # Calculate the total vote count
        total_vote_count = db.session.query(db.func.sum(Vote.vote_type)).filter_by(comment_id=c.comment_id).scalar()
        total_vote_count = total_vote_count if total_vote_count is not None else 0

        # Check if current user has voted on this answer
        user_vote = Vote.query.filter_by(answer_id=c.answer_id, created_by=current_user).first()
        user_vote_type = user_vote.vote_type if user_vote else None
        
        creator = User.query.filter_by(email=c.created_by).first()

        # Append the comment details and vote count to the comment list
        comments_of_questions_list.append({
            "comment_id": c.comment_id,
            "content": c.content,
            "date_commented": c.date_commented,
            "date_last_edited": c.date_last_edited,
            "created_by": c.created_by,
            "total_vote_count": total_vote_count,
            "user_vote_type": user_vote_type,  # 1 for upvote, -1 for downvote, or None
            "creator": {
                "email": creator.email,
                "username": creator.username,
                "display_name": creator.display_name,
                "reputation": creator.reputation,
                "date_joined": creator.date_joined,
                "date_last_login": creator.date_last_login,
                "total_questions": creator.total_questions,
                "total_answers": creator.total_answers,
                "total_comments": creator.total_comments,
                "total_votes": creator.total_votes
            },
                
        })

    answers = Answer.query.filter_by(question_id=question_id).all()

    answers_list = []

    for a in answers:
        # Calculate the total vote count
        total_vote_count = db.session.query(db.func.sum(Vote.vote_type)).filter_by(answer_id=a.answer_id).scalar()
        total_vote_count = total_vote_count if total_vote_count is not None else 0

        # Check if current user has voted on this answer
        user_vote = Vote.query.filter_by(answer_id=a.answer_id).first()
        user_vote_type = user_vote.vote_type if user_vote else None

        comments = Comment.query.filter_by(question_id=question_id, answer_id=a.answer_id).all()
        comments_list = []

        # Loop through each answer to get its details and vote count
        for c in comments:
            # Calculate the total vote count
            total_vote_count = db.session.query(db.func.sum(Vote.vote_type)).filter_by(comment_id=c.comment_id).scalar()
            total_vote_count = total_vote_count if total_vote_count is not None else 0

            # Check if current user has voted on this answer
            user_vote = Vote.query.filter_by(answer_id=c.answer_id, created_by=current_user).first()
            user_vote_type = user_vote.vote_type if user_vote else None

            creator = User.query.filter_by(email=c.created_by).first()

            # Append the comment details and vote count to the comment list
            comments_list.append({
                "comment_id": c.comment_id,
                "content": c.content,
                "date_commented": c.date_commented,
                "date_last_edited": c.date_last_edited,
                "created_by": c.created_by,
                "total_vote_count": total_vote_count,
                "user_vote_type": user_vote_type,  # 1 for upvote, -1 for downvote, or None
                "creator": {
                    "email": creator.email,
                    "username": creator.username,
                    "display_name": creator.display_name,
                    "reputation": creator.reputation,
                    "date_joined": creator.date_joined,
                    "date_last_login": creator.date_last_login,
                    "total_questions": creator.total_questions,
                    "total_answers": creator.total_answers,
                    "total_comments": creator.total_comments,
                    "total_votes": creator.total_votes
                },
            })

        creator = User.query.filter_by(email=a.created_by).first()

        answers_list.append({
            "answer_id": a.answer_id,
            "content": a.content,
            "date_answered": a.date_answered,
            "date_last_edited": a.date_last_edited,
            "created_by": a.created_by,
            "total_vote_count": total_vote_count,
            "user_vote_type": user_vote_type,  # 1 for upvote, -1 for downvote, or None
            "comments_list": comments_list,
            "creator": {
                "email": creator.email,
                "username": creator.username,
                "display_name": creator.display_name,
                "reputation": creator.reputation,
                "date_joined": creator.date_joined,
                "date_last_login": creator.date_last_login,
                "total_questions": creator.total_questions,
                "total_answers": creator.total_answers,
                "total_comments": creator.total_comments,
                "total_votes": creator.total_votes
            },
        })

    creator = User.query.filter_by(email=query.created_by).first()

    # Convert results to JSON

    result = {
        "id": query.question_id,
        "title": query.title,
        "content": query.content,
        "date_asked": query.date_asked,
        "date_last_edited": query.date_last_edited,
        "date_closed": query.date_closed,
        "created_by": query.created_by,
        "reputation": db.session.query(db.func.coalesce(db.func.sum(Vote.vote_type), 0)).filter_by(question_id=query.question_id).scalar(),
        "tags": [Tag.query.get(tag).name for tag in query.tags],
        "comments_of_questions_list": comments_of_questions_list,
        "answers_list": answers_list,
        "creator": {
            "email": creator.email,
            "username": creator.username,
            "display_name": creator.display_name,
            "reputation": creator.reputation,
            "date_joined": creator.date_joined,
            "date_last_login": creator.date_last_login,
            "total_questions": creator.total_questions,
            "total_answers": creator.total_answers,
            "total_comments": creator.total_comments,
            "total_votes": creator.total_votes
        },
    }

    return jsonify(result)


# Endpoint to get questions or a specific question by question_id
@blueprint_questions.route('/api/questions', methods=['GET'])
def get_questions():
    # Get query parameters
    limit = request.args.get('limit', default=10, type=int)
    question_id = request.args.get('question_id', type=str)  # UUID is a string

    # Base query
    query = Question.query

    # Filter by specific question ID from database
    if question_id:
        query = query.filter_by(question_id=question_id)

    # Limit the number of questions returned
    questions = query.limit(limit).all()

    # Convert results to JSON
    questions_list = [{
        "id": q.question_id,
        "title": q.title,
        "content": q.content,
        "date_asked": q.date_asked,
        "date_last_edited": q.date_last_edited,
        "date_closed": q.date_closed,
        "created_by": q.created_by,
        "reputation": db.session.query(db.func.coalesce(db.func.sum(Vote.vote_type), 0)).filter_by(
            question_id=q.question_id).scalar(),
        "tags": [Tag.query.get(tag).name for tag in q.tags]
    } for q in questions]

    return jsonify(questions_list)


# Endpoint to post a new question
@blueprint_questions.route('/api/questions', methods=['POST'])
def post_question():
    data = request.get_json()
    new_question = Question(
        question_id=str(uuid4()),  # Generate unique UUID for the question ID
        title=data['title'],
        content=data['content'],
        date_asked=datetime.now(),  # Set date with timezone
        date_last_edited=datetime.now(),  # Initialize with current date and time
        created_by=endpoint_users.get_current_user().get_json()['email'],  # Use created_by as per schema
        tags=data.get('tags', [])  # Assign tags if provided, otherwise empty
    )

    if not data['content']:
        return jsonify({'error': 'Content cannot be empty'}), 400

    if not data['title']:
        return jsonify({'error': 'Title cannot be empty'}), 400

    db.session.add(new_question)
    
    for tag in data.get('tags', []):
        tag = Tag.query.get(tag)
        if not tag:
            tag = Tag(name=tag)
            db.session.add(tag)
    
    db.session.commit()
    return jsonify({"message": "Question posted successfully!", "question_id": new_question.question_id}), 201


# Endpoint to update an existing question specified by question_id
@blueprint_questions.route('/api/questions/<string:question_id>', methods=['PUT'])
def update_question(question_id):
    data = request.get_json()
    question = Question.query.filter_by(question_id=question_id).first()

    if not question:
        return jsonify({"error": "Question not found"}), 404

    # Update question fields based on input
    if 'title' in data:
        question.title = data['title']
    if 'content' in data:
        question.content = data['content']
    if 'date_last_edited' in data:
        question.date_last_edited = datetime.now()  # Update with current time
    if 'date_closed' in data:
        question.date_closed = data['date_closed']
    if 'tags' in data:
        question.tags = data['tags']  # Update tags

    db.session.commit()
    return jsonify({"message": "Question updated successfully!"})


# Endpoint to delete an existing question specified by question_id
@blueprint_questions.route('/api/questions/<string:question_id>', methods=['DELETE'])
def delete_question(question_id):
    question = Question.query.filter_by(question_id=question_id).first()

    if not question:
        return jsonify({"error": "Question not found"}), 404
    if endpoint_users.get_current_user().get_json()['email'] == question.created_by:
        db.session.delete(question)
        db.session.commit()
        return jsonify({"message": "Question deleted successfully!"})
    else:
        return jsonify({"error": "You do not have permission to delete this question!"}), 403
