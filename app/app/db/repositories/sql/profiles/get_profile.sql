SELECT
    username,
    bio,
    image,
    EXISTS(SELECT * FROM followers_to_followings WHERE $1::uuid IS NOT NULL AND follower_id = $1::uuid AND following_id = id) AS following
FROM users
WHERE username = $2
