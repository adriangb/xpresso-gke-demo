SELECT id,
       username,
       email,
       hashed_password,
       bio,
       image
FROM users
WHERE email = $1
