class Test:
    @classmethod
    def extract(cls, foo: str) -> str:
        return foo


print(Test.extract("foo"))
