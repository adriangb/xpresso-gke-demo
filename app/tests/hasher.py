from argon2 import PasswordHasher
from argon2.profiles import CHEAPEST

password_hasher = PasswordHasher.from_parameters(CHEAPEST)
