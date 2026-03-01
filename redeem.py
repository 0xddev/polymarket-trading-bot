


from dotenv import load_dotenv
from eth_utils import to_checksum_address, keccak
from eth_abi import encode
import os
from web3 import Web3
from py_builder_relayer_client.client import RelayClient  # pyright: ignore[reportMissingImports]
from py_builder_relayer_client.models import OperationType, SafeTransaction  # pyright: ignore[reportMissingImports]
from py_builder_signing_sdk.config import BuilderConfig, BuilderApiKeyCreds



load_dotenv()



def main():
    print("starting...")
    relayer_url = os.getenv("RELAYER_URL", "https://relayer-v2-staging.polymarket.dev/")
    chain_id = int(os.getenv("CHAIN_ID", 80002))
    pk = os.getenv("PRIVATE_KEY")

    builder_config = BuilderConfig(
        local_builder_creds=BuilderApiKeyCreds(
            key=os.getenv("BUILDER_API_KEY"),
            secret=os.getenv("BUILDER_SECRET"),
            passphrase=os.getenv("BUILDER_PASS_PHRASE"),
        )
    )

    client = RelayClient(relayer_url, chain_id, pk, builder_config)

    redeem_abi = [{
    "name": "redeemPositions",
    "type": "function",
    "inputs": [
        {"name": "collateralToken", "type": "address"},
        {"name": "parentCollectionId", "type": "bytes32"},
        {"name": "conditionId", "type": "bytes32"},
        {"name": "indexSets", "type": "uint256[]"}
    ],
    "outputs": []
    }]

    redeem_tx = {
    "to": "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045",
    "data": Web3().eth.contract(
        address="0x4D97DCd97eC945f40cF65F87097ACe5EA0476045", abi=redeem_abi
    ).encode_abi(
        abi_element_identifier="redeemPositions",
        args=["0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", bytes(32), condition_id, [1, 2]]
    ),
    "value": "0"}

    response = client.execute([redeem_tx], "Redeem winning tokens")
    response.wait()
    print(f"Redeem transaction hash: {response.transaction_hash}")
    print("Redeem complete!")
