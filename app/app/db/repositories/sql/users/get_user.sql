SELECT id,
       username,
       email,
       hashed_password,
       bio,
       image
FROM users
WHERE id = $1
