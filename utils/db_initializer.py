from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import sql

class DatabaseInitializer:
    def __init__(self, db_manager, tables_config,constrains):
        self.db_manager = db_manager
        self.tables_config = tables_config
        self.constrains = constrains

    def create_database_if_not_exists(self):
        """Create the destination database if it doesn't exist."""
        self.db_manager.connect_to_default()

        self.db_manager.execute_query("SELECT 1 FROM pg_database WHERE datname = %s",
                                      [self.db_manager.db_config['DB_NAME']])
        exists = self.db_manager.cursor.fetchone()

        if not exists:
            try:
                self.db_manager.execute_query(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.db_manager.db_config['DB_NAME'])))
                print(f"Database {self.db_manager.db_config['DB_NAME']} created successfully.")
            except Exception as e:
                print(f"Error creating database: {e}")
            self.db_manager.disconnect()
            self.db_manager.connect()

            self.create_metadata_table()
            self.db_manager.commit()

            self. create_tables()
            self.db_manager.commit()

            self.add_foreign_key_constraints()
            self.db_manager.commit()


        else:
            print(f"Database {self.db_manager.db_config['DB_NAME']} already exists.")
            self.db_manager.disconnect()
            self.db_manager.connect()
    def create_metadata_table(self):
        """Create metadata table if it doesn't exist and insert initial data."""
        create_metadata_table_sql = '''
            CREATE TABLE IF NOT EXISTS meta_data (
                updated_at TIMESTAMP PRIMARY KEY
            );
        '''
        self.db_manager.create_table(create_metadata_table_sql)

        # Insert initial data
        creation_time = '2022-01-01 00:00:00'
        try:
            self.db_manager.execute_query(
                "INSERT INTO meta_data (updated_at) VALUES (%s);",
                (creation_time,)
            )
            print("Metadata table updated with initial creation time.")
        except Exception as e:
            print(f"Error inserting initial metadata: {e}")
    def create_tables(self):
        """Create necessary tables in the destination database."""
        self.db_manager.connect()
        for table_name, config in self.tables_config.items():
            try:
                print(f"Creating table {table_name}...")
                self.db_manager.create_table(config['create_table_sql'])
                print(f"Table {table_name} ensured to exist.")
            except Exception as e:
                print(f"Error creating table {table_name}: {e}")

    def add_foreign_key_constraints(self):
        """Add foreign key constraints to the tables."""

        for constraint in self.constrains:
            try:
                self.db_manager.execute_query(constraint)
                print("Foreign key constraint added successfully.")
            except Exception as e:
                print(f"Error adding foreign key constraint: {e}")
