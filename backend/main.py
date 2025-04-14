from fastapi import FastAPI, HTTPException, Depends, Body, status
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import List, Optional
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
from db import users_collection, products_collection, transactions_collection

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
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Load and compile the smart contract (in production, would use the deployed ABI)
with open("../contracts/SupplyChain.json") as f:
    contract_json = json.load(f)

contract_abi = contract_json["abi"]
contract_address = contract_json.get("networks", {}).get("5777", {}).get("address")

if not contract_address:
    print("Warning: Contract address not found in JSON. Using placeholder.")
    contract_address = "0x0000000000000000000000000000000000000000"  # Placeholder

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

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
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = users_collection.find_one({"email": email})
    if user is None:
        raise credentials_exception
    return user

# Role-based access control
def has_permission(user, required_permission):
    user_role = user.get("role")
    role_permissions = roles_permissions_collection.find_one({"role": user_role})
    if not role_permissions:
        return False
    return required_permission in role_permissions["permissions"]

# Authentication endpoints
@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: User = Body(...)):
    # Check if user already exists
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user.password_hash)
    
    # Create user with hashed password
    user_dict = user.dict()
    user_dict["password_hash"] = hashed_password
    user_dict["registered_at"] = datetime.utcnow()
    
    # Insert user into database
    result = users_collection.insert_one(user_dict)
    
    return {"message": "User created successfully", "user_id": str(result.inserted_id)}

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Product endpoints
@app.post("/product", status_code=status.HTTP_201_CREATED)
async def add_product(product: Product = Body(...), current_user: dict = Depends(get_current_user)):
    # Check if user has permission to add product
    if not has_permission(current_user, "add_product"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add products"
        )
    
    # Add product to blockchain
    try:
        # Get an address with funds from Ganache
        account = w3.eth.accounts[0]
        
        # Execute contract function
        tx_hash = contract.functions.addProduct(
            product.productId,
            product.name,
            current_user["email"]  # Producer email as initial owner
        ).transact({'from': account})
        
        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # If successful, also save product metadata to MongoDB
        product_dict = product.dict()
        product_dict["current_owner"] = current_user["email"]
        product_dict["last_updated"] = datetime.utcnow()
        
        result = products_collection.insert_one(product_dict)
        
        # Create initial transaction record
        transaction = Transaction(
            productId=product.productId,
            from_user=current_user["email"],
            to_user=current_user["email"],
            action="created",
            note="Product created and registered"
        )
        
        transactions_collection.insert_one(transaction.dict())
        
        return {
            "message": "Product added successfully",
            "product_id": product.productId,
            "tx_hash": tx_hash.hex()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add product to blockchain: {str(e)}"
        )

@app.put("/product/{product_id}")
async def update_product(
    product_id: str,
    update_data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    # Check if user has permission to update product
    if not has_permission(current_user, "update_product"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update products"
        )
    
    # Check if product exists
    product = products_collection.find_one({"productId": product_id})
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update product on blockchain
    try:
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
            
            # Create transaction record
            transaction = Transaction(
                productId=product_id,
                from_user=product["current_owner"],
                to_user=new_owner,
                action="transferred",
                note=update_data.get("note", "")
            )
            
            transactions_collection.insert_one(transaction.dict())
            
            # Update MongoDB record
            update_data["current_owner"] = new_owner
        else:
            # Just update status
            tx_hash = contract.functions.updateProductStatus(
                product_id,
                update_data.get("status", "Updated")
            ).transact({'from': account})
            
            # Create transaction record
            transaction = Transaction(
                productId=product_id,
                from_user=current_user["email"],
                to_user=product["current_owner"],
                action="updated",
                note=update_data.get("note", "")
            )
            
            transactions_collection.insert_one(transaction.dict())
        
        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Update timestamp
        update_data["last_updated"] = datetime.utcnow()
        
        # Update MongoDB record
        products_collection.update_one(
            {"productId": product_id},
            {"$set": update_data}
        )
        
        return {
            "message": "Product updated successfully",
            "tx_hash": tx_hash.hex()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update product on blockchain: {str(e)}"
        )

@app.get("/product/{product_id}")
async def get_product(product_id: str):
    try:
        # Get product data from blockchain
        blockchain_data = contract.functions.getProduct(product_id).call()
        
        # Get detailed metadata from MongoDB
        product = products_collection.find_one({"productId": product_id})
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found in database"
            )
        
        # Get transaction history
        transactions = list(transactions_collection.find(
            {"productId": product_id},
            {"_id": 0}  # Exclude the MongoDB _id from results
        ))
        
        # Combine blockchain and database data
        return {
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
    # If user is a producer, return their products
    # If user is a distributor or retailer, return products they're involved with
    # If user is a regulator, return all products
    
    if current_user["role"] == "regulator":
        products = list(products_collection.find({}, {"_id": 0}))
    elif current_user["role"] in ["producer", "distributor", "retailer"]:
        products = list(products_collection.find({"current_owner": current_user["email"]}, {"_id": 0}))
    else:  # Consumer
        products = list(products_collection.find({}, {"_id": 0}).limit(10))  # Limited view
    
    return {"products": products}

# Transaction endpoints
@app.get("/transactions/{product_id}")
async def get_product_transactions(product_id: str, current_user: dict = Depends(get_current_user)):
    transactions = list(transactions_collection.find(
        {"productId": product_id},
        {"_id": 0}
    ))
    
    return {"transactions": transactions}

@app.get("/")
async def root():
    return {"message": "Welcome to the Supply Chain Traceability API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)