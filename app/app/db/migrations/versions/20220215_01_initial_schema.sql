-- Create triggers for created_at and updated_at columns
CREATE FUNCTION trigger_set_timestamp()
  RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

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

CREATE TRIGGER set_users_upated_at
  BEFORE UPDATE ON users
  FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Create followers to following multi-link table
create table followers_to_followings(
  follower_id uuid not null,
  foreign key (follower_id) references users on delete cascade,
  following_id uuid not null,
  foreign key (following_id) references users on delete cascade,
  created_at timestamptz not null default now(),
  unique (follower_id, following_id),
  CONSTRAINT user_can_not_follow_themselves check (follower_id != following_id)
);

create index follower_id_index on followers_to_followings(follower_id);
create index following_id_index on followers_to_followings(following_id);

-- Create tags table
create table tags(
  tag_name text primary key
);

create index tag_name_index on tags using hash(tag_name);

-- Create articles table
create table articles(
  id uuid default gen_random_uuid() primary key,
  title text not null,
  description text not null,
  body text,
  author_id uuid,
  foreign key (author_id) references users on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index author_index on articles(author_id);

CREATE TRIGGER set_articles_updated_at
  BEFORE UPDATE ON articles
  FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Create articles <-> tags table
create table articles_to_tags(
  article_id uuid not null,
  foreign key (article_id) references articles on delete cascade,
  tag_name text not null,
  foreign key (tag_name) references tags,
  unique (article_id, tag_name)
);

create index articles_index on articles_to_tags(article_id);
create index tags_index on articles_to_tags using hash(tag_name);

-- Create a trigger to insert a tag into the tags table if it doesn't exist

CREATE FUNCTION record_new_tag() RETURNS TRIGGER AS $$
	BEGIN
		INSERT INTO tags (tag_name) VALUES (NEW.tag_name)
		ON CONFLICT DO NOTHING;
    RETURN NEW;
	END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER record_new_tag
    BEFORE INSERT ON articles_to_tags
    FOR EACH ROW EXECUTE FUNCTION record_new_tag();

-- Create triggers to clean up tags that have no articles
-- Whenver the on delete cascade deletes a row from articles_to_tags
-- we check if any of the delted tags are no longer in the articles_to_tags
-- table anymore and if so, we delete them from the tags table

CREATE FUNCTION delete_dangling_tags() RETURNS TRIGGER AS $$
	BEGIN
		DELETE FROM tags
		WHERE tags.tag_name in (
			SELECT old_table.tag_name from old_table
			LEFT OUTER JOIN articles_to_tags ON (old_table.tag_name = articles_to_tags.tag_name)
		);
		RETURN null;
	END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER clean_dangling_tags
    AFTER DELETE ON articles_to_tags
    REFERENCING OLD TABLE AS old_table
    FOR EACH STATEMENT EXECUTE FUNCTION delete_dangling_tags();

-- Create comments table
create table comments(
  id uuid default gen_random_uuid() primary key,
  body text,
  author_id uuid not null,
  foreign key (author_id) references users on delete cascade,
  article_id uuid not null,
  foreign key (article_id) references articles on delete cascade,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Create favorites table
create table favorites(
  user_id uuid not null,
  foreign key (user_id) references users on delete cascade,
  article_id uuid not null,
  foreign key (article_id) references articles on delete cascade,
  unique (user_id, article_id)
);
-- Create indexes so that we can find a users favorited articles
-- as well as all of the users that favorited an article
create index article_id_index on favorites(article_id);
create index user_id_index on favorites(user_id);
