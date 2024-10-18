import logging
from utils.db_manager import DatabaseManager
from utils.db_data_transfer import DataTransfer
from utils.db_initializer import DatabaseInitializer
from utils.config import src_db_config,dest_db_config,CONSTRAINTS,TABLES_CONFIG
def main():
    src_db = DatabaseManager(src_db_config).connect()
    dest_db = DatabaseManager(dest_db_config)

    initializer = DatabaseInitializer(dest_db, TABLES_CONFIG, CONSTRAINTS)
    initializer.create_database_if_not_exists()

    data_transfer = DataTransfer(src_db, dest_db, TABLES_CONFIG)
    data_transfer.get_last_update_time()
    data_transfer.transfer_all_data()
    dest_db.commit()

    src_db.disconnect()
    dest_db.disconnect()

if __name__ == '__main__':
    main()