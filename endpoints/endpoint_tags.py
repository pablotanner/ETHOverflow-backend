from models import Question, Tag
from flask import request, jsonify, Blueprint
from src import db

blueprint_tags = Blueprint("tags", __name__)

@blueprint_tags.route("/api/tags", methods=['GET'])
def get_tags():
    tags = Tags.query().all()
    tags_list = [name for name in tags]
    return jsonify(tags_list)

@blueprint_tags.route("/api/tags/<string:name>", methods=['GET'])
def tags_get_questions(name):
    tags = Tags.query().filterby(name=name).first()
    questions_list = []
    for question_id in tags.questions:
        q = Question.query().filterby(question_id=question_id).first()
        question_json = {
            "id": q.question_id,
            "title": q.title,
            "content": q.content,
            "date_asked": q.date_asked,
            "date_last_edited": q.date_last_edited,
            "date_closed": q.date_closed,
            "created_by": q.created_by,
            "reputation": endpoint_votes.get_question_vote_count(q.question_id).get_json()['total_vote_count'],
            "tags": [Tag.query.get(tag).name for tag in q.tags]
        }
        questions_list.append(question_json)
    return jsonify(questions_list)
