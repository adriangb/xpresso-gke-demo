from xpresso import Operation, Path, Router, status
from xpresso.routing.mount import Mount

from app.responses import empty_response, orjson_response
from app.routes import (
    article,
    articles,
    follow,
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
            article.create_article,
            **orjson_response(status_code=status.HTTP_201_CREATED)
        ),
        get=Operation(articles.list_articles, **orjson_response()),
    ),
    Path(
        "/articles/feed",
        get=Operation(articles.get_user_feed, **orjson_response()),
    ),
    Path(
        "/articles/{slug}",
        delete=Operation(article.delete_article, **empty_response()),
        put=Operation(article.update_article, **orjson_response()),
        get=Operation(article.get_article, **orjson_response()),
    ),
    Path(
        "/articles/{slug}/favorite",
        post=Operation(article.favorite_article, **orjson_response()),
        delete=Operation(article.unfavorite_article, **orjson_response()),
    ),
    Path(
        "/tags",
        get=Operation(tags.list_tags, **orjson_response()),
    ),
]

routes = [
    Path("/health", get=health.health),
    Mount("/api", app=Router(routes=api_routes)),
]
