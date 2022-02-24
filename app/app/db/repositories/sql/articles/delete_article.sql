/*
Parameters:
- $1: author id
- $2: article id

This assumes that the author_id is valid because the author has already been authenticated.

If the article is deleted, comments and favorites will be cascade deleted and
subsequently a trigger will delete any tags that no longer have articles.

There are two CTEs that are used to differentiate between the case when the article does
not exist and when it exists but the user does not own it.
*/
WITH article_subquery AS (
    SELECT id FROM articles WHERE id = $2
), delete_subquery AS (
    DELETE FROM articles
    WHERE EXISTS(SELECT * FROM article_subquery) AND author_id = $1 AND id = (SELECT id FROM article_subquery)
    RETURNING 1
)
SELECT
    EXISTS(SELECT * FROM article_subquery) AS article_exists,
    EXISTS(SELECT * FROM delete_subquery) AS article_deleted
