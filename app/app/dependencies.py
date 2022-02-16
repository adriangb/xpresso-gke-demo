from typing import Annotated

import argon2
from xpresso import Depends

PasswordHasher = Annotated[
    argon2.PasswordHasher, Depends(lambda: argon2.PasswordHasher(), scope="app")
]
