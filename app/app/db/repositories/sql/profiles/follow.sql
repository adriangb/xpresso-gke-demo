WITH followed_profile_subquery AS (
    SELECT id, username, bio, image
    FROM users
    WHERE username = $2
), follow_subquery AS (
    INSERT INTO followers_to_followings (follower_id, following_id)
    VALUES (
        $1,
        (SELECT id from followed_profile_subquery)
    )
)
SELECT username, bio, image FROM followed_profile_subquery
