from ninja import Schema


class TokenObtainPairOutputSchema(Schema):
    access: str
    refresh: str
