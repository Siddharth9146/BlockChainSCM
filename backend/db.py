from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import dotenv_values

# Load environment variables from .env file
config = dotenv_values("../.env")

# Ensure db_password is not None and is a string
db_password = config.get("DB_PASSWORD")
if not db_password:
    raise ValueError("DB_PASSWORD is not set in the .env file.")

# URL encode the password
encoded_password = quote_plus(db_password)

# Construct the MongoDB URI with encoded parameters
mongo_uri = f"mongodb+srv://sid:{encoded_password}@dbcluster.mdwkzgv.mongodb.net/?retryWrites=true&w=majority&appName=dbCluster"

# Connect to MongoDB
client = MongoClient(mongo_uri)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Create a db
db = client["supplychain"]

# Create collections
users_collection = db["users"]
products_collection = db["products"]
transactions_collection = db["transactions"]
roles_permissions_collection = db["roles_permissions"]

# Initialize roles and permissions if they don't exist
default_roles = [
    {
        "role": "producer",
        "permissions": ["add_product", "update_product", "view_own_products"]
    },
    {
        "role": "distributor",
        "permissions": ["update_product", "transfer_product", "view_own_products"]
    },
    {
        "role": "retailer",
        "permissions": ["update_product", "transfer_product", "view_own_products"]
    },
    {
        "role": "consumer",
        "permissions": ["view_product"]
    },
    {
        "role": "regulator",
        "permissions": ["view_all_products", "view_all_transactions"]
    }
]

# Add roles if they don't exist
for role in default_roles:
    if not roles_permissions_collection.find_one({"role": role["role"]}):
        roles_permissions_collection.insert_one(role)