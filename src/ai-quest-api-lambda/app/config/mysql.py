import os
import json
from sqlalchemy import create_engine


def configure_mysql():
    DEBUG = int(os.environ["DEBUG"])
    config = json.loads(os.environ["CONFIG"])
    # mysql+pymysql://user:password@localhost/dbname
    engine = create_engine(config["db-credentials"], echo=(DEBUG == 1))
    return engine
