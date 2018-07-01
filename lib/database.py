import datetime

from playhouse.pool import PooledPostgresqlDatabase, PooledMySQLDatabase, PooledSqliteDatabase
from playhouse.migrate import migrate, PostgresqlMigrator, SqliteMigrator, MySQLMigrator
from peewee import Model, TextField, DateTimeField, DatabaseError
from peewee import CharField, ForeignKeyField, IntegerField

from lib import config

try:
    engine, migrator_class = {
        "postgres": (PooledPostgresqlDatabase, PostgresqlMigrator),
        "mysql": (PooledMySQLDatabase, MySQLMigrator),
        "sqlite": (PooledSqliteDatabase, SqliteMigrator),
    }[config.get("db_engine", default="postgres")]
except KeyError:
    raise BaseException("Unknown database engine {}".format(config.get("db_engine")))

if engine == PooledSqliteDatabase:
    db = engine(config.get("db_name"))
else:
    db = engine(config.get("db_name"), user=config.get('db_user'), password=config.get("db_password"),
                host=config.get("db_host"), port=int(config.get("db_port")))


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
    app_version = CharField()
    os = TextField()
    wallet_type = CharField()
    exc_string = TextField()
    stack = TextField()
    description = TextField()
    locale = CharField(max_length=5, default="")
    python_version = CharField(default='')


class LogEntry(BaseModel):
    sender_ip = CharField()
    sent_at = DateTimeField(default=datetime.datetime.now)


def create_tables():
    db.create_tables([CrashKind, Crash, LogEntry], safe=True)

    # This will error if the column has already been added.
    try:
        migrator = migrator_class(db)
        migrate(
            migrator.add_column('crash', 'python_version', CharField(default='')),
        )
    except DatabaseError:
        pass
