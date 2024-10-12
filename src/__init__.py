from flask import Flask, request, jsonify
from config import Config
from src.database import init_db, db
from models import User, Question, Tag, Answer, Comment, Vote
import logging
from datetime import datetime
from uuid import uuid4

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database and migration
    init_db(app)

    @app.route('/test', methods=['GET'])
    def test_route():
        users = db.session.execute(db.select(User))
        return users

    # Endpoint to get question specified by question_id
    @app.route('/questions', methods=['GET'])
    def get_questions():
        # Get query parameters
        limit = request.args.get('limit', default=10, type=int)
        question_id = request.args.get('question_id', type=str)  # Use str because question_id is UUID in the schema

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
            "tags": [tag.tag_id for tag in q.tags]
        } for q in questions]

        return jsonify(questions_list)

    # Endpoint to post a new question
    @app.route('/questions', methods=['POST'])
    def post_question():
        data = request.get_json()
        new_question = Question(
            question_id=str(uuid4()),  # Generate unique UUID for the question ID
            title=data['title'],
            content=data['content'],
            date_asked=datetime.datetime.now(),  # Automatically set the date when the question is asked
            date_last_edited=datetime.datetime.now(),  # Initialize with current date and time
            created_by=data['created_by'],  # Use created_by as per schema
            tags=data.get('tags', [])  # Assign tags if provided, otherwise empty
        )
        db.session.add(new_question)
        db.session.commit()
        return jsonify({"message": "Question posted successfully!", "question_id": new_question.question_id}), 201

    # Endpoint to post an answer to a question
    @app.route('/questions/<string:question_id>/answers', methods=['POST'])
    def post_answer(question_id):
        data = request.get_json()
        new_answer = Answer(
            answer_id=str(uuid4()),  # Generate unique UUID for the answer ID
            content=data['content'],
            question_id=question_id,
            date_answered=datetime.datetime.now(),  # Automatically set the date when the answer is posted
            date_last_edited=datetime.datetime.now(),  # Initialize with current date and time
            created_by=data['created_by']  # Use created_by instead of user_id as per schema
        )
        db.session.add(new_answer)
        db.session.commit()
        return jsonify({"message": "Answer posted successfully!", "answer_id": new_answer.answer_id}), 201

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    app.logger.info("Application initialized")

    # @app.before_first_request
    # def setup_database():
    # 	 db.drop_all()
    # 	 db.create_all()
    # 	 app.logger.info("Database tables re-created")
    with app.app_context():
        db.drop_all()
        db.create_all()
        app.logger.info("Database tables re-created")

    return app
