// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title SupplyChain
 * @dev Smart contract for tracking products in a supply chain
 */
contract SupplyChain {
    // Product structure
    struct Product {
        string productId;      // Unique product identifier
        string name;           // Product name
        string category;       // Product category
        string description;    // Product description
        uint256 quantity;      // Product quantity
        string location;       // Current location
        string currentOwner;   // Current owner's identifier (username)
        string status;         // Current status (e.g., "Produced", "In Transit", "Delivered")
        uint256 createdAt;     // Timestamp when product was created
        uint256 updatedAt;     // Timestamp when product was last updated
    }
    
    // Transaction structure to track product lifecycle
    struct ProductTransaction {
        string productId;      // Product identifier
        string fromOwner;      // Previous owner
        string toOwner;        // New owner
        string action;         // Action performed (e.g., "Created", "Transferred", "Updated")
        string status;         // Status at time of transaction
        string location;       // Location at time of transaction
        string note;           // Additional notes
        uint256 timestamp;     // When transaction occurred
    }
    
    // Role structure
    struct Role {
        string name;           // Role name (Producer, Distributor, Retailer, etc.)
        bool canAddProducts;   // Can add products
        bool canTransferProducts; // Can transfer products
        bool canUpdateStatus;  // Can update product status
        bool canViewAllProducts; // Can view all products regardless of ownership
    }
    
    // State variables
    address public owner;                                  // Contract owner/deployer
    mapping(string => Product) public products;            // Maps productId to Product
    mapping(string => ProductTransaction[]) public productHistory; // Maps productId to its history
    mapping(string => Role) public roles;                  // Maps role name to Role
    mapping(string => string) public userRoles;            // Maps username to role name
    
    // Events for logging
    event ProductAdded(string productId, string name, string owner, uint256 timestamp);
    event ProductTransferred(string productId, string fromOwner, string toOwner, uint256 timestamp);
    event ProductUpdated(string productId, string status, uint256 timestamp);
    event UserRoleAssigned(string username, string role, uint256 timestamp);
    
    // Constructor
    constructor() {
        owner = msg.sender;
        
        // Initialize default roles
        roles["Producer"] = Role({
            name: "Producer",
            canAddProducts: true,
            canTransferProducts: true,
            canUpdateStatus: true,
            canViewAllProducts: false
        });
        
        roles["Distributor"] = Role({
            name: "Distributor",
            canAddProducts: false,
            canTransferProducts: true,
            canUpdateStatus: true,
            canViewAllProducts: false
        });
        
        roles["Retailer"] = Role({
            name: "Retailer",
            canAddProducts: false,
            canTransferProducts: true,
            canUpdateStatus: true,
            canViewAllProducts: false
        });
        
        roles["Consumer"] = Role({
            name: "Consumer",
            canAddProducts: false,
            canTransferProducts: false,
            canUpdateStatus: false,
            canViewAllProducts: false
        });
        
        roles["Regulator"] = Role({
            name: "Regulator",
            canAddProducts: false,
            canTransferProducts: false,
            canUpdateStatus: false,
            canViewAllProducts: true
        });
    }
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only contract owner can call this function");
        _;
    }
    
    // Function to assign a role to a user
    function assignUserRole(string memory _username, string memory _role) public {
        // In a real implementation, we would add access control here
        userRoles[_username] = _role;
        emit UserRoleAssigned(_username, _role, block.timestamp);
    }
    
    // Function to add a new product to the supply chain
    function addProduct(
        string memory _productId,
        string memory _name,
        string memory _owner
    ) public {
        // Ensure product doesn't already exist
        require(bytes(products[_productId].productId).length == 0, "Product already exists");
        
        // Create new product with minimal info
        products[_productId] = Product({
            productId: _productId,
            name: _name,
            category: "",
            description: "",
            quantity: 1,
            location: "",
            currentOwner: _owner,
            status: "Produced",
            createdAt: block.timestamp,
            updatedAt: block.timestamp
        });
        
        // Add initial transaction to history
        productHistory[_productId].push(ProductTransaction({
            productId: _productId,
            fromOwner: _owner,
            toOwner: _owner,
            action: "Created",
            status: "Produced",
            location: "",
            note: "Product created and registered",
            timestamp: block.timestamp
        }));
        
        // Emit event
        emit ProductAdded(_productId, _name, _owner, block.timestamp);
    }
    
    // Function to update product details
    function updateProductDetails(
        string memory _productId,
        string memory _category,
        string memory _description,
        uint256 _quantity,
        string memory _location
    ) public {
        // Ensure product exists
        require(bytes(products[_productId].productId).length != 0, "Product does not exist");
        
        // Update product details
        products[_productId].category = _category;
        products[_productId].description = _description;
        products[_productId].quantity = _quantity;
        products[_productId].location = _location;
        products[_productId].updatedAt = block.timestamp;
        
        // Add transaction to history
        productHistory[_productId].push(ProductTransaction({
            productId: _productId,
            fromOwner: products[_productId].currentOwner,
            toOwner: products[_productId].currentOwner,
            action: "Updated",
            status: products[_productId].status,
            location: _location,
            note: "Product details updated",
            timestamp: block.timestamp
        }));
        
        // Emit event
        emit ProductUpdated(_productId, products[_productId].status, block.timestamp);
    }
    
    // Function to transfer product ownership
    function transferProduct(
        string memory _productId, 
        string memory _newOwner,
        string memory _newStatus
    ) public {
        // Ensure product exists
        require(bytes(products[_productId].productId).length != 0, "Product does not exist");
        
        // Get current owner for the transaction record
        string memory currentOwner = products[_productId].currentOwner;
        
        // Update product
        products[_productId].currentOwner = _newOwner;
        products[_productId].status = _newStatus;
        products[_productId].updatedAt = block.timestamp;
        
        // Add transaction to history
        productHistory[_productId].push(ProductTransaction({
            productId: _productId,
            fromOwner: currentOwner,
            toOwner: _newOwner,
            action: "Transferred",
            status: _newStatus,
            location: products[_productId].location,
            note: "Ownership transferred",
            timestamp: block.timestamp
        }));
        
        // Emit event
        emit ProductTransferred(_productId, currentOwner, _newOwner, block.timestamp);
    }
    
    // Function to update product location (for distributors)
    function updateProductLocation(
        string memory _productId,
        string memory _newLocation,
        string memory _note
    ) public {
        // Ensure product exists
        require(bytes(products[_productId].productId).length != 0, "Product does not exist");
        
        // Update product location
        products[_productId].location = _newLocation;
        products[_productId].updatedAt = block.timestamp;
        
        // Add transaction to history
        productHistory[_productId].push(ProductTransaction({
            productId: _productId,
            fromOwner: products[_productId].currentOwner,
            toOwner: products[_productId].currentOwner,
            action: "LocationUpdated",
            status: products[_productId].status,
            location: _newLocation,
            note: _note,
            timestamp: block.timestamp
        }));
    }
    
    // Function to update product status
    function updateProductStatus(
        string memory _productId, 
        string memory _newStatus
    ) public {
        // Ensure product exists
        require(bytes(products[_productId].productId).length != 0, "Product does not exist");
        
        // Update product status
        products[_productId].status = _newStatus;
        products[_productId].updatedAt = block.timestamp;
        
        // Add transaction to history
        productHistory[_productId].push(ProductTransaction({
            productId: _productId,
            fromOwner: products[_productId].currentOwner,
            toOwner: products[_productId].currentOwner,
            action: "StatusUpdated",
            status: _newStatus,
            location: products[_productId].location,
            note: "Status updated",
            timestamp: block.timestamp
        }));
        
        // Emit event
        emit ProductUpdated(_productId, _newStatus, block.timestamp);
    }
    
    // Function to update product availability (for retailers)
    function updateProductAvailability(
        string memory _productId,
        string memory _availability,
        uint256 _price
    ) public {
        // Ensure product exists
        require(bytes(products[_productId].productId).length != 0, "Product does not exist");
        
        // Update product status to reflect availability
        products[_productId].status = _availability;
        products[_productId].updatedAt = block.timestamp;
        
        // Add transaction to history
        productHistory[_productId].push(ProductTransaction({
            productId: _productId,
            fromOwner: products[_productId].currentOwner,
            toOwner: products[_productId].currentOwner,
            action: "AvailabilityUpdated",
            status: _availability,
            location: products[_productId].location,
            note: string(abi.encodePacked("Price set to ", _toString(_price))),
            timestamp: block.timestamp
        }));
    }
    
    // Function to get product details
    function getProduct(string memory _productId) public view returns (
        string memory productId,
        string memory name,
        string memory category,
        string memory currentOwner,
        string memory status,
        string memory location,
        uint256 createdAt,
        uint256 updatedAt
    ) {
        // Ensure product exists
        require(bytes(products[_productId].productId).length != 0, "Product does not exist");
        
        Product memory product = products[_productId];
        return (
            product.productId,
            product.name,
            product.category,
            product.currentOwner,
            product.status,
            product.location,
            product.createdAt,
            product.updatedAt
        );
    }
    
    // Function to get transaction history count
    function getProductHistoryCount(string memory _productId) public view returns (uint256) {
        return productHistory[_productId].length;
    }
    
    // Function to get specific transaction from history
    function getProductHistoryItem(string memory _productId, uint256 _index) public view returns (
        string memory fromOwner,
        string memory toOwner,
        string memory action,
        string memory status,
        string memory location,
        string memory note,
        uint256 timestamp
    ) {
        require(_index < productHistory[_productId].length, "Transaction index out of bounds");
        
        ProductTransaction memory txn = productHistory[_productId][_index];
        return (
            txn.fromOwner,
            txn.toOwner,
            txn.action,
            txn.status,
            txn.location,
            txn.note,
            txn.timestamp
        );
    }
    
    // Helper function to convert uint to string
    function _toString(uint256 value) internal pure returns (string memory) {
        // This is just a simple implementation for a limited range of values
        if (value == 0) {
            return "0";
        }
        
        uint256 temp = value;
        uint256 digits;
        
        while (temp != 0) {
            digits++;
            temp /= 10;
        }
        
        bytes memory buffer = new bytes(digits);
        
        while (value != 0) {
            digits -= 1;
            buffer[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }
        
        return string(buffer);
    }
}