from xpresso import Operation, Path, Router, status
from xpresso.routing.mount import Mount

from app.responses import empty_response, orjson_response
from app.routes import (
    article,
    articles,
    comments,
    feed,
    health,
    login,
    profile,
    tags,
    user,
    users,
)

api_routes = [
    Path(
        "/users",
        post=Operation(
            users.create_user,
            **orjson_response(status_code=status.HTTP_201_CREATED),
        ),
        tags=["users"],
    ),
    Path(
        "/user",
        get=Operation(user.get_user, **orjson_response()),
        put=Operation(user.update_user, **orjson_response()),
        tags=["users"],
    ),
    Path(
        "/users/login",
        post=Operation(login.login, **orjson_response()),
        tags=["login"],
    ),
    Path(
        "/profiles/{username}/follow",
        post=Operation(profile.follow_user, **orjson_response()),
        delete=Operation(profile.unfollow_user, **orjson_response()),
        tags=["profiles"],
    ),
    Path(
        "/profiles/{username}",
        get=Operation(profile.get_profile, **orjson_response()),
        tags=["profiles"],
    ),
    Path(
        "/articles",
        post=Operation(
            article.create_article,
            **orjson_response(status_code=status.HTTP_201_CREATED),
        ),
        get=Operation(articles.list_articles, **orjson_response()),
        tags=["articles"],
    ),
    Path(
        "/articles/feed",
        get=Operation(feed.get_user_feed, **orjson_response()),
        tags=["feed"],
    ),
    Path(
        "/articles/{slug}",
        delete=Operation(article.delete_article, **empty_response()),
        put=Operation(article.update_article, **orjson_response()),
        get=Operation(article.get_article, **orjson_response()),
        tags=["articles"],
    ),
    Path(
        "/articles/{slug}/favorite",
        post=Operation(article.favorite_article, **orjson_response()),
        delete=Operation(article.unfavorite_article, **orjson_response()),
        tags=["articles"],
    ),
    Path(
        "/articles/{slug}/comments",
        post=Operation(
            comments.create_comment,
            **orjson_response(status_code=status.HTTP_201_CREATED),
        ),
        get=Operation(comments.get_comments_for_article, **orjson_response()),
        tags=["articles"],
    ),
    Path(
        "/articles/{slug}/comments/{comment_id}",
        delete=Operation(comments.delete_comment, **empty_response()),
        tags=["articles"],
    ),
    Path(
        "/tags",
        get=Operation(tags.list_tags, **orjson_response()),
        tags=["tags"],
    ),
]

routes = [
    Path("/health", get=health.health, tags=["health"]),
    Mount("/api", app=Router(routes=api_routes)),
]
