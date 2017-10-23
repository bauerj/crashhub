from peewee import Model, PostgresqlDatabase, TextField
from peewee import CharField, ForeignKeyField, IntegerField

from lib import config

db = PostgresqlDatabase(config.get("db_name"), user=config.get('db_user'), password=config.get("db_password"),
                        host=config.get("db_host"), port=config.get("db_port"))


class BaseModel(Model):
    class Meta:
        database = db


class CrashKind(BaseModel):
    file = TextField()
    name = CharField()
    type = CharField()
    github_id = IntegerField(default=-1)


class Crash(BaseModel):
    kind_id = ForeignKeyField(CrashKind)
    electrum_version = CharField()
    os = TextField()
    wallet_type = CharField()
    exc_string = TextField()
    stack = TextField()
    description = TextField()
    locale = CharField(max_length=5)


def create_tables():
    db.create_tables([CrashKind, Crash], safe=True)
