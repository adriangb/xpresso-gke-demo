from xpresso import Path, Router
from xpresso.routing.mount import Mount

from app.responses import create_json_operation
from app.routes import articles, follow, health, login, profile, user, users

api_routes = [
    Path("/users", post=create_json_operation(users.create_user)),
    Path("/user", get=user.get_user, put=user.update_user),
    Path("/users/login", post=login.login),
    Path("/profiles/{username}/follow", post=follow.follow_user),
    Path("/profiles/{username}/unfollow", post=follow.unfollow_user),
    Path("/profiles/{username}", get=profile.get_profile),
    Path("/articles", post=articles.create_article, get=articles.list_articles),
]

routes = [
    Path("/health", get=health.health),
    Mount("/api", app=Router(routes=api_routes)),
]
