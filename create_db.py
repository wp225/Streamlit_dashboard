import logging

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, DECIMAL, MetaData, text, \
    inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship, declarative_base

from utils.config import dest_db_config

metadata = MetaData()
Base = declarative_base(metadata=metadata)


def create_database_if_not_exist():
    """
    Function to create a database if it doesn't exist and by default store a value in the metadata table.
    :return: A database
    """
    conn = dest_db_config
    db_url = f'postgresql://{conn["DB_USER"]}:{conn["DB_PASS"]}@{conn["DB_HOST"]}:{conn["DB_PORT"]}/postgres'

    try:
        default_engine = create_engine(db_url, isolation_level='AUTOCOMMIT')

        with default_engine.connect() as connection:
            result = connection.execute(text(f"SELECT 1 FROM pg_database WHERE datname = :dbname"),
                                        {'dbname': conn['DB_NAME']})
            if result.scalar() is None:
                logging.info('Database does not exist. Creating database.')
                connection.execute(text(f"CREATE DATABASE {conn['DB_NAME']}"))
                logging.info(f"Database {conn['DB_NAME']} created successfully")
            else:
                logging.info(f"Database {conn['DB_NAME']} already exists. Skipping creation.")

    except SQLAlchemyError as e:
        logging.error(f"Error occurred while creating database: {e}")
        raise

    # Check if tables exist and if they don't, then create tables and add initial value to the metadata table
    try:
        updated_db_url = f'postgresql://{conn["DB_USER"]}:{conn["DB_PASS"]}@{conn["DB_HOST"]}:{conn["DB_PORT"]}/{conn["DB_NAME"]}'
        engine = create_engine(updated_db_url, isolation_level='AUTOCOMMIT')
        inspector = inspect(engine)

        existing_tables = inspector.get_table_names()

        if not existing_tables:
            logging.info("No tables found. Creating tables.")
            Base.metadata.create_all(engine)
            logging.info("Tables created successfully")
            try:
                with engine.connect() as connection:
                    connection.execute(
                        text("INSERT INTO metadata (last_update) VALUES ('1970-01-01 00:00:00') ON CONFLICT DO NOTHING")
                    )

            except SQLAlchemyError as e:
                logging.error(f"Error inserting initial timestamp: {e}")
                raise
        else:
            logging.info("Tables already exist. Skipping creation.")

    except SQLAlchemyError as e:
        logging.error(f"Error occurred while inspecting or creating tables: {e}")
        raise


# Define Database schema and their relations
class AccountManagementUser(Base):
    __tablename__ = 'account_management_user'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    country = Column(String)
    is_email_confirmed = Column(Boolean)
    created_at = Column(DateTime)
    last_login = Column(DateTime)


class AccountManagementFollowersTransaction(Base):
    __tablename__ = 'account_management_followerstransaction'

    id = Column(Integer, primary_key=True)
    followed_by_id = Column(Integer, ForeignKey('account_management_user.id'))
    updated_at = Column(DateTime)

    followed_by = relationship('AccountManagementUser', backref='followers')


class AccountManagementReferralTransaction(Base):
    __tablename__ = 'account_management_referraltransaction'

    id = Column(Integer, primary_key=True)
    referred_by_id = Column(Integer, ForeignKey('account_management_user.id'))
    created_at = Column(DateTime)

    referred_by = relationship('AccountManagementUser', backref='referrals')


class FileManagementCategory(Base):
    __tablename__ = 'file_management_category'

    id = Column(Integer, primary_key=True)
    category_name = Column(String)
    updated_at = Column(DateTime)


class FileManagementUserFile(Base):
    __tablename__ = 'file_management_userfile'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('account_management_user.id'))
    category_id_id = Column(Integer)
    created_at = Column(DateTime)

    user = relationship('AccountManagementUser', backref='userfiles')


class FileManagementFileDownloadTransaction(Base):
    __tablename__ = 'file_management_filedownloadtransaction'

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('file_management_userfile.id'))
    counted = Column(Boolean)
    browser_name = Column(String)
    device_name = Column(String)
    created_at = Column(DateTime)
    country_name = Column(String)

    file = relationship('FileManagementUserFile', backref='downloads')


class FileManagementFileDownloadHistoryTransaction(Base):
    __tablename__ = 'file_management_filedownloadhistorytransaction'
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('file_management_userfile.id'))
    created_at = Column(DateTime)

    file = relationship('FileManagementUserFile', backref='download_history')


class FinanceManagementCountryWiseEarning(Base):
    __tablename__ = 'finance_management_countrywiseearning'

    id = Column(Integer, primary_key=True)
    country_name = Column(String)
    earning_rate = Column(DECIMAL(10, 2))
    updated_at = Column(DateTime)


class FinanceManagementWithdrawMethod(Base):
    __tablename__ = 'finance_management_withdrawmethod'

    id = Column(Integer, primary_key=True)
    method_name = Column(String)
    created_at = Column(DateTime)


class FinanceManagementWithdrawRequestTransaction(Base):
    __tablename__ = 'finance_management_withdrawrequesttransaction'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('account_management_user.id'))
    withdraw_method_id = Column(Integer, ForeignKey('finance_management_withdrawmethod.id'))
    amount = Column(DECIMAL(10, 2))
    date_approved = Column(DateTime)

    user = relationship('AccountManagementUser', backref='withdraw_requests')
    withdraw_method = relationship('FinanceManagementWithdrawMethod', backref='requests')


class FinanceManagementUserWallet(Base):
    __tablename__ = 'finance_management_userwallet'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('account_management_user.id'))
    total_balance = Column(DECIMAL(10, 2))
    paid_balance = Column(DECIMAL(10, 2))
    updated_at = Column(DateTime)

    user = relationship('AccountManagementUser', backref='wallet')

class SubscriptionManagementSubscription(Base):
    __tablename__ = 'subscription_management_subscription'

    id = Column(Integer, primary_key=True)
    subscription_name = Column(String(255), nullable=False)
    updated_at = Column(DateTime)


class SubscriptionManagementSubscriptionTransaction(Base):
    __tablename__ = 'subscription_management_subscriptiontransaction'

    id = Column(Integer, primary_key=True)
    updated_at = Column(DateTime)
    subscription_id = Column(Integer, ForeignKey('subscription_management_subscription.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('account_management_user.id'), nullable=False)
    is_active = Column(Boolean)
    subscription = relationship('SubscriptionManagementSubscription', backref='subscription_transactions')
    user = relationship('AccountManagementUser', backref='subscription_transactions')


class FileManagementFileViewTransaction(Base):
    __tablename__ = 'file_management_fileviewstransaction'

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('file_management_userfile.id'))
    created_at = Column(DateTime)

    file = relationship('FileManagementUserFile', backref='views')

class MetaData(Base):
    __tablename__ = 'metadata'

    id = Column(Integer, primary_key=True)
    last_update = Column(DateTime)


if __name__ == '__main__':
    create_database_if_not_exist()
