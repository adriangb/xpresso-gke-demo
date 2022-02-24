WITH followed_profile_subquery AS (
    SELECT id, username, bio, image
    FROM users
    WHERE username = $2
), follow_subquery AS (
    DELETE FROM followers_to_followings
    WHERE follower_id = $1 AND following_id = (SELECT id from followed_profile_subquery)
)
SELECT username, bio, image FROM followed_profile_subquery
