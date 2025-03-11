import requests
import json
import datetime
import psycopg2
import requestingFact
import os

# Fact0rn API base URL
BASE_URL = os.environ.get("API_BASE_URL", "https://explorer.fact0rn.io/api/")
EXT_BASE_URL = os.environ.get("EXT_BASE_URL", "https://explorer.fact0rn.io/ext/")

# Database connection parameters
DB_PARAMS = {
    "dbname": os.environ.get("DB_NAME", "fact0rn_data"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "Haadimoto2005"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432")
}

def fetch_api_data(endpoint):
    """Fetch data from the Fact0rn API."""
    try:
        response = requests.get(BASE_URL + endpoint)
        response.raise_for_status()
        if "getblockhash" in endpoint:
            return response.text.strip()  # Block hash is returned as plain text
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching {endpoint}: {e}")
        return None

def get_money_supply():
    """Get the current money supply."""
    try:
        # Use the ext endpoint instead of api
        response = requests.get(EXT_BASE_URL + "getmoneysupply")
        response.raise_for_status()
        # The API returns the value directly as text
        money_supply = float(response.text.strip())
        print(f"Current money supply: {money_supply}")
        return money_supply
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching money supply: {e}")
        return None

def get_block_reward(block_hash):
    """Get the block reward using the block hash."""
    print(f"Getting block reward for hash: {block_hash}")
    
    # Get block info to get the coinbase transaction
    block_info = fetch_api_data(f"getblock?hash={block_hash}")
    if not block_info or "tx" not in block_info or not block_info["tx"]:
        print("Failed to get block info or no transactions found")
        return None
    
    # Get the coinbase transaction details
    coinbase_tx = fetch_api_data(f"getrawtransaction?txid={block_info['tx'][0]}&decrypt=1")
    if not coinbase_tx or "vout" not in coinbase_tx:
        print("Failed to get coinbase transaction details")
        return None
    
    # Sum up all outputs in the coinbase transaction
    reward = sum(vout["value"] for vout in coinbase_tx["vout"] if "value" in vout)
    print(f"Block reward: {reward}")
    return reward

def save_to_database(data):
    """Save emissions data to PostgreSQL database."""
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(**DB_PARAMS)
        cursor = connection.cursor()
        
        cursor.execute("""
            INSERT INTO emissions 
            (current_block_number, unix_timestamp, date_time, money_supply, block_reward)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (current_block_number) 
            DO UPDATE SET 
                unix_timestamp = EXCLUDED.unix_timestamp,
                date_time = EXCLUDED.date_time,
                money_supply = EXCLUDED.money_supply,
                block_reward = EXCLUDED.block_reward;
        """, (
            data["block_index"],
            data["unix_timestamp"],
            data["date_time"],
            data["money_supply"],
            data["block_reward"]
        ))
        
        connection.commit()
        print(f" Emissions data saved to database for block {data['block_index']}")
        
    except psycopg2.Error as e:
        print(f" Database error: {e}")
    finally:
        if connection:
            if cursor:
                cursor.close()
            connection.close()

def track_emissions():
    """Track emissions using data from requestingFact."""
    print(f"\nTracking emissions for block {requestingFact.block_count}...")
    
    # Get block hash
    block_hash = fetch_api_data(f"getblockhash?index={requestingFact.block_count}")
    if not block_hash:
        print(" Failed to get block hash")
        return
    
    print(f"Got block hash: {block_hash}")
    
    # Get money supply and block reward
    money_supply = get_money_supply()
    block_reward = get_block_reward(block_hash)
    
    if money_supply is None and block_reward is None:
        print(" Failed to get both money supply and block reward")
        return
    
    # Create emissions data using existing timestamp from requestingFact
    emissions_data = {
        "block_index": requestingFact.block_count,
        "unix_timestamp": requestingFact.block_time,
        "date_time": datetime.datetime.fromtimestamp(requestingFact.block_time),
        "money_supply": money_supply if money_supply is not None else None,
        "block_reward": block_reward if block_reward is not None else None
    }
    
    # Save to database
    save_to_database(emissions_data)
    print(f" Successfully tracked emissions for block {requestingFact.block_count}")

if __name__ == "__main__":
    track_emissions()