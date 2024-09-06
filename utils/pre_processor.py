from typing import List, Callable, Dict

import pandas as pd
from sqlalchemy import text

from utils.config import src_db_config, TABLES_CONFIG, dest_db_config
from utils.general import connect, create_df

# Connect to destination database and fetch the last update timestamp
dest_engine = connect(dest_db_config)
with dest_engine.connect() as dest_conn:
    last_update_query = text("SELECT last_update FROM metadata ORDER BY id DESC LIMIT 1")
    last_update_result = dest_conn.execute(last_update_query)
    last_update = last_update_result.scalar()
    print(last_update)

# Connect to the source database once
src_engine = connect(src_db_config)


def preprocess_table(table_name: str,
                     last_update: str,
                     date_columns: List[str] = ['created_at', 'updated_at', 'date_approved']
                     ) -> pd.DataFrame:
    """General function to preprocess a table and format the date column."""
    columns = TABLES_CONFIG.get(table_name, {}).get('columns', [])
    date_column = next((col for col in date_columns if col in columns), None)

    df = create_df(table_name, src_engine, columns, date_column, last_update)
    if date_column and date_column in df.columns:
        df[date_column] = df[date_column].dt.strftime('%Y/%m/%d')
    return df


def preprocess_user() -> pd.DataFrame:
    return preprocess_table('account_management_user', last_update=last_update)


def preprocess_referrals() -> pd.DataFrame:
    return preprocess_table('account_management_referraltransaction', last_update=last_update)


def preprocess_followers() -> pd.DataFrame:
    return preprocess_table('account_management_followerstransaction', last_update=last_update)


def preprocess_userfile() -> pd.DataFrame:
    return preprocess_table('file_management_userfile', last_update=last_update)


def preprocess_category() -> pd.DataFrame:
    return preprocess_table('file_management_category', last_update=last_update)


def preprocess_download() -> pd.DataFrame:
    return preprocess_table('file_management_filedownloadtransaction', last_update=last_update)


def preprocess_downloadhistory() -> pd.DataFrame:
    return preprocess_table('file_management_filedownloadhistorytransaction', last_update=last_update)


def process_countrywise_earning() -> pd.DataFrame:
    return preprocess_table('finance_management_countrywiseearning', last_update=last_update)


def process_userwallet() -> pd.DataFrame:
    return preprocess_table('finance_management_userwallet', last_update=last_update)


def process_withdraw_request() -> pd.DataFrame:
    return preprocess_table('finance_management_withdrawrequesttransaction', last_update=last_update)


def process_withdraw_method() -> pd.DataFrame:
    return preprocess_table('finance_management_withdrawmethod', last_update=last_update)


def process_subscriptions() -> pd.DataFrame:
    return preprocess_table('subscription_management_subscription', last_update=last_update)


def process_subscriptiontransactions() -> pd.DataFrame:
    return preprocess_table('subscription_management_subscription', last_update=last_update)

def process_viewtransaction():
    return preprocess_table('file_management_fileviewstransaction', last_update=last_update)

table_processors: Dict[str, Callable[[], pd.DataFrame]] = {
    'preprocess_user': preprocess_user,
    'preprocess_referrals': preprocess_referrals,
    'preprocess_followers': preprocess_followers,
    'preprocess_userfile': preprocess_userfile,
    'preprocess_category': preprocess_category,
    'preprocess_download': preprocess_download,
    'process_countrywise_earning': process_countrywise_earning,
    'process_userwallet': process_userwallet,
    'process_withdraw_request': process_withdraw_request,
    'process_withdraw_method': process_withdraw_method,
    'process_downloadhistory': preprocess_downloadhistory,
    'process_subscriptions': process_subscriptions,
    'process_subscriptiontransactions': process_subscriptiontransactions,
    'process_viewtransaction': process_viewtransaction,
}

if __name__ == '__main__':
    print("Testing preprocess functions...\n")
    (process_userwallet())

    # for func_name, func in table_processors.items():
    #     try:
    #         df = func()
    #         print(f"{func_name}:\n{df.head()}\n")
    #     except Exception as e:
    #         print(f"Error testing {func_name}: {e}")
