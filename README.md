# Blockchain Supply Chain Traceability System

A comprehensive blockchain-based solution for tracing products through the supply chain, providing transparency and authenticity verification.

## System Architecture

This system combines blockchain technology with a traditional database to provide an optimal balance of immutability, traceability, and performance.

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Backend API | FastAPI | REST API for app logic, user management, blockchain interaction |
| Blockchain | Ganache + Web3.py | Local Ethereum blockchain, smart contract interaction |
| Database | MongoDB | Stores user data and non-critical product data |
| Frontend | Streamlit | Python-based GUI for usability |
| Smart Contract | Solidity | Stores product lifecycle data on blockchain |

### Authentication System
- User roles: Producer, Distributor, Retailer, Consumer, Regulator
- JWT-based authentication for API security
- Role-based permissions and access control

### Data Distribution

| Type of Data | Stored In | Why |
|--------------|-----------|-----|
| Product ID, timestamps, handlers, status | Blockchain (Ganache) | Immutable, traceable |
| User credentials, roles, emails | MongoDB | Private, not for decentralization |
| Product images, descriptions, comments | MongoDB | Mutable, optional data |

## Getting Started

### Prerequisites

- Python 3.8+
- MongoDB (local or Atlas)
- Ganache (local Ethereum blockchain)
- Solidity compiler (for contract deployment)

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/BlockChainSCM.git
cd BlockChainSCM
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your configurations:
```
DB_PASSWORD=your_mongodb_password
SECRET_KEY=your_secret_key_for_jwt
PROVIDER_URL=http://127.0.0.1:7545  # Ganache default URL
CONTRACT_ADDRESS=0xYourContractAddress  # After deployment
PRIVATE_KEY=your_ganache_account_private_key  # For blockchain transactions
```

### Deploying the Smart Contract

1. Start Ganache
2. Deploy the contract using Truffle or a similar tool:
```bash
cd contracts
truffle migrate --network development
```
3. Copy the contract address to your `.env` file

### Running the Application

1. Start the backend API
```bash
cd backend
uvicorn main:app --reload
```

2. Start the frontend
```bash
cd frontend
streamlit run app.py
```

## Product Lifecycle Flow

1. **Product Creation**:
   - Performed by: Producer
   - Adds product info (ID, name, timestamp) to the blockchain
   - Metadata stored in MongoDB

2. **Product Updates**:
   - Each supply chain participant updates relevant info
   - All updates recorded as blockchain transactions
   - Status and location changes are tracked

3. **Product Verification**:
   - Anyone can verify a product using its ID or QR code
   - Complete trace history available
   - Ensures product authenticity and provenance

## Features

- **Full Traceability**: Track products from production to consumer
- **QR Code Generation**: Easy verification for consumers
- **Role-Based Workflows**: Different interfaces for each supply chain participant
- **Blockchain Security**: Immutable record of all product movements
- **Hybrid Storage**: Performance optimization with blockchain + MongoDB

## API Documentation

API documentation is available when the server is running at:
```
http://localhost:8000/docs
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.