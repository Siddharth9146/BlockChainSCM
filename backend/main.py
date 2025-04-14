from fastapi import FastAPI, HTTPException, Depends, Body, status
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from passlib.context import CryptContext
from web3 import Web3
import json
import os
from dotenv import dotenv_values

# Import local modules
from models.user import User
from models.product import Product
from models.transaction import Transaction
from models.role_permission import RolePermission
from db import users_collection, products_collection, transactions_collection, roles_permissions_collection

# Load environment variables
config = dotenv_values("../.env")
SECRET_KEY = config.get("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Setup FastAPI
app = FastAPI(title="Supply Chain Traceability API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 with Password flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Web3 setup - connect to local Ganache instance
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

# Load and compile the smart contract (in production, would use the deployed ABI)
try:
    with open("../contracts/SupplyChain.json") as f:
        contract_json = json.load(f)
    
    contract_abi = contract_json["abi"]
    contract_address = contract_json.get("networks", {}).get("5777", {}).get("address")
    
    if not contract_address:
        print("Warning: Contract address not found in JSON. Using placeholder.")
        contract_address = "0x0000000000000000000000000000000000000000"  # Placeholder
    
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)
except Exception as e:
    print(f"Warning: Unable to load contract: {str(e)}")
    contract = None

# Authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = users_collection.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user

# Role-based access control
def has_permission(user, required_permission):
    user_role = user.get("role").lower()
    role_permissions = roles_permissions_collection.find_one({"role": user_role})
    if not role_permissions:
        return False
    return required_permission in role_permissions["permissions"]

# Authentication endpoints
@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: Dict[str, Any] = Body(...)):
    # Check if user already exists
    if users_collection.find_one({"username": user_data["username"]}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user_data["password"])
    
    # Create user with hashed password
    user_dict = {
        "username": user_data["username"],
        "password_hash": hashed_password,
        "role": user_data["role"],
        "phone": user_data.get("phone", ""),
        "email": user_data.get("email", ""),
        "registered_at": datetime.utcnow()
    }
    
    # Insert user into database
    result = users_collection.insert_one(user_dict)
    
    return {"message": "User created successfully", "user_id": str(result.inserted_id)}

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}, 
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user["role"]
    }

@app.post("/login", status_code=status.HTTP_200_OK)
async def login(username: str = Body(...), password: str = Body(...)):
    user = users_collection.find_one({"username": username})
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    return {
        "success": True,
        "user_id": str(user["_id"]),
        "role": user["role"],
        "username": user["username"]

        
    }

# Product endpoints
@app.post("/product", status_code=status.HTTP_201_CREATED)
async def add_product(product_data: Dict[str, Any] = Body(...), current_user: dict = Depends(get_current_user)):
    # Check if user has permission to add product
    
    
    
    # Generate product ID if not provided
    if "productId" not in product_data:
        product_data["productId"] = f"PROD-{datetime.utcnow().timestamp():.0f}"
    
    # Add product to blockchain
    try:
        if contract:
            # Get an address with funds from Ganache
            account = w3.eth.accounts[0]
            
            # Execute contract function
            tx_hash = contract.functions.addProduct(
                product_data["productId"],
                product_data["name"],
                current_user["username"],
            ).transact({'from': account})
            
            # Wait for transaction receipt
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            blockchain_tx = tx_hash.hex()
        else:
            blockchain_tx = "mock-tx-hash-contract-not-available"
        
        # Save product metadata to MongoDB
        product_dict = {
            "productId": product_data["productId"],
            "name": product_data["name"],
            "description": product_data.get("description", ""),
            "category": product_data.get("category", ""),
            "quantity": product_data.get("quantity", 1),
            "location": product_data.get("location", ""),
            "date_created": product_data.get("date", datetime.utcnow().strftime("%Y-%m-%d")),
            "image_url": product_data.get("image_url", ""),
            "current_owner": current_user["username"],
            "status": "Produced",
            "last_updated": datetime.utcnow(),
            "batch_id": product_data.get("batch_id", ""),
        }
        
        result = products_collection.insert_one(product_dict)
        
        # Create initial transaction record
        transaction = {
            "productId": product_data["productId"],
            "from_user": current_user["username"],
            "to_user": current_user["username"],
            "timestamp": datetime.utcnow(),
            "action": "created",
            "note": "Product created and registered"
        }
        
        transactions_collection.insert_one(transaction)
        
        return {
            "success": True,
            "message": "Product added successfully",
            "product_id": product_data["productId"],
            "tx_hash": blockchain_tx
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add product: {str(e)}"
        )

@app.post("/distributor", status_code=status.HTTP_201_CREATED)
async def add_distributor(distributor_data: Dict[str, Any] = Body(...), current_user: dict = Depends(get_current_user)):
    # Check if user has permission to add distributor
    if current_user["role"].lower() != "producer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only producers can add distributors"
        )
    
    try:
        # Create a distributor record
        distributor = {
            "id": distributor_data["id"],
            "name": distributor_data["name"],
            "created_by": current_user["username"],
            "created_at": datetime.utcnow()
        }
        
        result = db.distributors.insert_one(distributor)
        
        return {
            "success": True,
            "message": f"Distributor '{distributor_data['name']}' added successfully",
            "distributor_id": distributor_data["id"]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add distributor: {str(e)}"
        )

