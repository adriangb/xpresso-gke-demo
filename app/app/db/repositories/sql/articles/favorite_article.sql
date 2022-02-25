/*
Parameters:
- $1: user id
- $2: article id

This assumes that the user id is valid because the user has already been authenticated.

If the article doesn't exist, this will return no rows.
If the article does exist, this will return the article regardless of whether it was already favorited.
*/
WITH favorites_subquery AS (
	INSERT INTO favorites (user_id, article_id) VALUES ($1, $2)
    ON CONFLICT DO NOTHING
    RETURNING 1
)
SELECT
    articles.id,
    articles.title,
    articles.description,
    articles.body,
    articles.created_at,
    articles.updated_at,
    true AS favorited,
    (SELECT COUNT(*) + (SELECT COUNT(*) FROM favorites_subquery) FROM favorites WHERE article_id = id) AS favorites_count,
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
    (SELECT array_agg(tag_name ORDER BY tag_name ASC) FROM articles_to_tags WHERE article_id = id) AS tags
FROM articles
WHERE id = $2
