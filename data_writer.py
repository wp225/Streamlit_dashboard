from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

import sys
from utils.general import connect
from create_db import (
    AccountManagementUser,
    AccountManagementFollowersTransaction,
    AccountManagementReferralTransaction,
    FileManagementCategory,
    FileManagementUserFile,
    FileManagementFileDownloadTransaction,
    FinanceManagementCountryWiseEarning,
    FinanceManagementWithdrawMethod,
    FinanceManagementWithdrawRequestTransaction,
    FinanceManagementUserWallet,
    MetaData,
    FileManagementFileDownloadHistoryTransaction,
    SubscriptionManagementSubscription,
    SubscriptionManagementSubscriptionTransaction,
    FileManagementFileViewTransaction
)
from utils.pre_processor import (
    preprocess_category,
    preprocess_download,
    preprocess_followers,
    preprocess_referrals,
    preprocess_user,
    preprocess_userfile,
    process_countrywise_earning,
    process_userwallet,
    process_withdraw_method,
    process_withdraw_request,
    preprocess_downloadhistory,
    process_subscriptions,
    process_subscriptiontransactions,
    process_viewtransaction

)
from utils.config import dest_db_config
from utils.general import update_metadata

new_db_engine = connect(dest_db_config)
Session = sessionmaker(bind=new_db_engine)

def batch_insert(session, model, data):
    """Batch insert using SQLAlchemy's bulk_insert_mappings for performance."""
    try:
        data_dicts = data.to_dict(orient='records')
        session.bulk_insert_mappings(model, data_dicts)
        session.commit()
        print(f"Data inserted into {model.__tablename__} successfully.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error inserting data into {model.__tablename__}: {e}", file=sys.stderr)

def populate_database():
    session = Session()
    try:
        data_processors = {
            AccountManagementUser: preprocess_user,
            FinanceManagementUserWallet: process_userwallet,
            AccountManagementReferralTransaction: preprocess_referrals,
            AccountManagementFollowersTransaction: preprocess_followers,
            FileManagementUserFile: preprocess_userfile,
            FileManagementCategory: preprocess_category,
            FileManagementFileDownloadTransaction: preprocess_download,
            FinanceManagementCountryWiseEarning: process_countrywise_earning,
            FinanceManagementWithdrawMethod: process_withdraw_method,
            FinanceManagementWithdrawRequestTransaction: process_withdraw_request,
            FileManagementFileDownloadHistoryTransaction: preprocess_downloadhistory,
            SubscriptionManagementSubscriptionTransaction: process_subscriptiontransactions,
            SubscriptionManagementSubscription: process_subscriptions,
            FileManagementFileViewTransaction: process_viewtransaction()
        }

        for model, processor in data_processors.items():
            data = processor()
            batch_insert(session, model, data)
            update_metadata(session,datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
    finally:
        update_metadata(session, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        session.close()

if __name__ == "__main__":
    populate_database()
