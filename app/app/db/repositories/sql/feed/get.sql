-- $1 = current user's ID, maybe null
-- $5 = limit
-- $6 = offset
SELECT
    articles.id,
    articles.title,
    articles.description,
    articles.body,
    articles.created_at,
    articles.updated_at,
    EXISTS(SELECT 1 FROM favorites WHERE $1::uuid IS NOT NULL AND user_id = $1::uuid AND article_id = id) AS favorited,
    (SELECT COUNT(*) FROM favorites WHERE article_id = id) AS favorites_count,
    (
        SELECT json_build_object(
            'username', username,
            'bio', bio,
            'image', image,
            'following', EXISTS(SELECT 1 FROM followers_to_followings WHERE $1::uuid IS NOT NULL AND follower_id = $1::uuid AND following_id = author_id)
        )
        FROM users
        WHERE id = author_id
    ) AS author,
    (SELECT array_agg(tag_name) FROM articles_to_tags WHERE article_id = id) AS tags
FROM articles
INNER JOIN followers_to_followings ON (follower_id = $1 AND following_id = articles.author_id)
ORDER BY created_at DESC
LIMIT $2
OFFSET $3;