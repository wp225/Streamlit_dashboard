from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import sql

class DataTransfer:
    def __init__(self, src_db, dest_db, tables_config):
        self.src_db = src_db
        self.dest_db = dest_db
        self.tables_config = tables_config
        self.last_update = None

    def get_last_update_time(self):
        """Get the last update time from the destination database."""
        query = "SELECT MAX(updated_at) FROM meta_data"
        self.dest_db.execute_query(query)
        result = self.dest_db.cursor.fetchone()
        self.last_update = result[0] if result and result[0] else '2020-09-19 00:00:00'  # Default if no previous updates
        print(self.last_update)

    def update_last_update_time(self):
        query = """
            INSERT INTO meta_data (updated_at)
            VALUES (NOW())
        """
        self.dest_db.execute_query(query)
        self.dest_db.commit()

    def transfer_table_data(self, table_name):
        """Transfer data for a specific table."""
        columns = self.tables_config[table_name]['columns']
        if columns:
            timestamp_col = self.tables_config[table_name]['timestamp_col']
            col_placeholder = ', '.join(['%s'] * len(columns))

            src_query = f"SELECT {', '.join(columns)} FROM {table_name} WHERE {timestamp_col} > %s"
            self.src_db.execute_query(src_query, (self.last_update,))
            rows = self.src_db.fetch_all()

            # Insert data into the destination
            if rows:
                dest_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({col_placeholder})"
                for row in rows:
                    try:
                        self.dest_db.execute_query(dest_query, row)
                    except Exception as e:
                        print(f"Error inserting data into {table_name}: {e}")
        else:
            print(f"No columns defined for table {table_name}.")

    def transfer_all_data(self):
        """Transfer data for all tables."""
        for table_name in self.tables_config:
            print(f'Transferring data to table: {table_name}')
            self.transfer_table_data(table_name)

        self.update_last_update_time()
