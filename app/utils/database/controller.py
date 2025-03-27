import sqlite3
import mysql.connector
import psycopg2
import logging

logger = logging.getLogger(__name__)


class DatabaseController:
    def __init__(self, config):
        self.config = config
        self.conn = None
        self.connect()

    def connect(self):
        try:
            if self.config['type'] == 'SQLite':
                self.conn = sqlite3.connect(self.config['path'])
                self.conn.row_factory = sqlite3.Row
            elif self.config['type'] == 'MySQL':
                self.conn = mysql.connector.connect(
                    host=self.config["host"],
                    user=self.config["user"],
                    password=self.config["password"],
                    database=self.config["dbname"],
                    auth_plugin="mysql_native_password"
                )
            elif self.config['type'] == 'PostgreSQL':
                self.conn = psycopg2.connect(
                    host=self.config.get("host", "localhost"),
                    user=self.config["user"],
                    password=self.config["password"],
                    dbname=self.config["dbname"]
                )
            else:
                raise ValueError(f"Unsupported database type: {self.config['type']}")

            logger.info(f"Connected to {self.config['type']} database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise

    def create_table(self, table_name, columns, initial_rows=0):
        try:
            cursor = self.conn.cursor()
            if self.config['type'] == 'SQLite':
                columns_sql = ', '.join([f'"{name}" {type}' for name, type in columns])
                cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_sql})')
            elif self.config['type'] in ['MySQL', 'PostgreSQL']:
                columns_sql = ', '.join([f'{name} {type}' for name, type in columns])
                cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})')

            # Insert initial rows if specified
            if initial_rows > 0:
                placeholders = ', '.join(
                    ['%s' if self.config['type'] in ['MySQL', 'PostgreSQL'] else '?' for _ in columns])
                insert_sql = f'INSERT INTO {table_name} VALUES ({placeholders})'
                default_values = ['' if 'TEXT' in col[1].upper() else 0 for col in columns]

                for _ in range(initial_rows):
                    cursor.execute(insert_sql, default_values)

            self.conn.commit()
            logger.info(f"Table '{table_name}' created successfully with {initial_rows} initial rows")
        except Exception as e:
            logger.error(f"Failed to create table: {str(e)}")
            raise

    def get_tables(self):
        try:
            cursor = self.conn.cursor()
            if self.config['type'] == 'SQLite':
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            elif self.config['type'] == 'MySQL':
                cursor.execute("SHOW TABLES")
            elif self.config['type'] == 'PostgreSQL':
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")

            tables = [row[0] for row in cursor.fetchall()]
            logger.info(f"Retrieved tables: {tables}")
            return tables
        except Exception as e:
            logger.error(f"Failed to get tables: {str(e)}")
            raise

    def get_table_data(self, table_name):
        try:
            cursor = self.conn.cursor()
            if self.config['type'] == 'SQLite':
                cursor.execute(f"PRAGMA table_info('{table_name}')")
                columns = [info[1] for info in cursor.fetchall()]
            elif self.config['type'] in ['MySQL', 'PostgreSQL']:
                cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}'")
                columns = [col[0] for col in cursor.fetchall()]

            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()

            return columns, [dict(zip(columns, row)) for row in data]
        except Exception as e:
            logger.error(f"Failed to get table data: {str(e)}")
            raise

    def update_record(self, table_name, primary_key_col, primary_key_value, column_name, new_value):
        try:
            cursor = self.conn.cursor()

            if self.config['type'] == 'SQLite':
                query = f'UPDATE "{table_name}" SET "{column_name}" = ? WHERE "{primary_key_col}" = ?'
                params = (new_value, primary_key_value)
            else:
                query = f'UPDATE {table_name} SET {column_name} = %s WHERE {primary_key_col} = %s'
                params = (new_value, primary_key_value)

            cursor.execute(query, params)
            self.conn.commit()

            logger.info(f"Updated record in table '{table_name}' where '{primary_key_col}'={primary_key_value}")
        except Exception as e:
            logger.error(f"Failed to update record: {str(e)}")
            raise

    def commit(self):
        try:
            self.conn.commit()
            logger.info("Changes committed to database")
        except Exception as e:
            logger.error(f"Failed to commit changes: {str(e)}")
            raise

    def close(self):
        if self.conn:
            self.conn.close()
