INSERT INTO users (username, email, hashed_password)
VALUES ($1, $2, $3)
RETURNING id
