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
        string currentOwner;   // Current owner's identifier (email)
        string status;         // Current status (e.g., "Produced", "In Transit", "Delivered")
        uint256 createdAt;     // Timestamp when product was created
        uint256 updatedAt;     // Timestamp when product was last updated
    }
    
    // Transaction structure to track product lifecycle
    struct ProductTransaction {
        string productId;      // Product identifier
        string fromOwner;      // Previous owner
        string toOwner;        // New owner
        string action;         // Action performed (e.g., "Created", "Transferred", "Inspected")
        string status;         // Status at time of transaction
        uint256 timestamp;     // When transaction occurred
    }
    
    // State variables
    address public owner;                                  // Contract owner/deployer
    mapping(string => Product) public products;            // Maps productId to Product
    mapping(string => ProductTransaction[]) public productHistory; // Maps productId to its history
    
    // Events for logging
    event ProductAdded(string productId, string name, string owner, uint256 timestamp);
    event ProductTransferred(string productId, string fromOwner, string toOwner, uint256 timestamp);
    event ProductUpdated(string productId, string status, uint256 timestamp);
    
    // Constructor
    constructor() {
        owner = msg.sender;
    }
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only contract owner can call this function");
        _;
    }
    
    // Function to add a new product to the supply chain
    function addProduct(
        string memory _productId, 
        string memory _name, 
        string memory _owner
    ) public {
        // Ensure product doesn't already exist
        require(bytes(products[_productId].productId).length == 0, "Product already exists");
        
        // Create new product
        products[_productId] = Product({
            productId: _productId,
            name: _name,
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
            timestamp: block.timestamp
        }));
        
        // Emit event
        emit ProductAdded(_productId, _name, _owner, block.timestamp);
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
            timestamp: block.timestamp
        }));
        
        // Emit event
        emit ProductTransferred(_productId, currentOwner, _newOwner, block.timestamp);
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
            action: "Updated",
            status: _newStatus,
            timestamp: block.timestamp
        }));
        
        // Emit event
        emit ProductUpdated(_productId, _newStatus, block.timestamp);
    }
    
    // Function to get product details
    function getProduct(string memory _productId) public view returns (
        string memory productId,
        string memory name,
        string memory currentOwner,
        string memory status,
        uint256 createdAt,
        uint256 updatedAt
    ) {
        // Ensure product exists
        require(bytes(products[_productId].productId).length != 0, "Product does not exist");
        
        Product memory product = products[_productId];
        return (
            product.productId,
            product.name,
            product.currentOwner,
            product.status,
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
        uint256 timestamp
    ) {
        require(_index < productHistory[_productId].length, "Transaction index out of bounds");
        
        ProductTransaction memory txn = productHistory[_productId][_index];
        return (
            txn.fromOwner,
            txn.toOwner,
            txn.action,
            txn.status,
            txn.timestamp
        );
    }
}