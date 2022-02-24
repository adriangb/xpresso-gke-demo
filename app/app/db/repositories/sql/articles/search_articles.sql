/*
Parameters:
- $1: user id, can be null. used to determine if the user liked the article and/or follows the author.
- $2: a tag to filter by, can be null
- $3: an author username to filter by, can be null
- $4: a username to filter by users that have favorited the article, can be null
- $5: offset
- $6: limit

The strategy here is to push the filtering into sub-queries that select only matching rows from
their respective tables / link tables.
Then in our main select query we filter on those rows _only if that parameter is not null_.
This will generate multiple query paths depending on what parameters are included,
but each individual query path should be optimal since it will optimize away the
CTEs and WHERE clauses for paramters that are null.

This assumes that that if the user id is not null is is a valid user id because the user has been authenticated.
In our main SELECT query, the subqueries build up the dynamic attributes of the article model.
Notably, the author is returned as a JSON object (so you'll get a string back for that column).
*/
WITH matched_tags AS (
        SELECT article_id, tag_name FROM articles_to_tags
        WHERE $2::text IS NOT NULL AND tag_name = $2::text
    ), filter_author AS (
        SELECT id FROM users
        WHERE ($3::text IS NOT NULL AND username = $3::text)
    ), articles_favorited_by_filter_user AS (
        SELECT articles.id
        FROM users
        LEFT JOIN favorites ON (favorites.user_id = users.id)
        LEFT JOIN articles ON (favorites.article_id = articles.id)
        WHERE ($4::text IS NOT NULL AND users.username = $4::text)
    )
SELECT
    articles.id,
    articles.title,
    articles.description,
    articles.body,
    articles.created_at,
    articles.updated_at,
    EXISTS(SELECT * FROM favorites WHERE $1::uuid IS NOT NULL AND user_id = $1::uuid AND article_id = id) AS favorited,
    (SELECT COUNT(*) FROM favorites WHERE article_id = id) AS favorites_count,
    (
        SELECT json_build_object(
            'username', username,
            'bio', bio,
            'image', image,
            'following', EXISTS(SELECT * FROM followers_to_followings WHERE $1::uuid IS NOT NULL AND follower_id = $1::uuid AND following_id = author_id)
        )
        FROM users
        WHERE id = author_id
    ) AS author,
    (SELECT array_agg(tag_name) FROM articles_to_tags WHERE article_id = id) AS tags
FROM articles
WHERE (
    ($2::text IS NULL OR id IN (SELECT article_id FROM matched_tags))
    AND
    ($3::text IS NULL OR author_id IN (SELECT id FROM filter_author))
    AND
    ($4::text IS NULL OR id IN (SELECT id FROM articles_favorited_by_filter_user))
)
ORDER BY created_at DESC
LIMIT $5
OFFSET $6
