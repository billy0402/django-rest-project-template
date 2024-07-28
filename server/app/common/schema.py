from ninja import Schema


class HealthOut(Schema):
    status: bool


class VersionOut(Schema):
    version: int
