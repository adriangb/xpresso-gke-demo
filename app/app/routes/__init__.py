from app.routes import health, login, user, users
from xpresso import Router
from xpresso.routing.mount import Mount

api_routes = [
    users.path_item,
    user.path_item,
    login.path_item,
]

api = Mount("/api", app=Router(routes=api_routes))

routes = [
    health.health_pathitem,
    api,
]
