from xpresso import Operation, Path, Router
from xpresso.responses import Response
from xpresso.routing.mount import Mount
from xpresso.routing.operation import Endpoint

from app.encoder import OrjsonPydanticOutEncoder
from app.routes import articles, follow, health, login, profile, user, users

encoder = OrjsonPydanticOutEncoder()


def _json_operation_factory(endpoint: Endpoint, status_code: int = 200) -> Operation:
    return Operation(
        endpoint,
        response_encoder=encoder,
        response_factory=lambda content: Response(content, status_code=status_code),
    )


api_routes = [
    Path("/users", post=_json_operation_factory(users.create_user)),
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
