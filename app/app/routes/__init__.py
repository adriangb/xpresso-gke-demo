from xpresso import Operation, Path, Router
from xpresso.routing.mount import Mount

from app.responses import orjson_response
from app.routes import articles, feed, follow, health, login, profile, user, users

api_routes = [
    Path("/users", post=Operation(users.create_user, **orjson_response())),
    Path(
        "/user", get=user.get_user, put=Operation(user.update_user, **orjson_response())
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
    Path("/profiles/{username}", get=profile.get_profile),
    Path(
        "/articles",
        post=Operation(articles.create_article, **orjson_response()),
        get=articles.list_articles,
    ),
    Path("/articles/feed", get=feed.get_user_feed),
    Path("/articles/{slug}", delete=articles.delete_article),
]

routes = [
    Path("/health", get=health.health),
    Mount("/api", app=Router(routes=api_routes)),
]
