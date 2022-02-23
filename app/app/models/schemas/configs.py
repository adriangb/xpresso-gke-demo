from datetime import datetime

from pydantic import BaseConfig

from app.models.schemas.utils import (
    convert_datetime_to_realworld,
    convert_field_to_camel_case,
    convert_field_to_snake_case,
)


class ModelInResponseConfig(BaseConfig):
    allow_population_by_field_name = True
    json_encoders = {datetime: convert_datetime_to_realworld}
    alias_generator = convert_field_to_camel_case


class ModelInRequestConfig(BaseConfig):
    alias_generator = convert_field_to_snake_case
