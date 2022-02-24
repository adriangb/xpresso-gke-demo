/*
Parameters:
- $1: user id, can be null. used to determine if the user liked the article and/or follows the author.
- $2: offset
- $3: limit

The main thing to note here is that the author subquery is aggregated into a JSON object.
*/
SELECT
    id,
    title,
    description,
    articles.body,
    articles.created_at,
    articles.updated_at,
    EXISTS(SELECT * FROM favorites WHERE user_id = $1 AND article_id = id) AS favorited,
    (SELECT COUNT(*) FROM favorites WHERE article_id = id) AS favorites_count,
    (
        SELECT json_build_object(
            'username', username,
            'bio', bio,
            'image', image,
            'following', true
        )
        FROM users
        WHERE id = author_id
    ) AS author,
    (SELECT array_agg(tag_name) FROM articles_to_tags WHERE article_id = id) AS tags
FROM articles
INNER JOIN followers_to_followings ON (follower_id = $1 AND following_id = articles.author_id)
ORDER BY articles.created_at DESC
LIMIT $2
OFFSET $3
