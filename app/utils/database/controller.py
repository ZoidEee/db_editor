import sqlite3
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
            else:
                raise ValueError(f"Unsupported database type: {self.config['type']}")

            logger.info(f"Connected to {self.config['type']} database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise

    def create_table(self, table_name, columns, initial_rows=0):
        try:
            cursor = self.conn.cursor()
            columns_sql = ', '.join([f'"{name}" {type}' for name, type in columns])
            cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_sql})')

            # Insert initial rows if specified
            if initial_rows > 0:
                placeholders = ', '.join(['?' for _ in columns])
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
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

            tables = [row[0] for row in cursor.fetchall()]
            logger.info(f"Retrieved tables: {tables}")
            return tables
        except Exception as e:
            logger.error(f"Failed to get tables: {str(e)}")
            raise

    def get_table_data(self, table_name):
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            columns = [info[1] for info in cursor.fetchall()]

            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()

            return columns, [dict(zip(columns, row)) for row in data]
        except Exception as e:
            logger.error(f"Failed to get table data: {str(e)}")
            raise

    def update_record(self, table_name, primary_key_col, primary_key_value, column_name, new_value):
        try:
            cursor = self.conn.cursor()
            query = f'UPDATE "{table_name}" SET "{column_name}" = ? WHERE "{primary_key_col}" = ?'
            params = (new_value, primary_key_value)

            cursor.execute(query, params)
            self.conn.commit()

            logger.info(f"Updated record in table '{table_name}' where '{primary_key_col}'={primary_key_value}")
        except Exception as e:
            logger.error(f"Failed to update record: {str(e)}")
            raise

    def add_column(self, table_name, column_name, column_type):
        try:
            with self.conn:
                self.conn.execute(
                    f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {column_type}'
                )
            logger.info(f"Added column {column_name} to {table_name}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Add column failed: {str(e)}")
            return False

    def optimize(self):
        try:
            with self.conn:
                self.conn.execute('VACUUM')
                self.conn.execute('PRAGMA optimize')
            logger.info("Database optimized")
            return True
        except sqlite3.Error as e:
            logger.error(f"Optimization failed: {str(e)}")
            return False

    def drop_table(self, table_name):
        try:
            with self.conn:
                self.conn.execute(f'DROP TABLE IF EXISTS "{table_name}"')
            logger.info(f"Dropped table {table_name}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Table deletion failed: {str(e)}")
            return False

    def rename_table(self, old_name, new_name):
        try:
            with self.conn:
                self.conn.execute(f'ALTER TABLE "{old_name}" RENAME TO "{new_name}"')
            return True
        except sqlite3.Error as e:
            logger.error(f"Rename table failed: {str(e)}")
            return False

    def remove_column(self, table_name, column_name):
        try:
            with self.conn:
                # SQLite doesn't support DROP COLUMN directly
                cols = [col for col in self.get_schema(table_name) if col['name'] != column_name]
                cols_sql = ', '.join([f'"{col["name"]}" {col["type"]}' for col in cols])

                self.conn.execute(f'ALTER TABLE "{table_name}" RENAME TO temp_table')
                self.conn.execute(f'CREATE TABLE "{table_name}" ({cols_sql})')
                self.conn.execute(
                    f'INSERT INTO "{table_name}" SELECT {",".join([col["name"] for col in cols])} FROM temp_table')
                self.conn.execute('DROP TABLE temp_table')
            return True
        except sqlite3.Error as e:
            logger.error(f"Remove column failed: {str(e)}")
            return False

    def rename_column(self, table_name, old_name, new_name):
        try:
            with self.conn:
                # SQLite doesn't support RENAME COLUMN directly
                schema = self.get_schema(table_name)
                cols_sql = ', '.join([
                    f'"{col["name"] if col["name"] != old_name else new_name}" {col["type"]}'
                    for col in schema
                ])

                self.conn.execute(f'ALTER TABLE "{table_name}" RENAME TO temp_table')
                self.conn.execute(f'CREATE TABLE "{table_name}" ({cols_sql})')
                self.conn.execute(f'INSERT INTO "{table_name}" SELECT * FROM temp_table')
                self.conn.execute('DROP TABLE temp_table')
            return True
        except sqlite3.Error as e:
            logger.error(f"Rename column failed: {str(e)}")
            return False

    def get_schema(self, table_name):
        try:
            cursor = self.conn.execute(f'PRAGMA table_info("{table_name}")')
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Get schema failed: {str(e)}")
            return []

    def batch_insert(self, table_name, data):
        try:
            with self.conn:
                columns = self.get_schema(table_name)
                col_names = [col['name'] for col in columns if col['name'].lower() != 'id']
                placeholders = ', '.join(['?' for _ in col_names])
                insert_sql = f'INSERT INTO "{table_name}" ({", ".join(col_names)}) VALUES ({placeholders})'

                for row in data:
                    values = [row.get(col) for col in col_names]
                    self.conn.execute(insert_sql, values)
            return True
        except sqlite3.Error as e:
            logger.error(f"Batch insert failed: {str(e)}")
            return False

    def execute(self, query):
        try:
            with self.conn:
                cursor = self.conn.execute(query)
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                return cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {str(e)}")
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
