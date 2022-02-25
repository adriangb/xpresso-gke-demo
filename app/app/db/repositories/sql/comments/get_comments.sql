/*
This one is relatively straightforward.
The one caveat is we do have to differentiate between there being no article
and that article having no comments.
Luckily, asyncpg's fetch differentiates these two scenarios.
*/
SELECT
    id,
    created_at,
    updated_at,
    body,
    (
        SELECT json_build_object(
            'username', username,
            'bio', bio,
            'image', image,
            'following', EXISTS(SELECT * FROM followers_to_followings WHERE $1::uuid IS NOT NULL AND follower_id = $1::uuid AND following_id = author_id)
        )
        FROM users
        WHERE id = author_id
    ) AS author
FROM comments
WHERE article_id = $2
