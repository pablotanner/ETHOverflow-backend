# Database Schema

## Users Table

Column | Type | Attributes | Description | Necessity
--- | --- | --- | --- | ---
username | PRIMARY KEY, UNIQUE, TEXT | NOT NULL | Username for the user | Yes
email | TEXT | NOT NULL | Email address for the user | Yes
display_name | TEXT | NOT NULL | Display name for the user | Yes
date_joined | DATETIME | NOT NULL | Date and time when the user joined | No
date_last_login | DATETIME | NOT NULL | Date and time when the user last logged in | Yes
reputation | INTEGER | NOT NULL | Reputation score of the user | Yes
total_questions | INTEGER | NOT NULL | Total number of questions asked by the user | No
total_answers | INTEGER | NOT NULL | Total number of answers given by the user | No
total_comments | INTEGER | NOT NULL | Total number of comments made by the user | No
total_votes | INTEGER | NOT NULL | Total number of votes given by the user | No

## Questions Table

Column | Type | Attributes | Description | Necessity
--- | --- | --- | --- | ---
question_id | UUID | PRIMARY KEY | Unique identifier for the question | Yes
date_asked | DATETIME | NOT NULL | Date and time when the question was asked | No
date_last_edited | DATETIME | NOT NULL | Date and time when the question was last edited | Yes
date_closed | DATETIME | NULL | Date and time when the question was closed | Yes
created_by | TEXT | NOT NULL | Username of the user who asked the question | Yes
title | TEXT | NOT NULL | Title of the question | Yes
content | TEXT | NOT NULL | Content of the question | Yes
tags | INTEGER[] | NOT NULL | Array of tag IDs for the question | Yes


## Tags Table

Column | Type | Attributes | Description | Necessity
--- | --- | --- | --- | ---
tag_id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier for the tag | Yes
name | TEXT | NOT NULL | Name of the tag | Yes

## Answers Table

Column | Type | Attributes | Description | Necessity
--- | --- | --- | --- | ---
answer_id | UUID | PRIMARY KEY | Unique identifier for the answer | Yes
date_answered | DATETIME | NOT NULL | Date and time when the answer was given | No
date_last_edited | DATETIME | NOT NULL | Date and time when the answer was last edited | Yes
created_by | TEXT | NOT NULL | Username of the user who answered the question | Yes
question_id | UUID | NOT NULL | ID of the question to which the answer belongs | Yes
content | TEXT | NOT NULL | Content of the answer | Yes

## Comments Table

Column | Type | Attributes | Description | Necessity
--- | --- | --- | --- | ---
comment_id | UUID | PRIMARY KEY | Unique identifier for the comment | Yes
date_commented | DATETIME | NOT NULL | Date and time when the comment was made | No
date_last_edited | DATETIME | NOT NULL | Date and time when the comment was last edited | Yes
question_id | UUID | NULL | ID of the question to which the comment belongs | Yes
answer_id | UUID | NULL | ID of the answer to which the comment belongs | Yes
created_by | TEXT | NOT NULL | Username of the user who made the comment | Yes
content | TEXT | NOT NULL | Content of the comment | Yes

## Votes Table

Column | Type | Attributes | Description | Necessity
--- | --- | --- | --- | ---
vote_id | UUID | PRIMARY KEY | Unique identifier for the vote | Yes
date_voted | DATETIME | NOT NULL | Date and time when the vote was cast | No
created_by | TEXT | NOT NULL | Username of the user who cast the vote | Yes
question_id | UUID | NULL | ID of the question to which the vote belongs | Yes
answer_id | UUID | NULL | ID of the answer to which the vote belongs | Yes
comment_id | UUID | NULL | ID of the comment to which the vote belongs | Yes
vote_type | INTEGER | NOT NULL | Type of vote (1 for upvote, -1 for downvote) | Yes
