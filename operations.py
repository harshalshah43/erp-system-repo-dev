import sqlite3

class DatabaseOperations:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        column_definitions = ', '.join([f'{column[0]} {column[1]}' for column in columns])
        query = f'CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})'
        self.cursor.execute(query)
        self.conn.commit()

    def insert_record(self, table_name, data):
        column_names = ', '.join(data.keys())
        values = ', '.join(['?' for _ in data.keys()])
        query = f'INSERT INTO {table_name} ({column_names}) VALUES ({values})'
        self.cursor.execute(query, list(data.values()))
        self.conn.commit()

    def delete_record(self, table_name, data):
        column_names = ', '.join(data.keys())
        values = ', '.join(['?' for _ in data.keys()])
        query = f'DELETE FROM {table_name} WHERE {column_names} VALUES ({values})'
        self.cursor.execute(query, list(data.values()))
        self.conn.commit()

    def search_record(self, table_name, data):
        column_names = ', '.join(data.keys())
        values = ', '.join(['?' for _ in data.keys()])
        query = f'SELECT * FROM {table_name} WHERE {column_names} VALUES ({values})'
        self.cursor.execute(query, list(data.values()))
        result = self.cursor.fetchone()
        return result

    def list_records(self, table_name):
        query = f'SELECT * FROM {table_name}'
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def close_connection(self):
        self.conn.close()


if __name__ == "__main__":
    db_name = 'idbi_account_statement.db'
    db_operations = DatabaseOperations(db_name)

    # Create the 'idbi_account_statement' table
    db_operations.create_table('idbi_account_statement', [
        ('Date', 'TEXT'),
        ('Particular', 'TEXT'),
        ('Chq. No', 'TEXT'),
        ('Withdrawals', 'TEXT'),
        ('Deposits', 'TEXT'),
        ('Balance', 'TEXT')
    ])

    # Insert records
    db_operations.insert_record('idbi_account_statement', {'Date': '2022-01-01', 'Particular': 'Withdrew 1000', 'Chq. No': '1234', 'Withdrawals': '1000', 'Deposits': '0', 'Balance': '900'})
    db_operations.insert_record('idbi_account_statement', {'Date': '2022-01-02', 'Particular': 'Deposited 500', 'Chq. No': '5678', 'Withdrawals': '0', 'Deposits': '500', 'Balance': '1000'})

    # List records
    records = db_operations.list_records('idbi_account_statement')
    for record in records:
        print(record)

    # Search a record
    data = {'Date': '2022-01-01', 'Particular': 'Withdrew 1000', 'Chq. No': '1234', 'Withdrawals': '1000', 'Deposits': '0', 'Balance': '900'}
    result = db_operations.search_record('idbi_account_statement', data)
    if result:
        print(result)

    # Delete a record
    data = {'Date': '2022-01-01', 'Particular': 'Withdrew 1000', 'Chq. No': '1234', 'Withdrawals': '1000', 'Deposits': '0', 'Balance': '900'}
    db_operations.delete_record('idbi_account_statement', data)
