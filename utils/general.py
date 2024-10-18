from typing import List

import pandas as pd
from sqlalchemy import create_engine, text

from utils.config import dest_db_config


def connect(conn_name: dict):
    src_engine = create_engine(
        f'postgresql://{conn_name["DB_USER"]}:{conn_name["DB_PASS"]}@{conn_name["DB_HOST"]}:{conn_name["DB_PORT"]}/{conn_name["DB_NAME"]}')
    return src_engine


def create_df(table_name: str, engine: str, cols: List[str], date_column, last_update) -> pd.DataFrame:
    columns_str = ", ".join(cols)
    query = f"SELECT {columns_str} FROM {table_name} WHERE {date_column} > '{last_update}'" #
    df = pd.read_sql(query, engine)
    return df


def get_last_update(engine: str):
    query = "SELECT last_update FROM metadata ORDER BY id DESC LIMIT 1"
    result = engine.execute(text(query), engine)
    return result

def update_metadata(session: str,new_timestamp):
    query = "INSERT INTO metadata (last_update) VALUES (:new_timestamp)"
    session.execute(text(query), {'new_timestamp': new_timestamp})
    session.commit()

