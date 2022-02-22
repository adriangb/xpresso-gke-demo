from xpresso import Operation, Path, Router, status
from xpresso.routing.mount import Mount

from app.responses import empty_response, orjson_response
from app.routes import articles, feed, follow, health, login, profile, user, users

api_routes = [
    Path(
        "/users",
        post=Operation(
            users.create_user, **orjson_response(status_code=status.HTTP_201_CREATED)
        ),
    ),
    Path(
        "/user",
        get=Operation(user.get_user, **orjson_response()),
        put=Operation(user.update_user, **orjson_response()),
    ),
    Path("/users/login", post=Operation(login.login, **orjson_response())),
    Path(
        "/profiles/{username}/follow",
        post=Operation(follow.follow_user, **orjson_response()),
    ),
    Path(
        "/profiles/{username}/unfollow",
        post=Operation(follow.unfollow_user, **orjson_response()),
    ),
    Path(
        "/profiles/{username}",
        get=Operation(profile.get_profile, **orjson_response()),
    ),
    Path(
        "/articles",
        post=Operation(
            articles.create_article,
            **orjson_response(status_code=status.HTTP_201_CREATED)
        ),
        get=Operation(articles.list_articles, **orjson_response()),
    ),
    Path(
        "/articles/feed",
        get=Operation(feed.get_user_feed, **orjson_response()),
    ),
    Path(
        "/articles/{slug}",
        delete=Operation(articles.delete_article, **empty_response()),
        put=Operation(articles.update_article, **orjson_response()),
        get=Operation(articles.get_article, **orjson_response()),
    ),
]

routes = [
    Path("/health", get=health.health),
    Mount("/api", app=Router(routes=api_routes)),
]
