from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import sql
class DatabaseManager:
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establish a connection to the database."""
        try:
            self.connection = psycopg2.connect(
                host=self.db_config['DB_HOST'],
                database=self.db_config['DB_NAME'],
                user=self.db_config['DB_USER'],
                password=self.db_config['DB_PASS'],
                port=self.db_config['DB_PORT']
            )
            self.cursor = self.connection.cursor()
            print(f"Connected to database: {self.db_config['DB_NAME']}")
            return self
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    def connect_to_default(self):
        """Connect to the default 'postgres' database to create the destination DB if necessary."""
        try:
            self.connection = psycopg2.connect(
                host=self.db_config['DB_HOST'],
                database='postgres',  # Connect to the default 'postgres' DB
                user=self.db_config['DB_USER'],
                password=self.db_config['DB_PASS'],
                port=self.db_config['DB_PORT']
            )
            self.connection.autocommit = True  # Enable autocommit for creating a new database
            self.cursor = self.connection.cursor()
            print("Connected to default database 'postgres'")
            return self
        except Exception as e:
            print(f"Error connecting to default database: {e}")
            raise

    def disconnect(self):
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    def execute_query(self, query, params=None):
        """Execute a SQL query with optional parameters."""
        try:
            self.cursor.execute(query, params)
        except Exception as e:
            print(f"Error executing query: {e}")
            raise

    def fetch_all(self):
        """Fetch all results from the last executed query."""
        return self.cursor.fetchall()

    def commit(self):
        """Commit the current transaction."""
        self.connection.commit()

    def create_table(self, create_table_sql):
        """Create a table in the database."""
        self.execute_query(create_table_sql)
