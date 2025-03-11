import requests
from datetime import datetime, UTC  # Import UTC for timezone-aware handling

BASE_URL = "https://explorer.fact0rn.io/api/"

def fetch_api_data(endpoint):
    try:
        response = requests.get(BASE_URL + endpoint)
        response.raise_for_status()
        if "getblockhash" in endpoint:
            return response.text.strip()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching {endpoint}: {e}")
        return None

def format_unix_time(unix_time):
    # Use timezone-aware UTC conversion
    return datetime.fromtimestamp(unix_time, UTC).strftime("%H:%M:%S")

# Step 1: Get current block count
block_count = fetch_api_data("getblockcount")
if block_count is None:
    print("Failed to get block count. Exiting.")
    exit()

print(f"Current block index: {block_count}")



# Step 2: Get previous block hash
block_hash = fetch_api_data(f"getblockhash?index={block_count}")
if block_hash is None:
    print("Failed to get block hash. Exiting.")
    exit()

print(f"Hash of block {block_count}: {block_hash}")

# Step 3: Get previous block info
block_info = fetch_api_data(f"getblock?hash={block_hash}")
if block_info is None:
    print("Failed to get block info. Exiting.")
    exit()

# Step 4: Get second previous block info
second_previous_block_index = block_count -1
second_block_hash = fetch_api_data(f"getblockhash?index={second_previous_block_index}")
if second_block_hash is None:
    print("Failed to get block hash for second previous block. Exiting.")
    exit()

block_info_second = fetch_api_data(f"getblock?hash={second_block_hash}")
if block_info_second is None:
    print("Failed to get block info for second previous block. Exiting.")
    exit()

block_time = block_info.get("time")
block_time_second = block_info_second.get("time")

