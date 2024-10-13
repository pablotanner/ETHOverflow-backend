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
    questions = [
        {
            "title": "What are some effective strategies for competitive programming?",
            "content": "I want to improve my skills in competitive programming. Any tips?",
            "created_by": "jdoe@example.com",
            "tags": ["Competitive Programming", "Algorithms", "Data Structures"],
        },
        {
            "title": "How do distributed systems handle fault tolerance?",
            "content": "I'm curious about the mechanisms used in distributed systems to ensure reliability.",
            "created_by": "asmith@example.com",
            "tags": ["Distributed Systems", "Fault Tolerance", "Networking"],
        },
        {
            "title": "What are some best practices for cybersecurity in IoT?",
            "content": "I'm working on an IoT project and want to ensure it's secure. Any guidance?",
            "created_by": "bwilliams@example.com",
            "tags": ["IoT", "Cybersecurity", "Best Practices"],
        },
        {
            "title": "How does functional programming differ from object-oriented programming?",
            "content": "I'm trying to understand the main differences between these two paradigms.",
            "created_by": "jdoe@example.com",
            "tags": ["Functional Programming", "Object-Oriented Programming", "Programming Paradigms"],
        },
        {
            "title": "What are the key principles of agile software development?",
            "content": "I want to understand how agile methodology works and its benefits for software projects.",
            "created_by": "asmith@example.com",
            "tags": ["Agile", "Software Development", "Project Management"],
        },
        {
            "title": "How can I optimize SQL queries for large databases?",
            "content": "I'm working with a large database and want to improve query performance.",
            "created_by": "bwilliams@example.com",
            "tags": ["SQL", "Databases", "Optimization"],
        },
        {
            "title": "What are the ethical implications of AI in healthcare?",
            "content": "I'm interested in how AI impacts privacy and ethics in healthcare.",
            "created_by": "jdoe@example.com",
            "tags": ["AI", "Healthcare", "Ethics"],
        },
        {
            "title": "How does Ethereum differ from Bitcoin in terms of blockchain technology?",
            "content": "I want to understand the technical differences between Ethereum and Bitcoin.",
            "created_by": "asmith@example.com",
            "tags": ["Blockchain", "Ethereum", "Bitcoin"],
        },
        {
            "title": "What are some common techniques for 3D rendering in computer graphics?",
            "content": "I'm curious about the basic methods used for 3D rendering.",
            "created_by": "bwilliams@example.com",
            "tags": ["Computer Graphics", "3D Rendering", "Rendering Techniques"],
        },
        {
            "title": "How can I set up a CI/CD pipeline for my project?",
            "content": "I need help setting up continuous integration and delivery for my web application.",
            "created_by": "jdoe@example.com",
            "tags": ["CI/CD", "DevOps", "Automation"],
        },
        {
            "title": "What are the benefits and challenges of cloud computing?",
            "content": "I'm interested in the advantages and potential issues with using cloud services.",
            "created_by": "asmith@example.com",
            "tags": ["Cloud Computing", "Benefits", "Challenges"],
        },
        {
            "title": "How can I get started with quantum computing?",
            "content": "I'm fascinated by quantum computing and want to learn the basics.",
            "created_by": "bwilliams@example.com",
            "tags": ["Quantum Computing", "Beginners", "Computing"],
        },
        {
            "title": "What are some common techniques for reverse engineering?",
            "content": "I'm interested in understanding how reverse engineering is used in software analysis.",
            "created_by": "jdoe@example.com",
            "tags": ["Reverse Engineering", "Software Analysis", "Security"],
        },
        {
            "title": "How does natural language processing differ from traditional linguistics?",
            "content": "I'm curious about the differences between NLP and linguistics in terms of their goals and methods.",
            "created_by": "asmith@example.com",
            "tags": ["NLP", "Linguistics", "AI"],
        },
        {
            "title": "What is homomorphic encryption, and how is it applied?",
            "content": "I'm interested in learning about homomorphic encryption and its use cases.",
            "created_by": "bwilliams@example.com",
            "tags": ["Encryption", "Homomorphic Encryption", "Cryptography"],
        },
        {
            "title": "How can I contribute to open-source projects as a beginner?",
            "content": "I want to start contributing to open-source, but I'm not sure where to begin.",
            "created_by": "jdoe@example.com",
            "tags": ["Open Source", "Beginners", "Software Development"],
        },
        {
            "title": "What are the principles of UX design for mobile applications?",
            "content": "I'm working on a mobile app and want to ensure a good user experience.",
            "created_by": "asmith@example.com",
            "tags": ["UX Design", "Mobile Apps", "User Experience"],
        },
        {
            "title": "What are the basics of Bayesian statistics?",
            "content": "I want to understand the fundamentals of Bayesian approaches in statistics.",
            "created_by": "bwilliams@example.com",
            "tags": ["Bayesian Statistics", "Statistics", "Data Science"],
        },
        {
            "title": "How does blockchain technology support decentralized finance (DeFi)?",
            "content": "I'm curious about how blockchain enables DeFi and its potential impact.",
            "created_by": "jdoe@example.com",
            "tags": ["Blockchain", "DeFi", "Finance"],
        },
        {
            "title": "What are the best practices for securing a REST API?",
            "content": "I'm developing a REST API and want to ensure it's secure against attacks.",
            "created_by": "asmith@example.com",
            "tags": ["API Security", "REST API", "Web Security"],
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
            "question_id": Question.query.filter_by(title="What are the basics of Bayesian statistics?")
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
                title="What are the basics of Bayesian statistics?"
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
