import os
import json
from sqlalchemy import create_engine


def configure_mysql():
    config = json.loads(os.environ["CONFIG"])
    # mysql+pymysql://user:password@localhost/dbname
    engine = create_engine(config["db-credentials"])
    return engine