@app.get("/distributors")
async def get_distributors():
    try:
        # Fetch all users with role = distributor from the database
        distributors = list(users_collection.find({"role": "distributor"}))
        
        # Extract usernames and IDs for JSON serialization
        distributor_data = [
            {"id": str(distributor["_id"]), "username": distributor["username"]}
            for distributor in distributors
        ]
        
        return {"success": True, "distributors": distributor_data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve distributors: {str(e)}"
        )

@app.put("/product/{product_id}")
async def update_product(
    product_id: str,
    update_data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    # Check product exists
    product = products_collection.find_one({"productId": product_id})
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update product on blockchain and in database
    try:
        if contract:
            # Get an address with funds from Ganache
            account = w3.eth.accounts[0]
            
            # If ownership transfer
            new_owner = update_data.get("new_owner")
            if new_owner:
                # Execute contract function to transfer ownership
                tx_hash = contract.functions.transferProduct(
                    product_id,
                    new_owner,
                    update_data.get("status", "Transferred")
                ).transact({'from': account})
                
                blockchain_tx = tx_hash.hex()
            else:
                # Just update status
                tx_hash = contract.functions.updateProductStatus(
                    product_id,
                    update_data.get("status", "Updated")
                ).transact({'from': account})
                
                blockchain_tx = tx_hash.hex()
        else:
            blockchain_tx = "mock-tx-hash-contract-not-available"
        
        # Create transaction record
        transaction = {
            "productId": product_id,
            "from_user": product["current_owner"],
            "to_user": update_data.get("new_owner", product["current_owner"]),
            "timestamp": datetime.utcnow(),
            "action": "transferred" if update_data.get("new_owner") else "updated",
            "note": update_data.get("note", "")
        }
        
        transactions_collection.insert_one(transaction)
        
        # Update timestamp
        update_data["last_updated"] = datetime.utcnow()
        
        # For distributor location updates
        if "new_location" in update_data:
            update_data["location"] = update_data.pop("new_location")
        
        # If ownership transfer
        if "new_owner" in update_data:
            update_data["current_owner"] = update_data.pop("new_owner")
        
        # Update MongoDB record
        products_collection.update_one(
            {"productId": product_id},
            {"$set": update_data}
        )
        
        return {
            "success": True,
            "message": "Product updated successfully",
            "tx_hash": blockchain_tx
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update product: {str(e)}"
        )

@app.get("/product/{product_id}")
async def get_product(product_id: str):
    try:
        # Get product data from blockchain
        blockchain_data = None
        if contract:
            try:
                blockchain_data = contract.functions.getProduct(product_id).call()
            except Exception as e:
                print(f"Warning: Could not fetch blockchain data: {str(e)}")
        
        # Get detailed metadata from MongoDB
        product = products_collection.find_one({"productId": product_id})
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found in database"
            )
        
        # Convert ObjectId to string for JSON serialization
        product["_id"] = str(product["_id"])
        
        # Get transaction history
        transactions = list(transactions_collection.find(
            {"productId": product_id}
        ))
        
        # Convert ObjectId to string in each transaction
        for txn in transactions:
            txn["_id"] = str(txn["_id"])
        
        # Combine blockchain and database data
        return {
            "success": True,
            "product": product,
            "blockchain_data": blockchain_data,
            "transaction_history": transactions
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve product data: {str(e)}"
        )

@app.get("/products")
async def get_products(current_user: dict = Depends(get_current_user)):
    try:
        # Determine which products to return based on role
        role = current_user["role"].lower()
        
        if role == "regulator":
            # Regulators can see all products
            products_cursor = products_collection.find({})
        elif role == "producer":
            # Producers can see products they created
            products_cursor = products_collection.find({"current_owner": current_user["username"]})
        elif role in ["distributor", "retailer"]:
            # Distributors and retailers can see products assigned to them
            products_cursor = products_collection.find({"current_owner": current_user["username"]})
        else:  # Consumer
            # Consumers can see all products but with limited info
            products_cursor = products_collection.find({})
        
        # Convert to list and clean for JSON serialization
        products = []
        for product in products_cursor:
            product["_id"] = str(product["_id"])
            products.append(product)
        
        return {
            "success": True,
            "products": products
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve products: {str(e)}"
        )

@app.get("/transactions/{product_id}")
async def get_product_transactions(product_id: str):
    try:
        # Get transaction history from MongoDB
        transactions_cursor = transactions_collection.find({"productId": product_id})
        
        # Convert to list and clean for JSON serialization
        transactions = []
        for txn in transactions_cursor:
            txn["_id"] = str(txn["_id"])
            transactions.append(txn)
        
        return {
            "success": True,
            "transactions": transactions
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve transactions: {str(e)}"
        )

@app.get("/trace/{product_id}")
async def get_product_trace(product_id: str):
    try:
        # Get product details
        product = products_collection.find_one({"productId": product_id})
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Convert ObjectId to string
        product["_id"] = str(product["_id"])
        
        # Get complete transaction history
        transactions = list(transactions_collection.find({"productId": product_id}))
        
        # Clean transactions for JSON serialization
        for txn in transactions:
            txn["_id"] = str(txn["_id"])
        
        # Format trace information
        trace = {
            "product": product,
            "history": transactions,
            "origin": transactions[0]["from_user"] if transactions else None,
            "current_location": product.get("location", "Unknown"),
            "roles_involved": list(set([txn["from_user"] for txn in transactions] + [txn["to_user"] for txn in transactions]))
        }
        
        return {
            "success": True,
            "trace": trace
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve product trace: {str(e)}"
        )

@app.get("/")
async def root():
    return {"message": "Welcome to the Supply Chain Traceability API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)