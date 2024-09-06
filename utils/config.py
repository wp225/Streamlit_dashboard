import os
from dotenv import load_dotenv

load_dotenv()

src_db_config = {
    'DB_TYPE': os.getenv('SRC_DB_TYPE'),
    'DB_HOST': os.getenv('SRC_DB_HOST'),
    'DB_NAME': os.getenv('SRC_DB_NAME'),
    'DB_USER': os.getenv('SRC_DB_USER'),
    'DB_PASS': os.getenv('SRC_DB_PASS'),
    'DB_PORT': os.getenv('SRC_DB_PORT')
}

dest_db_config = {
    'DB_TYPE': os.getenv('DEST_DB_TYPE'),
    'DB_HOST': os.getenv('DEST_DB_HOST'),
    'DB_NAME': os.getenv('DEST_DB_NAME'),
    'DB_USER': os.getenv('DEST_DB_USER'),
    'DB_PASS': os.getenv('DEST_DB_PASS'),
    'DB_PORT': os.getenv('DEST_DB_PORT')
}

TABLES_CONFIG = {
    'account_management_user': {
        'columns': ['id', 'username', 'country', 'is_email_confirmed', 'created_at','last_login']
    },
    'account_management_referraltransaction': {
        'columns': ['id', 'referred_by_id', 'created_at']
    },
    'account_management_followerstransaction': {
        'columns': ['id', 'followed_by_id', 'updated_at']
    },
    'file_management_userfile': {
        'columns': ['id', 'user_id', 'category_id_id', 'created_at']
    },
    'file_management_category': {
        'columns': ['id', 'category_name','updated_at']
    },
    'file_management_filedownloadtransaction': {
        'columns': ['id', 'file_id', 'country_name','counted', 'created_at', 'browser_name', 'device_name']
    },
    'file_management_filedownloadhistorytransaction': {
        'columns': ['id', 'file_id', 'created_at']
    },
    'finance_management_countrywiseearning': {
        'columns': ['id', 'country_name', 'earning_rate', 'updated_at']
    },
    'finance_management_userwallet': {
        'columns': ['id', 'user_id', 'total_balance', 'paid_balance', 'updated_at']
    },
    'finance_management_withdrawrequesttransaction': {
        'columns': ['id', 'user_id', 'withdraw_method_id', 'amount','date_approved']
    },
    'finance_management_withdrawmethod': {
        'columns': ['id', 'method_name','created_at']
    },
    'subscription_management_subscription': {
        'columns': ['id', 'subscription_name','updated_at']
    },
    'subscription_management_subscriptiontransaction': {
        'columns': ['id','updated_at','subscription_id', 'user_id','is_active']},

    'file_management_fileviewstransaction': {
        'columns': ['id','created_at','file_id']}

}




