# Creation, management, and invocation of change management scripts for a relational database.

## How to generate migration
from /backend/db directory:
```bash
alembic revision -m "your message" --autogenerate
```

## Managing of Sequences
I have some trouble like in [this issue](https://github.com/encode/orm/issues/21)

So, let's use bicycle:

__db/models/*.py__
```python
your_table_id_seq = sa.Sequence("app_your_table_id_seq")


class YourTable(Base):
    ...

    id = sa.Column(sa.Integer, primary_key=True, nullable=False,
                   server_default=your_table_id_seq.next_value())
    ...
```
After generating migration you should to change script:

__alembic/versions/*.py__
```python
...
from db.alembic.helpers import Sequence
your_table_id_seq = Sequence("app_your_table_id_seq")
...

def upgrade():
    your_table_id_seq.upgrade()
    ...

def downgrade():
    ...
    your_table_id_seq.downgrade()
```

# Remove Enum
You can you __alembic.helpers:remove_enum__ to downgrade Enum type.
```python
from db.alembic.helpers import remove_enum
remove_enum("yourenum")
```
