/*
Parameters:
- $1: user id, can be null. used to determine if the user liked the article and/or follows the author.
- $2: article id

Since the user id may be null, we check for that first before comparing it to the columns.
We also need to do some explicit casts so that postgres understands the type of the parameter.

The subqueries build up the dynamic attributes of the article model.
Notably, the author is returned as a JSON object (so you'll get a string back for that column).
*/
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
WHERE id = $2
