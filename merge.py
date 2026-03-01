import os
from dotenv import load_dotenv

load_dotenv()

try:
    from web3 import Web3
    from web3.constants import MAX_INT, HASH_ZERO
    from web3.middleware import (geth_poa_middleware, construct_sign_and_send_raw_middleware)
    from web3.gas_strategies.time_based import fast_gas_price_strategy
    WEB3_AVAILABLE = True
except ImportError as e:
    WEB3_AVAILABLE = False
    Web3 = None  # type: ignore
    MAX_INT = None  # type: ignore
    HASH_ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
    geth_poa_middleware = None  # type: ignore
    construct_sign_and_send_raw_middleware = None  # type: ignore
    fast_gas_price_strategy = None  # type: ignore
    print(f"Error: web3.py is not available. Install with: pip install web3 setuptools")
    print(f"Import error: {e}")
    raise

merge_positions_abi = """[{"constant":false,"inputs":[{"name":"collateralToken","type":"address"},{"name":"parentCollectionId","type":"bytes32"},{"name":"conditionId","type":"bytes32"},{"name":"partition","type":"uint256[]"},{"name":"amount","type":"uint256"}],"name":"mergePositions","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]"""

def main():
    if not WEB3_AVAILABLE or Web3 is None:
        print("Error: web3.py is not available. Cannot proceed.")
        return
    
    pk = os.getenv("PRIVATE_KEY")
    rpc_url = os.getenv("POLYGON_RPC") 

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(pk))
    w3.eth.default_account = w3.eth.account.from_key(pk).address
    w3.eth.set_gas_price_strategy(fast_gas_price_strategy)

    print(f"Starting...")
    print(f"Wallet: {w3.eth.default_account}")
    amount = 1 * 10 ** 6
    collateral_token = Web3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")
            
            # 2. parentCollectionId: bytes32 (HASH_ZERO is already bytes32 format)
    parent_collection_id = HASH_ZERO
            
            # 3. conditionId: bytes32 (ensure it's a hex string with 0x prefix)
            # Web3.py will auto-convert hex string to bytes32
            
            # 4. partition: uint256[] (list of integers, web3.py auto-converts)
    partition = [1, 2]
            
            # 5. amount: uint256 (integer, web3.py auto-converts)
    amount_uint256 = int(amount)
    ctf = w3.eth.contract(address = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045", abi = merge_positions_abi)

    condition_id = "0x49a0055e61d4d481ca57781f5488275a24cdfaa5ce235fd99049dbf203f0d1ab"
    amount = 1 * 10 ** 6 # The amount to merge into collateral
    try:
        txn_hash_bytes = ctf.functions.mergePositions(
            collateral_token, # The collateral token address
            parent_collection_id, # The parent collectionId, always bytes32(0) for Polymarket markets  
            condition_id, # The conditionId of the market
            partition, # The index set used by Polymarket for binary markets
            amount_uint256,
        ).transact()
        print(f"Txn hash bytes: {txn_hash_bytes}")
        txn_hash = w3.to_hex(txn_hash_bytes)
        print(f"Merge transaction hash: {txn_hash}")
        w3.eth.wait_for_transaction_receipt(txn_hash)
        print("Merge complete!")

    except Exception as e:
        print(f"Error merging Outcome Tokens : {e}")
        raise e

    print("Done!")


main()