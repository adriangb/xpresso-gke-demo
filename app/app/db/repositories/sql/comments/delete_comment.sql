/*
Parameters:
- $1: author id
- $2: comment id

Just like with the articles queries,
we want to delete the comment if it exists and the belongs to the current user,
but otherwise we want to differentiate the comment not existing from a user
trying to delete another's comment.
*/
WITH comments_subquery AS (
    SELECT id FROM comments WHERE id = $2
), deletion_subquery AS (
    DELETE FROM comments
    WHERE author_id = $1 AND id = $2
    RETURNING 1
)
SELECT
    EXISTS(SELECT * FROM comments_subquery) AS comment_exists,
    EXISTS(SELECT * FROM deletion_subquery) AS comment_deleted
