/*
Parameters:
- $1: author id
- $2: comment id

This assumes that the author_id is valid because the author has already been authenticated.
The return value can be checked and if no rows were deleted then the comment didn't exist in the first place.
*/
DELETE FROM comments
WHERE author_id = $1 AND id = $2
