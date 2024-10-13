from models import User, Question, Answer, Vote, Comment, Tag
from datetime import datetime
from uuid import uuid4
from flask import request, jsonify, Blueprint
from src import db
from endpoints import endpoint_users, endpoint_votes
from model_managers import delete_methods

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
        total_vote_count = endpoint_votes.get_comment_vote_count(c.comment_id).get_json()['total_vote_count']

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
                "reputation": endpoint_users.get_user_vote_count(c.created_by).get_json()['total_vote_count'],
                "date_joined": creator.date_joined,
                "date_last_login": creator.date_last_login,
            },
                
        })

    answers = Answer.query.filter_by(question_id=question_id).all()

    answers_list = []

    for a in answers:
        # Calculate the total vote count
        total_vote_count = endpoint_votes.get_answer_vote_count(a.answer_id).get_json()['total_vote_count']

        # Check if current user has voted on this answer
        user_vote = Vote.query.filter_by(answer_id=a.answer_id).first()
        user_vote_type = user_vote.vote_type if user_vote else None

        comments = Comment.query.filter_by(answer_id=a.answer_id).all()
        comments_list = []

        # Loop through each answer to get its details and vote count
        for c in comments:
            # Calculate the total vote count
            total_vote_count = endpoint_votes.get_comment_vote_count(c.comment_id).get_json()['total_vote_count']

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
                    "reputation": endpoint_users.get_user_vote_count(c.created_by).get_json()['total_vote_count'],
                    "date_joined": creator.date_joined,
                    "date_last_login": creator.date_last_login,
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
                "reputation": endpoint_users.get_user_vote_count(creator.email).get_json()['total_vote_count'],
                "date_joined": creator.date_joined,
                "date_last_login": creator.date_last_login,
            },
        })

    creator = User.query.filter_by(email=query.created_by).first()

    user_vote = Vote.query.filter_by(question_id=query.question_id, created_by=current_user).first()
    user_vote_type = user_vote.vote_type if user_vote else None
    # Convert results to JSON

    result = {
        "id": query.question_id,
        "title": query.title,
        "content": query.content,
        "date_asked": query.date_asked,
        "date_last_edited": query.date_last_edited,
        "date_closed": query.date_closed,
        "created_by": query.created_by,
        "reputation": endpoint_votes.get_question_vote_count(query.question_id).get_json()['total_vote_count'],
        "tags": [Tag.query.get(tag).name for tag in query.tags],
        "comments_of_questions_list": comments_of_questions_list,
        "answers_list": answers_list,
        "user_vote_type": user_vote_type,  # 1 for upvote, -1 for downvote, or None
        "creator": {
            "email": creator.email,
            "username": creator.username,
            "display_name": creator.display_name,
            "reputation": endpoint_users.get_user_vote_count(creator.email).get_json()['total_vote_count'],
            "date_joined": creator.date_joined,
            "date_last_login": creator.date_last_login,
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
    questions_list = []
    for q in questions:
        user_vote = Vote.query.filter_by(question_id=q.question_id, created_by=endpoint_users.get_current_user().get_json()['email']).first()
        user_vote = user_vote.vote_type if user_vote else None
        
        questions_list.append({
            "id": q.question_id,
            "title": q.title,
            "content": q.content,
            "date_asked": q.date_asked,
            "date_last_edited": q.date_last_edited,
            "date_closed": q.date_closed,
            "created_by": q.created_by,
            "user_vote_type": user_vote,
            "reputation": endpoint_votes.get_question_vote_count(q.question_id).get_json()['total_vote_count'],
            "tags": [Tag.query.get(tag).name for tag in q.tags]
        })

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
    
    for tagname in data.get('tags', []):
        tag = Tag.query.get(tagname)
        if not tag:
            tag = Tag(name=tagname, questions=[new_question.question_id])
            db.session.add(tag)
        tag.questions.append(new_question.question_id)
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


# Endpoint to mark an answer as accepted answer
@blueprint_questions.route('/api/questions/<string:question_id>/mark-accepted/<string:answer_id>', methods=['PUT'])
def mark_accepted_answer(question_id, answer_id):
    question = Question.query.filter_by(question_id=question_id).first()
    if question.correct_answer_id:
        oldanswer = Answer.query.filter_by(answer_id=question.correct_answer_id).first()
        oldanswer.accepted = False
    question.correct_answer_id = answer_id
    if answer_id:
        answer = Answer.query.filter_by(answer_id=answer_id).first()
        answer.accepted = True
    db.session.commit()
    
    return  jsonify({"message": "Accepted answer updated successfully!"})


# Endpoint to delete an existing question specified by question_id
@blueprint_questions.route('/api/questions/<string:question_id>', methods=['DELETE'])
def delete_question(question_id):
    question = Question.query.filter_by(question_id=question_id).first()

    if not question:
        return jsonify({"error": "Question not found"}), 404
    if endpoint_users.get_current_user().get_json()['email'] == question.created_by:
        delete_methods.delete_question(question_id)
        return jsonify({"message": "Question deleted successfully!"})
    else:
        return jsonify({"error": "You do not have permission to delete this question!"}), 403
