# Blockchain Configuration for Activity Action API

## Environment Variables

To enable blockchain integration, set the following environment variables:

### Required Variables

```bash
# Web3 Provider URL (Ethereum node endpoint)
export WEB3_PROVIDER="http://localhost:8545"

# Deployed Smart Contract Address
export CONTRACT_ADDRESS="0x..."

# Private Key for Transaction Signing (without 0x prefix)
export PRIVATE_KEY="your_private_key_here"

# Contract ABI Path (absolute or relative)
export CONTRACT_ABI_PATH="/path/to/contract_abi.json"
```

### Alternative: Inline ABI

Instead of using `CONTRACT_ABI_PATH`, you can provide the ABI directly:

```bash
export CONTRACT_ABI='[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"}...]'
```

## Usage

The API will automatically:

1. **Create Activity** - Stores activity data on blockchain and returns transaction hash
2. **Deactivate Activity** - Updates activity status on blockchain
3. **Submit Action** - Records action submission on blockchain with proof hash
4. **Validate Proof** - Updates action validation status on blockchain

## Response Format with Blockchain

### Create Activity Response
```json
{
  "message": "Activity created successfully",
  "activityId": "550e8400-e29b-41d4-a716-446655440000",
  "blockchainActivityId": 1,
  "transactionHash": "0xabc123..."
}
```

### Submit Action Response
```json
{
  "message": "Action submitted successfully",
  "actionId": "750e8400-e29b-41d4-a716-446655440002",
  "blockchainActionId": 1,
  "transactionHash": "0xdef456..."
}
```

## Error Handling

If blockchain operations fail, the API will:
- Still complete the database operation successfully
- Return a warning message about blockchain failure
- Allow retry mechanisms to sync data later

Example fallback response:
```json
{
  "message": "Activity created successfully (blockchain storage pending)",
  "activityId": "550e8400-e29b-41d4-a716-446655440000",
  "warning": "Blockchain storage failed: connection timeout"
}
```

## UUID to Integer Conversion

The API automatically converts UUIDs to integers for blockchain storage:
- **PersonId** → Integer (for lead_id, person_id)
- **ActivityId** → Integer (for activity_id)
- **ActionId** → Integer (for action_id)

Conversion is bidirectional and maintains data integrity.

## Testing

### Local Blockchain Setup

1. Install and run Ganache:
```bash
npm install -g ganache
ganache --port 8545
```

2. Deploy the contract and note the contract address

3. Set environment variables:
```bash
export WEB3_PROVIDER="http://localhost:8545"
export CONTRACT_ADDRESS="0x..."
export PRIVATE_KEY="0x..."
```

### Testing Endpoints

Use the provided cURL examples in the main README with the environment configured.

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit private keys** to version control
2. Use environment variables or secure key management systems
3. In production, use:
   - Hardware wallets
   - Key management services (AWS KMS, Azure Key Vault)
   - Secure enclaves

4. Consider using a separate signing service for production deployments

## Troubleshooting

### Common Issues

**Issue:** "Cannot connect to blockchain"
- **Solution:** Verify `WEB3_PROVIDER` is correct and the node is running

**Issue:** "Transaction failed: insufficient funds"
- **Solution:** Ensure the account has enough ETH for gas fees

**Issue:** "Contract ABI not found"
- **Solution:** Check `CONTRACT_ABI_PATH` points to valid JSON file

**Issue:** "Invalid contract address"
- **Solution:** Verify `CONTRACT_ADDRESS` is checksummed and correct

## Integration Flow

```
User Request
    ↓
API Validation
    ↓
Application Service (Domain Logic)
    ↓
Database Storage ✓
    ↓
Blockchain Storage
    ↓
    ├─ Success → Return with transaction hash
    └─ Failure → Return with warning (data still saved in DB)
```

This ensures the system remains operational even if blockchain connectivity is temporarily unavailable.
