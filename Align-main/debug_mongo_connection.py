import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, ConfigurationError

load_dotenv()

def test_mongo():
    uri = os.getenv("MONGO_URI")
    print(f"Testing Connection to: {uri.split('@')[-1] if '@' in uri else 'Invalid URI Structure'}")
    
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Trigger a connection
        info = client.server_info()
        print("PASS: Connection Successful!")
        print(f"Server Version: {info.get('version')}")
        
        # Test Auth by listing databases
        dbs = client.list_database_names()
        print(f"PASS: Authenticated. Databases: {dbs}")
        
    except OperationFailure as e:
        print(f"FAIL: Authentication Failed: {e.details}")
        print("Tip: Check Username/Password in .env")
    except ConnectionFailure as e:
        print(f"FAIL: Connection Failed: {e}")
        print("Tip: Check IP Whitelist in Atlas (0.0.0.0/0 for testing)")
    except ConfigurationError as e:
        print(f"FAIL: Configuration Error: {e}")
        print("Tip: Check URI format")
    except Exception as e:
        print(f"FAIL: Unknown Error: {e}")

if __name__ == "__main__":
    test_mongo()
