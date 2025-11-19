from web3 import Web3
from web3.contract import Contract
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class ActionStatus(Enum):
    """Enum matching the ActionStatus in the smart contract"""
    SUBMITTED = 0
    VALIDATED = 1
    REJECTED = 2


@dataclass
class Activity:
    """Activity data structure"""
    activity_id: int
    name: bytes
    description: bytes
    lead_id: int
    points: int
    is_active: bool


@dataclass
class Action:
    """Action data structure"""
    action_id: int
    person_id: int
    activity_id: int
    description: bytes
    proof_hash: bytes
    status: ActionStatus


class ActivityActionTrackerClient:
    """Client for interacting with ActivityActionTracker smart contract"""
    
    def __init__(
        self,
        web3_provider: str,
        contract_address: str,
        contract_abi: list,
        private_key: Optional[str] = None
    ):
        """
        Initialize the contract client
        
        Args:
            web3_provider: Web3 provider URL (e.g., 'http://localhost:8545')
            contract_address: Deployed contract address
            contract_abi: Contract ABI as a list
            private_key: Private key for signing transactions (optional)
        """
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.contract: Contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=contract_abi
        )
        self.private_key = private_key
        self.account = None
        
        if private_key:
            self.account = self.w3.eth.account.from_key(private_key)
    
    async def _send_transaction(
        self,
        function_call,
        from_address: Optional[str] = None,
        gas: int = 300000000,
    ) -> Dict[str, Any]:
        """
        Send a transaction to the contract
        
        Args:
            function_call: Contract function call object
            from_address: Address to send from (uses account if not provided)
            gas: Gas limit
            gas_price: Gas price in Gpsi
            
        Returns:
            Transaction receipt
        """
        if not from_address:
            if not self.account:
                raise ValueError("No account configured for sending transactions")
            from_address = self.account.address
        # Build transaction
        checksum_address = Web3.to_checksum_address(from_address) # type: ignore
        tx_params = {
            'from': checksum_address,
            'nonce': self.w3.eth.get_transaction_count(checksum_address),
        }

        transaction = function_call.build_transaction(tx_params)
        
        # Sign and send transaction
        if self.private_key:
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction,
                private_key=self.private_key
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        else:
            tx_hash = self.w3.eth.send_transaction(transaction)
        
        # Wait for receipt
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return dict(tx_receipt)
    
    # --- Activity Functions ---
    
    async def create_activity(
        self,
        name: str,
        description: str,
        lead_id: int,
        points: int
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Create a new activity
        
        Args:
            name: Activity name (will be converted to bytes32)
            description: Activity description (will be converted to bytes32)
            lead_id: Person ID of the activity lead
            points: Reputation points for completing the activity
            
        Returns:
            Tuple of (activity_id, transaction_receipt)
        """
        name_bytes = self._string_to_bytes32(name)
        description_bytes = self._string_to_bytes32(description)
        
        function_call = self.contract.functions.createActivity(
            name_bytes,
            description_bytes,
            lead_id,
            points,
        )
        
        receipt = await self._send_transaction(function_call)
        
        # Extract activity ID from events
        activity_id = self._get_activity_id_from_receipt(receipt)
        print(f"Activity Created with ID: {activity_id}")
        
        return activity_id, receipt
    
    async def deactivate_activity(self, activity_id: int) -> Dict[str, Any]:
        """
        Deactivate an activity
        
        Args:
            activity_id: ID of the activity to deactivate
            
        Returns:
            Transaction receipt
        """
        function_call = self.contract.functions.deactivateActivity(activity_id)
        return await self._send_transaction(function_call)
    
    def get_activity(self, activity_id: int) -> Activity:
        """
        Get activity details
        
        Args:
            activity_id: ID of the activity
            
        Returns:
            Activity object
        """
        result = self.contract.functions.activities(activity_id).call()
        
        return Activity(
            activity_id=result[0],
            name=result[1],
            description=result[2],
            lead_id=result[3],
            points=result[4],
            is_active=result[5]
        )
    
    # --- Action Functions ---
    
    async def submit_action(
        self,
        person_id: int,
        activity_id: int,
        description: str,
        proof_hash: str
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Submit an action for an activity
        
        Args:
            person_id: ID of the person submitting the action
            activity_id: ID of the activity
            description: Description of the action
            proof_hash: Hash of the proof (hex string with 0x prefix)
            
        Returns:
            Tuple of (action_id, transaction_receipt)
        """
        description_bytes = self._string_to_bytes32(description)
        # Convert hex string to bytes32
        if proof_hash.startswith('0x'):
            # Remove 0x prefix and convert hex to bytes, then pad to 32 bytes
            proof_hash_bytes = bytes.fromhex(proof_hash[2:]).ljust(32, b'\0')[:32]
        else:
            # Fallback to string encoding if not a hex string
            proof_hash_bytes = self._string_to_bytes32(proof_hash)
        
        function_call = self.contract.functions.submitAction(
            person_id,
            activity_id,
            description_bytes,
            proof_hash_bytes
        )
        
        receipt = await self._send_transaction(function_call)
        
        # Extract action ID from events
        action_id = self._get_action_id_from_receipt(receipt)
        
        return action_id, receipt
    
    async def validate_proof(
        self,
        action_id: int,
        is_valid: bool
    ) -> Dict[str, Any]:
        """
        Validate or reject an action's proof
        
        Args:
            action_id: ID of the action to validate
            is_valid: True to validate, False to reject
            
        Returns:
            Transaction receipt
        """
        function_call = self.contract.functions.validateProof(action_id, is_valid)
        return await self._send_transaction(function_call)
    
    def get_action(self, action_id: int) -> Action:
        """
        Get action details
        
        Args:
            action_id: ID of the action
            
        Returns:
            Action object
        """
        result = self.contract.functions.actions(action_id).call()
        
        return Action(
            action_id=result[0],
            person_id=result[1],
            activity_id=result[2],
            description=result[3],
            proof_hash=result[4],
            status=ActionStatus(result[5])
        )
    
    # --- Reputation Tracker Functions ---
    
    async def set_reputation_tracker_address(
        self,
        reputation_tracker_address: str
    ) -> Dict[str, Any]:
        """
        Set the reputation tracker contract address
        
        Args:
            reputation_tracker_address: Address of the ReputationTracker contract
            
        Returns:
            Transaction receipt
        """
        checksum_address = Web3.to_checksum_address(reputation_tracker_address)
        function_call = self.contract.functions.setReputationTrackerAddress(
            checksum_address
        )
        return await self._send_transaction(function_call)
    
    def get_reputation_tracker_address(self) -> str:
        """
        Get the reputation tracker contract address
        
        Returns:
            Reputation tracker address
        """
        return self.contract.functions.reputationTrackerAddress().call()
    
    # --- Event Listeners ---
    
    def listen_activity_created(self, from_block: int = 'latest'): # type: ignore
        """
        Listen for ActivityCreated events
        
        Args:
            from_block: Starting block number or 'latest'
            
        Returns:
            Event filter
        """
        return self.contract.events.ActivityCreated.create_filter(
            fromBlock=from_block
        )
    
    def listen_action_submitted(self, from_block: int = 'latest'): # type: ignore
        """
        Listen for ActionSubmittedEvent events
        
        Args:
            from_block: Starting block number or 'latest'
            
        Returns:
            Event filter
        """
        return self.contract.events.ActionSubmittedEvent.create_filter(
            fromBlock=from_block
        )
    
    def listen_proof_validated(self, from_block: int = 'latest'): # type: ignore
        """
        Listen for ProofValidatedEvent events
        
        Args:
            from_block: Starting block number or 'latest'
            
        Returns:
            Event filter
        """
        return self.contract.events.ProofValidatedEvent.create_filter(
            fromBlock=from_block
        )
    
    # --- Utility Functions ---
    
    @staticmethod
    def _string_to_bytes32(text: str) -> bytes:
        """Convert string to bytes32"""
        return text.encode('utf-8').ljust(32, b'\0')[:32]
    
    @staticmethod
    def _bytes32_to_string(data: bytes) -> str:
        """Convert bytes32 to string"""
        return data.rstrip(b'\0').decode('utf-8')
    
    def _get_activity_id_from_receipt(self, receipt: Dict[str, Any]) -> int:
        """Extract activity ID from ActivityCreated event"""
        logs = self.contract.events.ActivityCreated().process_receipt(receipt)
        if logs:
            return logs[0]['args']['activityId']
        return 0
    
    def _get_action_id_from_receipt(self, receipt: Dict[str, Any]) -> int:
        """Extract action ID from ActionSubmittedEvent"""
        logs = self.contract.events.ActionSubmittedEvent().process_receipt(receipt)
        if logs:
            return logs[0]['args']['actionId']
        return 0


# --- Example Usage ---

if __name__ == "__main__":
    # Example configuration
    WEB3_PROVIDER = "http://localhost:8545"  # Your Ethereum node
    CONTRACT_ADDRESS = "0x..."  # Your deployed contract address
    PRIVATE_KEY = "0x..."  # Your private key
    
    # Load ABI from file
    with open('ActivityActionTracker_abi.json', 'r') as f:
        CONTRACT_ABI = json.load(f)
    
    # Initialize client
    client = ActivityActionTrackerClient(
        web3_provider=WEB3_PROVIDER,
        contract_address=CONTRACT_ADDRESS,
        contract_abi=CONTRACT_ABI,
        private_key=PRIVATE_KEY
    )
    
    # Create an activity
    activity_id, receipt = client.create_activity(
        name="Code Review",
        description="Review pull requests",
        lead_id=1,
        points=100
    ).__await__()
    print(f"Created activity with ID: {activity_id}")
    
    # Get activity details
    activity = client.get_activity(activity_id)
    print(f"Activity: {client._bytes32_to_string(activity.name)}")
    
    # Submit an action
    action_id, receipt = client.submit_action(
        person_id=2,
        activity_id=activity_id,
        description="Reviewed PR #123",
        proof_hash="0xabc123..."
    ).__await__()
    print(f"Submitted action with ID: {action_id}")
    
    # Validate the action
    receipt = client.validate_proof(action_id, is_valid=True)
    print(f"Validated action {action_id}")
    
    # Get action details
    action = client.get_action(action_id)
    print(f"Action status: {action.status.name}")