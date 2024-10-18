from dotenv import load_dotenv
import os

load_dotenv()

TABLES_CONFIG = {
    'account_management_user': {
        'columns': ['id', 'username', 'country', 'is_email_confirmed', 'created_at', 'last_login'],
        'timestamp_col': 'created_at',
        'create_table_sql': '''
                CREATE TABLE IF NOT EXISTS account_management_user (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255),
                    country VARCHAR(100),
                    is_email_confirmed BOOLEAN,
                    created_at TIMESTAMP,
                    last_login TIMESTAMP
                );
            '''
    },  # created_at
    'account_management_referraltransaction': {
        'columns': ['id', 'referred_by_id', 'created_at'],
        'timestamp_col': 'created_at',
        'create_table_sql': '''
                CREATE TABLE IF NOT EXISTS account_management_referraltransaction (
                    id SERIAL PRIMARY KEY,
                    referred_by_id INT,
                    created_at TIMESTAMP
                );
            '''
    },  # created_at
    'account_management_followerstransaction': {
        'columns': ['id', 'followed_by_id', 'created_at'],
        'timestamp_col': 'created_at',
        'create_table_sql': '''
                CREATE TABLE IF NOT EXISTS account_management_followerstransaction (
                    id SERIAL PRIMARY KEY,
                    followed_by_id INT,
                    created_at TIMESTAMP
                );
            '''
    },  # created_at
    'file_management_userfile': {
        'columns': ['id', 'user_id', 'category_id_id', 'created_at'],
        'timestamp_col': 'created_at',
        'create_table_sql': '''
                CREATE TABLE IF NOT EXISTS file_management_userfile (
                    id SERIAL PRIMARY KEY,
                    user_id INT,
                    category_id_id INT,
                    created_at TIMESTAMP
                );
            '''
    },  # created_at
    'file_management_category': {
        'columns': ['id', 'category_name', 'created_at'],
        'timestamp_col': 'updated_at',
        'create_table_sql': '''
                CREATE TABLE IF NOT EXISTS file_management_category (
                    id SERIAL PRIMARY KEY,
                    category_name VARCHAR(255),
                    created_at TIMESTAMP
                );
            '''
    },  # created at
    'file_management_filedownloadtransaction': {
        'columns': ['id', 'file_id', 'country_name', 'counted', 'created_at', 'browser_name', 'device_name'],
        'timestamp_col': 'created_at',
        'create_table_sql': '''
                CREATE TABLE IF NOT EXISTS file_management_filedownloadtransaction (
                    id SERIAL PRIMARY KEY,
                    file_id INT,
                    country_name VARCHAR(100),
                    counted BOOL,
                    created_at TIMESTAMP,
                    browser_name VARCHAR(100),
                    device_name VARCHAR(100)
                );
            '''
    },  # created_at
    'file_management_filedownloadhistorytransaction': {
        'columns': ['id', 'file_id', 'created_at'],
        'timestamp_col': 'created_at',
        'create_table_sql': '''
                CREATE TABLE IF NOT EXISTS file_management_filedownloadhistorytransaction (
                    id SERIAL PRIMARY KEY,
                    file_id INT,
                    created_at TIMESTAMP
                );
            '''
    },  # created_at
    'finance_management_countrywiseearning': {
        'columns': ['id', 'country_name', 'earning_rate', 'updated_at'],
        'timestamp_col': 'updated_at',
        'create_table_sql': '''
                CREATE TABLE IF NOT EXISTS finance_management_countrywiseearning (
                    id SERIAL PRIMARY KEY,
                    country_name VARCHAR(100),
                    earning_rate DECIMAL,
                    updated_at TIMESTAMP
                );
            '''
    },  # updated_at
    'finance_management_userwallet': {
        'columns': ['id', 'user_id', 'total_balance', 'paid_balance', 'updated_at'],
        'timestamp_col': 'updated_at',
        'create_table_sql': '''
                CREATE TABLE IF NOT EXISTS finance_management_userwallet (
                    id SERIAL PRIMARY KEY,
                    user_id INT,
                    total_balance DECIMAL,
                    paid_balance DECIMAL,
                    updated_at TIMESTAMP
                );
            '''
    },  # updated_at
    'finance_management_withdrawmethod': {
        'columns': ['id', 'method_name', 'created_at'],
        'timestamp_col': 'created_at',
        'create_table_sql': '''
            CREATE TABLE IF NOT EXISTS finance_management_withdrawmethod (
                id SERIAL PRIMARY KEY,
                method_name VARCHAR(255),
                created_at TIMESTAMP
            );
        '''
    },
    'finance_management_withdrawrequesttransaction': {
        'columns': ['id', 'user_id', 'withdraw_method_id', 'amount', 'date_approved'],
        'timestamp_col': 'date_approved',
        'create_table_sql': '''
                CREATE TABLE IF NOT EXISTS finance_management_withdrawrequesttransaction (
                    id SERIAL PRIMARY KEY,
                    user_id INT,
                    withdraw_method_id INT,
                    amount DECIMAL,
                    date_approved TIMESTAMP
                );
            '''
    },  # date_approved
    'subscription_management_subscriptionplan': {
        'columns': ['id', 'subscription_name', 'created_at', 'is_active'],
        'timestamp_col': 'created_at',
        'create_table_sql': '''
                CREATE TABLE IF NOT EXISTS subscription_management_subscriptionplan (
                    id SERIAL PRIMARY KEY,
                    subscription_name VARCHAR(255),
                    created_at TIMESTAMP,
                    is_active BOOLEAN
                );
            '''
    },  # created_at
    'subscription_management_subscriptiontransaction': {
        'columns': ['id', 'updated_at', 'subscription_plan_id', 'user_id', 'status'],
        'timestamp_col': 'updated_at',
        'create_table_sql': '''
                CREATE TABLE IF NOT EXISTS subscription_management_subscriptiontransaction (
                    id SERIAL PRIMARY KEY,
                    updated_at TIMESTAMP,
                    subscription_plan_id INT,
                    user_id INT,
                    status VARCHAR(255)
                );
            '''
    },  # updated_at
    'file_management_fileviewstransaction': {
        'columns': ['id', 'created_at', 'file_id'],
        'timestamp_col': 'created_at',
        'create_table_sql': '''
                CREATE TABLE IF NOT EXISTS file_management_fileviewstransaction (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP,
                    file_id INT
                );
            '''
    }  # created_at
}
CONSTRAINTS = [
    '''
    ALTER TABLE IF EXISTS public.file_management_fileviewstransaction
        ADD CONSTRAINT file_management_fileviewstransaction_file_id_fkey FOREIGN KEY (file_id)
        REFERENCES public.file_management_userfile (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION;
    ''',
    '''
    ALTER TABLE IF EXISTS public.file_management_userfile
        ADD CONSTRAINT file_management_userfile_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.account_management_user (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION;
    ''',
    '''
    ALTER TABLE IF EXISTS public.account_management_followerstransaction
        ADD CONSTRAINT account_management_followerstransaction_followed_by_id_fkey FOREIGN KEY (followed_by_id)
        REFERENCES public.account_management_user (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION;
    ''',
    '''
    ALTER TABLE IF EXISTS public.account_management_referraltransaction
        ADD CONSTRAINT account_management_referraltransaction_referred_by_id_fkey FOREIGN KEY (referred_by_id)
        REFERENCES public.account_management_user (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION;
    ''',
    '''
    ALTER TABLE IF EXISTS public.finance_management_withdrawrequesttransaction
        ADD CONSTRAINT finance_management_withdrawrequesttransaction_withdraw_method_id_fkey FOREIGN KEY (withdraw_method_id)
        REFERENCES public.finance_management_withdrawmethod (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION;
    ''',
    '''
    ALTER TABLE IF EXISTS public.finance_management_withdrawrequesttransaction
        ADD CONSTRAINT finance_management_withdrawrequesttransaction_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.account_management_user (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION;
    ''',
    '''
    ALTER TABLE IF EXISTS public.finance_management_userwallet
        ADD CONSTRAINT finance_management_userwallet_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.account_management_user (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION;
    ''',
    '''
    ALTER TABLE IF EXISTS public.subscription_management_subscriptiontransaction
        ADD CONSTRAINT subscription_management_subscriptiontransaction_subscription_id_fkey FOREIGN KEY (subscription_plan_id)
        REFERENCES public.subscription_management_subscriptionplan (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION;
    ''',
    '''
    ALTER TABLE IF EXISTS public.subscription_management_subscriptiontransaction
        ADD CONSTRAINT subscription_management_subscriptiontransaction_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.account_management_user (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION;
    ''',
    '''
    ALTER TABLE IF EXISTS public.file_management_filedownloadtransaction
        ADD CONSTRAINT file_management_filedownloadtransaction_file_id_fkey FOREIGN KEY (file_id)
        REFERENCES public.file_management_userfile (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION;
    ''',
    '''
    ALTER TABLE IF EXISTS public.file_management_filedownloadhistorytransaction
        ADD CONSTRAINT file_management_filedownloadhistorytransaction_file_id_fkey FOREIGN KEY (file_id)
        REFERENCES public.file_management_userfile (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION;
    '''
]

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



