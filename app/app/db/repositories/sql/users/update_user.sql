UPDATE users
SET username        = COALESCE($2, username),
    email           = COALESCE($3, email),
    bio             = COALESCE($4, bio),
    image           = COALESCE($5, image),
    hashed_password = COALESCE($6, hashed_password)
WHERE id = $1
RETURNING
    id,
    username,
    email,
    bio,
    image,
    hashed_password
