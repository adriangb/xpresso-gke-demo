/*
Parameters:
- $1: author id
- $2: article id
- $3: comment body

This assumes that that if the user id is not null is is a valid user id because the user has been authenticated.

If the article doesn't exist, this will return a FK violation error.

In our main select query we build up the author's profile in a subquery, which returns a json object
(so you'll have to parse the JSON string on the application side).
*/
WITH created_comment AS (
    INSERT INTO comments (author_id, article_id, body) VALUES ($1, $2, $3)
    RETURNING id, created_at, updated_at
)
SELECT
    id,
    created_at,
    updated_at,
    (
        SELECT json_build_object(
            'username', username,
            'bio', bio,
            'image', image
        )
        FROM users
        WHERE id = $1
    ) AS author
FROM created_comment
