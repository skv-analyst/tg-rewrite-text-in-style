from datetime import datetime
from pony.orm import Database, Required, Optional
from src.paths import PATH_TO_DATA

# Creating a database object
db = Database()


class Request(db.Entity):
    _table_ = 'requests'
    user_id = Required(int)
    created = Required(datetime)
    style = Required(str)
    text = Required(str)
    model = Required(str)
    input_tokens = Required(int)
    output_tokens = Required(int)
    response = Optional(str)
    response_content = Optional(str)


# Connecting to the SQLite database
db.bind('sqlite', f'{PATH_TO_DATA}/database.sqlite', create_db=True)

# Generating tables in the database
db.generate_mapping(create_tables=True)
