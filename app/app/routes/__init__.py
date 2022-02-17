from xpresso import Path, Router
from xpresso.routing.mount import Mount

from app.routes import articles, follow, health, login, profile, user, users

api_routes = [
    Path("/users", post=users.create_user_endpoint),
    Path("/user", get=user.get_user_endpoint, put=user.update_user_endpoint),
    Path("/users/login", post=login.login_endpoint),
    Path("/profiles/{username}/follow", post=follow.follow_user_endpoint),
    Path("/profiles/{username}/unfollow", post=follow.unfollow_user_endpoint),
    Path("/profiles/{username}", get=profile.get_profile_endpoint),
    Path("/articles", post=articles.create_article_endpoint),
]

routes = [
    Path("/health", get=health.health_endpoint),
    Mount("/api", app=Router(routes=api_routes)),
]
