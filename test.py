from pydantic import BaseModel


def to_camel(string: str) -> str:
    return ''.join(word.capitalize() for word in string.split('_'))


class Inner(BaseModel):
    some_field: str

class Voice(BaseModel):
    inner: Inner

    class Config:
        alias_generator = to_camel


voice = Voice.parse_obj({"Inner": {"SomeField": "a"}})
print(voice.json())
#> tr-TR
print(voice.dict(by_alias=True))
#> {'Name': 'Filiz', 'LanguageCode': 'tr-TR'}