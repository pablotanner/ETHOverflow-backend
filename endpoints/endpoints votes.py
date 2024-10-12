# Endpoint to add or update a vote on an answer
@app.route('/answers/<string:answer_id>/vote', methods=['POST'])
def vote_on_answer(answer_id):
    data = request.get_json()
    vote_type = data.get('vote_type')  # Should be 1 (upvote) or -1 (downvote)
    created_by = data.get('created_by')  # User who cast the vote

    # Check if a vote by this user on this answer already exists
    vote = Vote.query.filter_by(answer_id=answer_id, created_by=created_by).first()

    if vote:
        # If vote exists, update the vote type
        vote.vote_type = vote_type
    else:
        # If no vote exists, create a new vote
        new_vote = Vote(
            vote_id=str(uuid4()),
            answer_id=answer_id,
            vote_type=vote_type,
            created_by=created_by,
            date_voted=datetime.now(switzerland_tz)
        )
        db.session.add(new_vote)

    db.session.commit()
    return jsonify({"message": "Vote recorded successfully!"}), 201
