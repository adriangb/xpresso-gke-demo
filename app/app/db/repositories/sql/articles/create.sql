/*
Parameters:
- $1: author id
- $2: article title
- $3: article description
- $4: article body
- $5: array of tags

This assumes that the author_id is valid because the author has already been authenticated.
*/
WITH articles_subquery AS (
    INSERT INTO articles (author_id, title, description, body)
    VALUES ($1, $2, $3, $4)
    RETURNING
        id,
        created_at,
        updated_at
), tags_subquery AS (
	INSERT INTO articles_to_tags (article_id, tag_name)
	VALUES((SELECT id FROM articles_subquery), unnest($5::text[]))
)
SELECT id, created_at, updated_at FROM articles_subquery
