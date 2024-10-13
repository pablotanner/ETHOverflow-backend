from flask import jsonify, request, Blueprint
from transformers import BertModel, BertTokenizer
import torch
import numpy as np
from sqlalchemy import event
from sqlalchemy.sql import func
from models import Question, Tag, Vote, User
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


def listener(mapper, connection, target):
    target.search_vector = func.to_tsvector('english', target.title + " " + target.content)
    target.tag_vector = func.to_tsvector('english', " ".join(target.tags))
    text = target.title + " " + target.content + " " + " ".join(target.tags)
    target.embedding = generate_embedding(text).tolist()


# Attach the event listeners to the Question model
event.listen(Question, 'before_insert', listener)
event.listen(Question, 'before_update', listener)

@blueprint_search.route("/api/search", methods=['GET'])
def search():
    query = request.args.get('query', type=str)
    ts_query = func.plainto_tsquery('english', query)
    full_text_results = Question.query.filter(Question.search_vector.op('@@')(ts_query)).all()
    full_tag_results = Question.query.filter(Question.tag_vector.op('@@')(ts_query)).all()
    
    query_embedding = generate_embedding(query)
    semantic_results = []
    for q in Question.query.all():
        question_embedding = np.array(q.embedding)
        similarity = np.dot(query_embedding, question_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(question_embedding))
        semantic_results.append((q, similarity))
    
    # Sort semantic results by similarity
    semantic_results.sort(key=lambda x: x[1], reverse=True)
    
    # Combine results
    combined_results = {}
    for q in full_text_results:
        combined_results[q.question_id] = {'question': q, 'score': 1.0}  # Full-text search score
        
    for q in full_tag_results:
        if q.question_id in combined_results:
            combined_results[q.question_id]['score'] += 10.0
        else:
            combined_results[q.question_id] = {'question': q, 'score': 1.0}
    
    for q, similarity in semantic_results:
        if q.question_id in combined_results:
            combined_results[q.question_id]['score'] += similarity  # Combine scores
        else:
            combined_results[q.question_id] = {'question': q, 'score': similarity}
            
    
    
    # Sort combined results by score
    sorted_combined_results = sorted(combined_results.values(), key=lambda x: x['score'], reverse=True)
    
    questions_list = []
    for result in sorted_combined_results[:10]:  # Return top 10 results
        q = result['question']
        user_vote = Vote.query.filter_by(question_id=q.question_id, created_by=endpoint_users.get_current_user().get_json()['email']).first()
        user_vote = user_vote.vote_type if user_vote else None
        creator = User.query.filter_by(email=q.created_by).first()
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
            "tags": [Tag.query.get(tag).name for tag in q.tags],
            "creator": {
                "email": creator.email,
                "username": creator.username,
                "display_name": creator.display_name,
                "reputation": endpoint_users.get_user_vote_count(creator.email).get_json()['total_vote_count'],
                "date_joined": creator.date_joined,
                "date_last_login": creator.date_last_login,
            },
        }
        questions_list.append(question_json)

    
    return jsonify(questions_list)
