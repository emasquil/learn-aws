from time import time
from fastapi.logger import logger

from app.core.config import config
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, String, MetaData, Integer

db_config = config["DB"]
db_string = f'postgres://{db_config["USER"]}:{db_config["PASSWORD"]}@{db_config["HOST"]}:{db_config["PORT"]}/{db_config["DATABASE"]}'

db = create_engine(db_string)
meta = MetaData(db)


prediction_table = Table(
    "predictions",
    meta,
    Column("image_id", String),
    Column("prediction", String),
    Column("timestamp", Integer),
)


def create_table():
    try:
        if not db.dialect.has_table(db, "predictions"):
            prediction_table.create()
            logger.info("Prediction table created")
        else:
            logger.info("Prediction table already exists")
            pass
    except Exception as e:
        logger.error(f"Error when trying to create/connect to the db {e}")


def insert_prediction(image_id: str, prediction: str):
    conn = None
    try:
        conn = db.connect()
        insert = prediction_table.insert().values(
            image_id=image_id, prediction=prediction, timestamp=int(time())
        )
        return conn.execute(insert)
    except Exception as e:
        logger.error(f"Error when inserting to the db {e}")
    finally:
        if conn is not None:
            conn.close()
