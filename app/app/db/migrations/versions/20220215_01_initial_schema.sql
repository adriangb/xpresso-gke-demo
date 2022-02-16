-- Create users table
create table users(
  id uuid default gen_random_uuid() primary key,
  username text not null,
  email text not null,
  bio text,
  image text,
  hashed_password text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(username),
  unique(email)
);

create index username_index on users using hash(username);
create index email_index on users using hash(email);

-- Create followers to following multi-link table
create table followers_to_followings(
  follower_id uuid not null,
  foreign key (follower_id) references users on delete cascade,
  following_id uuid not null,
  foreign key (following_id) references users on delete cascade,
  unique (follower_id, following_id)
);

create index follower_id_index on followers_to_followings(follower_id);
create index following_id_index on followers_to_followings(following_id);

-- Create triggers for created_at and updated_at columns
CREATE FUNCTION trigger_set_timestamp()
  RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER set_timestamp
  BEFORE UPDATE ON users
  FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();
