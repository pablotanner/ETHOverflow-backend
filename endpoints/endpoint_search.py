from models import Question, Tag
from flask import request, jsonify, Blueprint
from src import db
from endpoints import endpoint_votes

blueprint_search = Blueprint("search", __name__)

@blueprint_search.route("/api/search", methods=['GET'])
def search():
	query = request.args.get('query', type=str)
	questions = Question.query.filter(Question.title.ilike(f"%{query}%")).all()
	questions_list = []
	for q in questions:
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

