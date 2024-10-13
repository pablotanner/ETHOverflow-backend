from flask import Flask, request, jsonify
from config import Config
from src.database import init_db, db
from models import User, Question, Tag, Answer, Comment, Vote
import logging
import datetime
from uuid import uuid4
from endpoints.endpoint_questions import blueprint_questions
from endpoints.endpoint_answers import blueprint_answers
from endpoints.endpoint_comments import blueprint_comments
from endpoints.endpoint_users import blueprint_users
from endpoints.endpoint_user_activity import blueprint_user_activity
from endpoints.endpoint_votes import blueprint_votes
from endpoints.endpoint_tags import blueprint_tags
from endpoints.endpoint_search import blueprint_search


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database and migration
    init_db(app)
    
    app.register_blueprint(blueprint_questions)
    app.register_blueprint(blueprint_answers)
    app.register_blueprint(blueprint_comments)
    app.register_blueprint(blueprint_users)
    app.register_blueprint(blueprint_user_activity)
    app.register_blueprint(blueprint_votes)
    app.register_blueprint(blueprint_tags)
    app.register_blueprint(blueprint_search)
    
    

    # @app.route("/api/test", methods=["GET"])
    # def test_route():
    #     users = User.query.all()
    #
    #     return jsonify(
    #         [
    #             {
    #                 "username": user.username,
    #                 "email": user.email,
    #                 "display_name": user.display_name,
    #                 "date_joined": user.date_joined,
    #                 "date_last_login": user.date_last_login,
    #                 "reputation": user.reputation,
    #                 "total_questions": user.total_questions,
    #                 "total_answers": user.total_answers,
    #                 "total_comments": user.total_comments,
    #                 "total_votes": user.total_votes,
    #             }
    #             for user in users
    #         ]
    #     )
    #
    # # Endpoint to get question specified by question_id
    # @app.route("/api/questions", methods=["GET"])
    # def get_questions():
    #     # Get query parameters
    #     limit = request.args.get("limit", default=10, type=int)
    #     question_id = request.args.get(
    #         "question_id", type=str
    #     )  # Use str because question_id is UUID in the schema
    #
    #     # Base query
    #     query = Question.query
    #
    #     # Filter by specific question ID from database
    #     if question_id:
    #         query = query.filter_by(question_id=question_id)
    #
    #     # Limit the number of questions returned
    #     questions = query.limit(limit).all()
    #
    #     # Convert results to JSON
    #     questions_list = [
    #         {
    #             "id": q.question_id,
    #             "title": q.title,
    #             "content": q.content,
    #             "date_asked": q.date_asked,
    #             "date_last_edited": q.date_last_edited,
    #             "date_closed": q.date_closed,
    #             "created_by": q.created_by,
    #             "tags": [tag.tag_id for tag in q.tags],
    #         }
    #         for q in questions
    #     ]
    #
    #     return jsonify(questions_list)
    #
    # # Endpoint to post a new question
    # @app.route("/api/questions", methods=["POST"])
    # def post_question():
    #     data = request.get_json()
    #     new_question = Question(
    #         question_id=str(uuid4()),  # Generate unique UUID for the question ID
    #         title=data["title"],
    #         content=data["content"],
    #         date_asked=datetime.datetime.now(),  # Automatically set the date when the question is asked
    #         date_last_edited=datetime.datetime.now(),  # Initialize with current date and time
    #         created_by=data["created_by"],  # Use created_by as per schema
    #         tags=data.get("tags", []),  # Assign tags if provided, otherwise empty
    #     )
    #     db.session.add(new_question)
    #     db.session.commit()
    #     return (
    #         jsonify(
    #             {
    #                 "message": "Question posted successfully!",
    #                 "question_id": new_question.question_id,
    #             }
    #         ),
    #         201,
    #     )
    #
    # # Endpoint to post an answer to a question
    # @app.route("/api/questions/<string:question_id>/answers", methods=["POST"])
    # def post_answer(question_id):
    #     data = request.get_json()
    #     new_answer = Answer(
    #         answer_id=str(uuid4()),  # Generate unique UUID for the answer ID
    #         content=data["content"],
    #         question_id=question_id,
    #         date_answered=datetime.datetime.now(),  # Automatically set the date when the answer is posted
    #         date_last_edited=datetime.datetime.now(),  # Initialize with current date and time
    #         created_by=data[
    #             "created_by"
    #         ],  # Use created_by instead of user_id as per schema
    #     )
    #     db.session.add(new_answer)
    #     db.session.commit()
    #     return (
    #         jsonify(
    #             {
    #                 "message": "Answer posted successfully!",
    #                 "answer_id": new_answer.answer_id,
    #             }
    #         ),
    #         201,
    #     )

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    app.logger.info("Application initialized")

    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_db()
        app.logger.info("Database tables re-created")

    return app


