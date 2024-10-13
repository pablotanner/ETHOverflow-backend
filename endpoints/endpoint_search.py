from flask import jsonify, request, Blueprint
from transformers import BertModel, BertTokenizer
import torch
import numpy as np
from sqlalchemy import event
from models import Question, Tag, Vote
from endpoints import endpoint_users
from endpoints import endpoint_votes

blueprint_search = Blueprint("search", __name__)

# Load pre-trained model and tokenizer
model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)

def generate_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

def before_insert_listener(mapper, connection, target):
    text = target.title + " " + target.content
    target.embedding = generate_embedding(text).tolist()

def before_update_listener(mapper, connection, target):
    text = target.title + " " + target.content
    target.embedding = generate_embedding(text).tolist()

# Attach the event listeners to the Question model
event.listen(Question, 'before_insert', before_insert_listener)
event.listen(Question, 'before_update', before_update_listener)

@blueprint_search.route("/api/search", methods=['GET'])
def search():
    query = request.args.get('query', type=str)
    query_embedding = generate_embedding(query)
    
    questions = Question.query.all()
    similarities = []
    for q in questions:
        question_embedding = np.array(q.embedding)
        similarity = np.dot(query_embedding, question_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(question_embedding))
        similarities.append((q, similarity))
    
    # Sort questions by similarity
    similarities.sort(key=lambda x: x[1], reverse=True)
    questions_list = []
    for q, similarity in similarities[:10]:  # Return top 10 results
        user_vote = Vote.query.filter_by(question_id=q.question_id, created_by=endpoint_users.get_current_user().get_json()['email']).first()
        user_vote = user_vote.vote_type if user_vote else None
        question_json = {
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
        }
        questions_list.append(question_json)
    return jsonify(questions_list)