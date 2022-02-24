/*
Parameters:
- $1: author id
- $2: article id
- $3: new title, can be null
- $4: new description, can be null
- $5: new body, can be null

This assumes that that if the user id is not null is is a valid user id because the user has been authenticated.

If no rows are returned this means the article did not exist in the first place.

The subqueries in the RETURNING statement build up the computed attributes of the article model.
Notably, the author is returned as a JSON object (so you'll get a string back for that column).
*/
WITH articles_subquery AS (
    SELECT id FROM articles WHERE id = $2
), update_subquery AS (
    UPDATE articles
    SET title        = COALESCE($3, title),
        description  = COALESCE($4, description),
        body         = COALESCE($5, body)
    WHERE author_id = $1 AND id = (SELECT id FROM articles_subquery)
    RETURNING 1
)
SELECT
    id,
    title,
    description,
    body,
    created_at,
    updated_at,
    EXISTS(SELECT * FROM favorites WHERE user_id = $1 AND article_id = id) AS favorited,
    (SELECT COUNT(*) FROM favorites WHERE article_id = id) AS favorites_count,
    (
        SELECT json_build_object(
            'username', username,
            'bio', bio,
            'image', image,
            'following', EXISTS(SELECT * FROM followers_to_followings WHERE follower_id = $1 AND following_id = author_id)
        )
        FROM users
        WHERE id = author_id
    ) AS author,
    (SELECT array_agg(tag_name) FROM articles_to_tags WHERE article_id = id) AS tags,
    EXISTS(SELECT * FROM update_subquery) AS current_user_owns_article
FROM articles
WHERE id = $2