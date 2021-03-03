from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()


class Sequence:
    def __init__(self, name: str):
        self.name = name
        bind = op.get_bind()
        self.session = Session(bind=bind)

    def upgrade(self):
        sql = sa.text(f"CREATE SEQUENCE {self.name};")
        self.session.execute(sql)

    def downgrade(self):
        sql = sa.text(f"DROP SEQUENCE {self.name};")
        self.session.execute(sql)


def remove_enum(name: str):
    bind = op.get_bind()
    session = Session(bind=bind)

    sql = sa.text(f"DROP TYPE {name};")
    session.execute(sql)
