from models import User, Question, Answer, Vote, Comment, Tag
from datetime import datetime
from uuid import uuid4
from flask import request, jsonify, Blueprint
from src import db
from endpoints import endpoint_users

blueprint_questions = Blueprint("questions", __name__)

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
        "reputation": db.session.query(db.func.coalesce(db.func.sum(Vote.vote_type), 0)).filter_by(question_id=q.question_id).scalar(),
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
        created_by=endpoint_users.get_current_user(),
        tags=data.get('tags', [])  # Assign tags if provided, otherwise empty
    )
    db.session.add(new_question)
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

    db.session.delete(question)
    db.session.commit()
    return jsonify({"message": "Question deleted successfully!"})
