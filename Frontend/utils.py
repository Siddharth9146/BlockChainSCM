from datetime import date

# Dummy in-memory data stores
users = {
    "1": {"username": "producer", "password": "1", "role": "Producer", "phone": "1234567890", "email": "producer@example.com"},
    "2": {"username": "distributor", "password": "2", "role": "Distributor", "phone": "1234567891", "email": "distributor@example.com"},
    "3": {"username": "retailer", "password": "3", "role": "Retailer", "phone": "1234567892", "email": "retailer@example.com"},
    "4": {"username": "consumer", "password": "4", "role": "Consumer", "phone": "1234567893", "email": "consumer@example.com"},
}

distributors = []
products = []
retailers = []

# ------------------ Auth Functions ------------------

def register_user(username, password, phone, email, role):
    """Register a new user."""
    new_user_id = str(len(users) + 1)
    users[new_user_id] = {
        "username": username,
        "password": password,
        "role": role,
        "phone": phone,
        "email": email,
    }
    return {"success": True, "message": f"User '{username}' registered successfully."}

def login(username, password):
    """Login a user based on username and password."""
    for user in users.values():
        if user["username"] == username and user["password"] == password:
            return user["role"], user  # Return role and full user info
    return None, None

# ------------------ Producer ------------------

def add_distributor(distributor_id, distributor_name):
    """Add a new distributor."""
    distributors.append({"id": distributor_id, "name": distributor_name})
    return {"success": True, "message": f"Distributor '{distributor_name}' added successfully."}

def get_all_distributors():
    """Get all distributor IDs."""
    return [d["id"] for d in distributors]

def add_product(product_id, name, origin, timestamp, batch_id, distributor_id, additional_fields=None):
    """Add a new product."""
    product = {
        "id": product_id,
        "name": name,
        "origin": origin,
        "timestamp": timestamp,
        "batch_id": batch_id,
        "distributor_id": distributor_id
    }
    if additional_fields:
        product.update(additional_fields)
    products.append(product)
    return {"success": True, "message": f"Product '{name}' added successfully."}

def update_product(product_id, updates):
    """Update an existing product."""
    for product in products:
        if product["id"] == product_id:
            product.update(updates)
            return {"success": True, "message": f"Product {product_id} updated."}
    return {"success": False, "message": f"Product {product_id} not found."}

# ------------------ Retailer ------------------

def add_retailer(retailer_id, retailer_name):
    """Add a new retailer."""
    retailers.append({"id": retailer_id, "name": retailer_name})
    return {"success": True, "message": f"Retailer '{retailer_name}' added successfully."}

def view_retailer_products():
    """View products available to retailers."""
    return products  # Retailers can view all products (could be expanded later for access control)

# ------------------ Consumer ------------------

def view_products():
    """View all products."""
    return products if products else []

def view_transaction_history(product_id):
    """View transaction history of a product."""
    return [
        {"product_id": product_id, "transaction_type": "Added", "timestamp": "2025-04-01", "by": "Producer"},
        {"product_id": product_id, "transaction_type": "Shipped", "timestamp": "2025-04-05", "by": "Distributor"},
    ]

# ------------------ Common ------------------

def add_custom_fields(fields):
    """Add custom fields for products."""
    print(f"Custom fields added: {fields}")
    return {"success": True}

# ------------------ Mock HTTP ------------------

# Since you indicated no backend, I'm assuming mock HTTP functions aren't necessary right now.
# You may later implement them when connecting to a real backend, but for now, we will leave these unused.

def send_get(url):
    """Mock GET request for integration."""
    print(f"Mock GET to {url}")
    return {"status": "success", "data": "Mock GET response"}

def send_post(url, data):
    """Mock POST request for integration."""
    print(f"Mock POST to {url} with data: {data}")
    return {"status": "success", "data": "Mock POST response"}
