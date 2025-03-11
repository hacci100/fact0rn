import psycopg2
import os

try:
    # Connect using DATABASE_URL
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    cursor = conn.cursor()

    # Create block_data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS block_data (
        current_block_number bigint PRIMARY KEY,
        current_block_timestamp bigint,
        previous_block_number bigint,
        previous_block_timestamp bigint,
        block_time_interval_seconds integer,
        network_hashrate numeric(18,2)
    );
    ''')

    # Create emissions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS emissions (
        current_block_number bigint PRIMARY KEY,
        unix_timestamp bigint,
        date_time timestamp,
        money_supply numeric,
        block_reward numeric
    );
    ''')

    conn.commit()
    print('Tables created successfully')
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error setting up database: {e}")