def seed_db():
    # Define some initial users
    users = [
        {
            "username": "jdoe",
            "email": "jdoe@example.com",
            "display_name": "John Doe",
            "date_joined": datetime.datetime.utcnow(),
            "date_last_login": datetime.datetime.utcnow(),
        },
        {
            "username": "asmith",
            "email": "asmith@example.com",
            "display_name": "Alice Smith",
            "date_joined": datetime.datetime.utcnow(),
            "date_last_login": datetime.datetime.utcnow(),
        },
        {
            "username": "bwilliams",
            "email": "bwilliams@example.com",
            "display_name": "Bob Williams",
            "date_joined": datetime.datetime.utcnow(),
            "date_last_login": datetime.datetime.utcnow(),
        },
    ]

    # Insert users into the database
    for user_data in users:
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            display_name=user_data["display_name"],
            date_joined=user_data["date_joined"],
            date_last_login=user_data["date_last_login"],
        )
        db.session.add(user)
    db.session.commit()

    # Define some initial questions
    questions = questions = [
        {
            "title": "What are the health benefits of a Mediterranean diet?",
            "content": "I've heard a lot about the Mediterranean diet. What are its benefits?",
            "created_by": "jdoe@example.com",
            "tags": ["Health", "Nutrition", "Diet"],
        },
        {
            "title": "How does quantum computing differ from classical computing?",
            "content": "I'm interested in understanding the basic principles of quantum computing.",
            "created_by": "asmith@example.com",
            "tags": ["Technology", "Quantum Computing", "Science"],
        },
        {
            "title": "Who was the first woman to fly solo across the Atlantic?",
            "content": "I want to know more about the achievements of pioneering aviators.",
            "created_by": "bwilliams@example.com",
            "tags": ["History", "Aviation", "Women"],
        },
        {
            "title": "What causes seasonal allergies?",
            "content": "Every spring, I suffer from allergies. What triggers them?",
            "created_by": "jdoe@example.com",
            "tags": ["Health", "Allergies", "Medicine"],
        },
        {
            "title": "Can AI help with climate change?",
            "content": "I've read that AI is being used in environmental science. How does it help with climate change?",
            "created_by": "asmith@example.com",
            "tags": ["Technology", "AI", "Environment"],
        },
        {
            "title": "What are the basic principles of the Theory of Relativity?",
            "content": "Can someone explain Einstein's Theory of Relativity in simple terms?",
            "created_by": "bwilliams@example.com",
            "tags": ["Physics", "Science", "Relativity"],
        },
        {
            "title": "How do plants use photosynthesis?",
            "content": "I am curious about how plants convert sunlight into energy.",
            "created_by": "jdoe@example.com",
            "tags": ["Biology", "Science", "Photosynthesis"],
        },
        {
            "title": "What are the major causes of World War I?",
            "content": "I'm interested in understanding the events that led to the outbreak of WWI.",
            "created_by": "asmith@example.com",
            "tags": ["History", "World War I", "Politics"],
        },
        {
            "title": "How can meditation reduce stress?",
            "content": "I've heard meditation is good for stress relief. How does it work?",
            "created_by": "bwilliams@example.com",
            "tags": ["Health", "Wellness", "Meditation"],
        },
        {
            "title": "What are the steps in the water cycle?",
            "content": "I'd like a basic explanation of how the water cycle works.",
            "created_by": "jdoe@example.com",
            "tags": ["Geography", "Science", "Water Cycle"],
        },
        {
            "title": "How does the stock market work?",
            "content": "Can someone explain the basics of how the stock market functions?",
            "created_by": "asmith@example.com",
            "tags": ["Finance", "Economics", "Investing"],
        },
        {
            "title": "What were the major achievements of the Roman Empire?",
            "content": "I'd like to know more about the Roman Empire's contributions to the modern world.",
            "created_by": "bwilliams@example.com",
            "tags": ["History", "Ancient Rome", "Civilization"],
        },
        {
            "title": "How do vaccines work to protect against diseases?",
            "content": "I'm curious about the science behind vaccines and how they provide immunity.",
            "created_by": "jdoe@example.com",
            "tags": ["Health", "Medicine", "Vaccines"],
        },
        {
            "title": "What is the significance of the Renaissance period?",
            "content": "I want to understand the cultural and historical impact of the Renaissance.",
            "created_by": "asmith@example.com",
            "tags": ["History", "Art", "Renaissance"],
        },
        {
            "title": "What is blockchain technology?",
            "content": "How does blockchain work, and what are its applications outside of cryptocurrency?",
            "created_by": "bwilliams@example.com",
            "tags": ["Technology", "Blockchain", "Cryptocurrency"],
        },
        {
            "title": "How do animals adapt to survive in extreme environments?",
            "content": "I'm interested in learning about animal adaptations in harsh climates.",
            "created_by": "jdoe@example.com",
            "tags": ["Biology", "Animals", "Adaptation"],
        },
        {
            "title": "What were the causes and effects of the Industrial Revolution?",
            "content": "Can someone explain the main causes and consequences of the Industrial Revolution?",
            "created_by": "asmith@example.com",
            "tags": ["History", "Industrial Revolution", "Economics"],
        },
        {
            "title": "How does the human brain process emotions?",
            "content": "I'd like to know more about the neuroscience behind emotional processing.",
            "created_by": "bwilliams@example.com",
            "tags": ["Science", "Neuroscience", "Psychology"],
        },
        {
            "title": "What is the process of photosynthesis?",
            "content": "Can someone explain the photosynthesis process in plants?",
            "created_by": "jdoe@example.com",
            "tags": ["Biology", "Plants", "Photosynthesis"],
        },
        {
            "title": "How do electric cars work?",
            "content": "I'm curious about the technology behind electric vehicles and how they differ from traditional cars.",
            "created_by": "asmith@example.com",
            "tags": ["Technology", "Electric Vehicles", "Environment"],
        }
    ]

    # Define some initial tags
    tags = set()
    for question_data in questions:
        tags.update(question_data["tags"])
    tags = [{"name": tag} for tag in tags]

    # Insert tags into the database
    for tag_data in tags:
        tag = Tag(name=tag_data["name"])
        db.session.add(tag)
    db.session.commit()

    # Insert questions into the database
    for question_data in questions:
        question = Question(
            title=question_data["title"],
            content=question_data["content"],
            created_by=question_data["created_by"],
            tags=question_data["tags"],
        )
        db.session.add(question)
    db.session.commit()

    # Define some initial answers
    answers = [
        {
            "content": "You can use the psycopg2 library.",
            "created_by": "bwilliams@example.com",
            "question_id": Question.query.first().question_id,
        },
        {
            "content": "SQLAlchemy is an ORM for Python.",
            "created_by": "jdoe@example.com",
            "question_id": Question.query.filter_by(title="What is blockchain technology?")
            .first()
            .question_id,
        },
    ]

    # Insert answers into the database
    for answer_data in answers:
        answer = Answer(
            content=answer_data["content"],
            created_by=answer_data["created_by"],
            question_id=answer_data["question_id"],
        )
        db.session.add(answer)
    db.session.commit()

    # Define some initial comments
    comments = [
        {
            "content": "Thanks for the answer!",
            "created_by": "asmith@example.com",
            "answer_id": Answer.query.first().answer_id,
        },
        {
            "content": "This is very helpful.",
            "created_by": "bwilliams@example.com",
            "question_id": Question.query.filter_by(
                title="What is blockchain technology?"
            )
            .first()
            .question_id,
        },
    ]

    # Insert comments into the database
    for comment_data in comments:
        comment = Comment(
            content=comment_data["content"],
            created_by=comment_data["created_by"],
            question_id=comment_data.get("question_id"),
            answer_id=comment_data.get("answer_id"),
        )
        db.session.add(comment)
    db.session.commit()

    # Define some initial votes
    votes = [
        {
            "vote_type": 1,  # upvote
            "created_by": "jdoe@example.com",
            "question_id": Question.query.first().question_id,
        },
        {
            "vote_type": -1,  # downvote
            "created_by": "asmith@example.com",
            "answer_id": Answer.query.first().answer_id,
        },
    ]

    # Insert votes into the database
    for vote_data in votes:
        vote = Vote(
            vote_type=vote_data["vote_type"],
            created_by=vote_data["created_by"],
            question_id=vote_data.get("question_id"),
            answer_id=vote_data.get("answer_id"),
        )
        db.session.add(vote)
    db.session.commit()
