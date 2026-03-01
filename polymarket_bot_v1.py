"""
PolymarketBot - Trading bot for Polymarket BTC 5-minute up/down markets
"""
import json
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv  # pyright: ignore[reportUnusedImport]
import requests

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
    print(f"Warning: web3.py not installed. Install with: pip install web3 setuptools")
    print(f"Import error: {e}")

try:
    from py_clob_client.clob_types import OrderType, OrderArgs, MarketOrderArgs  # pyright: ignore[reportMissingImports]
    from py_clob_client.client import ClobClient  # pyright: ignore[reportMissingImports]
    from py_clob_client.constants import POLYGON, ZERO_ADDRESS  # pyright: ignore[reportMissingImports]
    from py_clob_client.order_builder.constants import BUY, SELL  # pyright: ignore[reportMissingImports]
    from py_builder_relayer_client.client import RelayClient  # pyright: ignore[reportMissingImports]
    from py_builder_relayer_client.models import OperationType, SafeTransaction  # pyright: ignore[reportMissingImports]
    from py_builder_signing_sdk.config import BuilderConfig, BuilderApiKeyCreds
    # Try to import MarketOrderArgs - may be in different location
    try:
        from py_clob_client.clob_types import MarketOrderArgs  # pyright: ignore[reportMissingImports]
    except ImportError:
        try:
            from py_clob_client.order_builder.order_builder import MarketOrderArgs  # pyright: ignore[reportMissingImports]
        except ImportError:
            # Fallback: use OrderArgs for market orders
            MarketOrderArgs = OrderArgs  # type: ignore
except ImportError:
    ClobClient = None  # type: ignore
    POLYGON = 137
    ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
    OrderArgs = None  # type: ignore
    MarketOrderArgs = None  # type: ignore
    RelayClient = None  # type: ignore
    BuilderConfig = None  # type: ignore
    BuilderApiKeyCreds = None  # type: ignore
    print("Warning: py-clob-client not installed. Install with: pip install py-clob-client")


class PolymarketBot:
    """Trading bot for Polymarket BTC 5-minute up/down markets"""
    
    def __init__(
        self,
        private_key: Optional[str] = None,
        host: Optional[str] = "https://clob.polymarket.com",
        chain_id: Optional[int] = None,
        signature_type: Optional[str] = None,
        funder: Optional[str] = None
    ):
        """
        Initialize the PolymarketBot
        
        Args:
            private_key: Private key for signing transactions
            host: CLOB API host URL
            chain_id: Blockchain chain ID (default: POLYGON)
            signature_type: Signature type for orders
            funder: Funder address (optional)
        """
        self.base_url = "https://gamma-api.polymarket.com"
        self.api_url = "https://gamma-api.polymarket.com/markets"
        self.clob_url = host
        self.host = host
        self.private_key = private_key
        self.market = ""
        self.relayer_url = os.getenv("RELAYER_URL")
        
        # Ensure chain_id is an int; fall back to POLYGON if invalid
        resolved_chain_id = chain_id if chain_id is not None else POLYGON
        try:
            self.chain_id = int(resolved_chain_id)
        except (TypeError, ValueError):
            print(f"Warning: Invalid chain_id '{resolved_chain_id}', defaulting to POLYGON ({POLYGON})")
            self.chain_id = POLYGON

        # Initialize builder config and relayer client if available
        if (BuilderConfig is not None and BuilderApiKeyCreds is not None and RelayClient is not None 
            and self.relayer_url is not None):
            try:
                self.builder_config = BuilderConfig(
                    local_builder_creds = BuilderApiKeyCreds(
                        key = os.getenv("BUILDER_API_KEY"),
                        secret = os.getenv("BUILDER_SECRET"),
                        passphrase = os.getenv("BUILDER_PASS_PHRASE"),
                    )
                )
                self.relayer_client = RelayClient(self.relayer_url, self.chain_id, self.private_key, self.builder_config)
            except Exception as e:
                print(f"Warning: Failed to initialize relayer client: {e}")
                self.builder_config = None
                self.relayer_client = None
        else:
            self.builder_config = None
            self.relayer_client = None
            if self.relayer_url is None:
                print("Warning: RELAYER_URL not set. Builder relayer client not available.")
            else:
                print("Warning: Builder relayer client not available. Install required packages.")

        self.signature_type = int(signature_type) if signature_type is not None else None
        self.funder = funder
        print(f"Host: {self.host}")
        print(f"Funder: {self.funder}")
        print(f"Chain ID: {self.chain_id}")
        print(f"Signature Type: {self.signature_type}")
        
        # Initialize CLOB client if available
        if ClobClient is not None:
            self.client = ClobClient(
                self.host,
                key=self.private_key,
                chain_id=self.chain_id,
                signature_type=self.signature_type,
                funder=self.funder
            )
            self.client.set_api_creds(self.client.create_or_derive_api_creds())
            print("CLOB client initialized successfully")
        else:
            self.client = None
            print("Warning: CLOB client not available. Install py-clob-client package.")

    def get_current_timestamp(self) -> int:
        """Get current Unix timestamp"""
        return int(time.time())
    
    def generate_slug(self, timestamp: Optional[int] = None) -> str:
        """
        Generate BTC up/down 5-minute market slug from timestamp
        
        Format: btc-updown-5m-{timestamp}
        
        Args:
            timestamp: Unix timestamp. If None, uses current time
            
        Returns:
            Market slug string
        """
        if timestamp is None:
            timestamp = self.get_current_timestamp()
        
        return f"btc-updown-5m-{timestamp}"
    
    def find_active_market(self, slug: Optional[str] = None) -> Optional[Dict[Any, Any]]:
        """
        Find active BTC 5-minute up/down market using Gamma API
        
        Args:
            slug: Market slug. If None, generates from current timestamp
            
        Returns:
            Market data dictionary or None if not found
        """
        if slug is None:
            slug = self.generate_slug()
        
        try:
            # Use Gamma API to fetch market by slug
            response = requests.get(f"{self.base_url}/events/slug/{slug}")
            
            if response.status_code == 200:
                market_data = response.json()
                return market_data
            else:
                print(f"Market not found: {slug} (Status: {response.status_code})")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching market: {e}")
            return None
    

    def get_token_ids(self, market: Optional[Dict[Any, Any]] = None) -> Optional[Dict[str, str]]:
        """
        Get Up and Down token IDs from market data using clobTokenIds
        
        Args:
            market: Market data dictionary from Gamma API. If None, returns None
            
        Returns:
            Dictionary with 'up_token_id' and 'down_token_id' keys, or None if not found
        """
        if not market:
            return None
        
        try:
            # Extract token IDs from market data
            # Gamma API returns markets array with clobTokenIds
            markets = market.get('markets', [])

            if not markets or len(markets) == 0:
                print("Market data does not contain markets array")
                print(f"Available keys in market: {list(market.keys())}")
                return None
            
            # Get the first market (should be the main market)
            main_market = markets[0]
            clob_token_ids_raw = main_market.get('clobTokenIds', None)
            
            if clob_token_ids_raw is None:
                print("Market does not contain clobTokenIds")
                print(f"Available keys in market[0]: {list(main_market.keys())}")
                return None
            
            # clobTokenIds might be a stringified JSON array, parse it if needed
            if isinstance(clob_token_ids_raw, str):
                try:
                    clob_token_ids = json.loads(clob_token_ids_raw)
                except json.JSONDecodeError:
                    print(f"Failed to parse clobTokenIds as JSON: {clob_token_ids_raw}")
                    return None
            elif isinstance(clob_token_ids_raw, list):
                clob_token_ids = clob_token_ids_raw
            else:
                print(f"clobTokenIds is not a string or list: {type(clob_token_ids_raw)}")
                return None

            if len(clob_token_ids) < 2:
                print(f"Market does not have enough clobTokenIds: {clob_token_ids}")
                return None
            
            # Extract Up and Down token IDs
            # (typically first is Up/Yes, second is Down/No)
            up_token_id = clob_token_ids[0]
            down_token_id = clob_token_ids[1]
            
            if up_token_id and down_token_id:
                return {
                    'up_token_id': up_token_id,
                    'down_token_id': down_token_id
                }
            else:
                print(f"Could not extract token IDs from clobTokenIds: {clob_token_ids}")
                return None
                
        except Exception as e:
            print(f"Error extracting token IDs: {e}")
            import traceback
            traceback.print_exc()
            return None

    def find_next_active_market(self) -> Optional[Dict[Any, Any]]:
        """
        Find the next active BTC 5-minute market.
        The active market timestamp is the NEXT 5-minute interval (rounded up).
        """
        current_timestamp = self.get_current_timestamp()
        market_timestamp = ((current_timestamp + 299) // 300) * 300
        slug = self.generate_slug(market_timestamp)
        market = self.find_active_market(slug)
        
        if market:
            print(f"Found Next active market: {slug}")
            return market
        
        print(f"No Next active market found for timestamp: {market_timestamp}")
        return None

    def find_current_market(self) -> Optional[Dict[Any, Any]]:
        """
        Find the current active BTC 5-minute market.
        The active market timestamp is the NEXT 5-minute interval (rounded up).
        
        Example: If current timestamp is 1770887393, active market is 1770887400
        
        Returns:
            Market data dictionary or None if not found
        """
        current_timestamp = self.get_current_timestamp()
        
        # Round UP to next 5-minute interval
        # 5 minutes = 300 seconds
        # Formula: ((timestamp + 299) // 300) * 300
        market_timestamp = ((current_timestamp) // 300) * 300
        
        slug = self.generate_slug(market_timestamp)
        market = self.find_active_market(slug)
        self.market = market.get("markets")[0].get("conditionId")
        if market:
            print(f"Found current active market: {slug}")
            return market
        
        print(f"No Next active market found for timestamp: {market_timestamp}")
        return None
    
    
    def place_market_order(
        self,
        token_id: str,
        side: str,
        size: float
    ) -> Optional[Dict[Any, Any]]:
        """
        Place a market order on Polymarket CLOB
        """
        if not self.client:
            print("Error: CLOB client not initialized.")
            print("Possible reasons:")
            print("  - Private key not provided or invalid")
            print("  - py-clob-client not installed (pip install py-clob-client)")
            print("  - CLOB client initialization failed (check error messages above)")
            return None

        if side.upper() not in ["BUY", "SELL"]:
            print(f"Error: Invalid side '{side}'. Must be 'BUY' or 'SELL'")
            return None
        
        try:
            # Create OrderArgs object for market order
            # MarketOrderArgs might be the same as OrderArgs or a separate class
            order = MarketOrderArgs(
                token_id=token_id,
                amount=float(size),
                side=BUY if side.upper() == "BUY" else SELL,
                order_type=OrderType.FOK
            )
                # Use OrderArgs if MarketOrderArgs is not available
            # Create signed order
            signed = self.client.create_market_order(order)

            # Post order with order type
            resp = self.client.post_order(signed, OrderType.FOK)
            
            print(f"Order placed successfully: {resp}")
            return resp
                
        except Exception as e:
            print(f"Error placing order: {e}")
            import traceback
            traceback.print_exc()
            return None 
    
    def place_limit_order(
        self,
        token_id: str,
        side: str,
        price: float,
        size: float,
        order_type: str = "LIMIT"
    ) -> Optional[Dict[Any, Any]]:
        """
        Place a limit order on Polymarket CLOB
        
        Args:
            token_id: The token ID to trade (up_token_id or down_token_id)
            side: "BUY" or "SELL"
            price: Price per share (0.0 to 1.0)
            size: Size of the order
            order_type: Order type, default "LIMIT"
            
        Returns:
            Order response dictionary or None if failed
        """
        if not self.client:
            print("Error: CLOB client not initialized.")
            print("Possible reasons:")
            print("  - Private key not provided or invalid")
            print("  - py-clob-client not installed (pip install py-clob-client)")
            print("  - CLOB client initialization failed (check error messages above)")
            return None
        
        if side.upper() not in ["BUY", "SELL"]:
            print(f"Error: Invalid side '{side}'. Must be 'BUY' or 'SELL'")
            return None
        
        if not (0.0 <= price <= 1.0):
            print(f"Error: Price must be between 0.0 and 1.0, got {price}")
            return None
        
        try:
            # Convert order_type to valid CLOB order type
            # Valid types: "GTC" (Good Till Cancelled), "FOK" (Fill or Kill), "IOC" (Immediate or Cancel
            # Create OrderArgs object
            # Note: OrderArgs has defaults for fee_rate_bps=0, nonce=0, expiration=0, taker=ZERO_ADDRESS
            order = OrderArgs(
                token_id=token_id,
                price=float(price),
                size=float(size),
                side=BUY if side.upper() == "BUY" else SELL  # Must be "BUY" or "SELL" (uppercase)
            )

            # Create signed order
            signed = self.client.create_order(order)

            # Post order with order type
            resp = self.client.post_order(signed, OrderType.GTC)
            
            print(f"Order placed successfully: {resp}")
            return resp
                
        except Exception as e:
            print(f"Error placing order: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def place_limit_order_up(
        self,
        token_ids: Dict[str, str],
        price: float,
        size: float,
        side: str = "BUY"
    ) -> Optional[Dict[Any, Any]]:
        """
        Place a limit order for the Up token
        
        Args:
            token_ids: Dictionary with 'up_token_id' and 'down_token_id'
            price: Price per share (0.0 to 1.0)
            size: Size of the order
            side: "BUY" or "SELL", default "BUY"
            
        Returns:
            Order response dictionary or None if failed
        """
        if not token_ids or 'up_token_id' not in token_ids:
            print("Error: up_token_id not found in token_ids")
            return None
        
        return self.place_limit_order(
            token_id=token_ids['up_token_id'],
            side=side,
            price=price,
            size=size
        )
    
    def place_limit_order_down(
        self,
        token_ids: Dict[str, str],
        price: float,
        size: float,
        side: str = "BUY"
    ) -> Optional[Dict[Any, Any]]:
        """
        Place a limit order for the Down token
        
        Args:
            token_ids: Dictionary with 'up_token_id' and 'down_token_id'
            price: Price per share (0.0 to 1.0)
            size: Size of the order
            side: "BUY" or "SELL", default "BUY"
            
        Returns:
            Order response dictionary or None if failed
        """
        if not token_ids or 'down_token_id' not in token_ids:
            print("Error: down_token_id not found in token_ids")
            return None
        
        return self.place_limit_order(
            token_id=token_ids['down_token_id'],
            side=side,
            price=price,
            size=size
        )

    def place_cancel_order(
        self,
        order_id: str
    ) -> Optional[Dict[Any, Any]]:

        """
        Cancel an order on Polymarket CLOB
        """
        if not self.client:
            print("Error: CLOB client not initialized.")
            return None
        
        return self.client.cancel_order(order_id, OrderType.IOC)   
         
    def merge_tokens(
        self,
        token_ids: Dict[str, str],
        amount: int,
        condition_id: str
    ) -> Optional[Dict[Any, Any]]:
        if not self.relayer_client:
            print("Error: Relayer client not initialized. Cannot merge tokens.")
            return None

        if not WEB3_AVAILABLE or Web3 is None:
            print("Error: Web3 not available. Cannot merge tokens.")
            return None

        try:
            client = self.relayer_client
            merge_abi = [{
            "name": "mergePositions",
            "type": "function",
            "inputs": [
                {"name": "collateralToken", "type": "address"},
                {"name": "parentCollectionId", "type": "bytes32"},
                {"name": "conditionId", "type": "bytes32"},
                {"name": "partition", "type": "uint256[]"},
                {"name": "amount", "type": "uint256"}
            ],
            "outputs": []
            }]

            # Ensure condition_id has 0x prefix
            if not condition_id.startswith("0x"):
                condition_id = "0x" + condition_id

            # Create Web3 instance for encoding (no provider needed for encoding)
            w3 = Web3()
            contract = w3.eth.contract(
                address="0x4D97DCd97eC945f40cF65F87097ACe5EA0476045", 
                abi=merge_abi
            )
            
            # Use encodeABI (camelCase) which is the correct method name in web3.py
            encoded_data = contract.encodeABI(
                fn_name="mergePositions",
                args=["0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", bytes(32), condition_id, [1, 2], amount]
            )

            merge_tx = {
                "to": "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045",
                "data": encoded_data,
                "value": "0"
            }

            response = client.execute([merge_tx], "Merge positions")
            response.wait()
            print(f"Merge transaction hash: {response.transaction_hash}")
            print("Merge complete!")
            return response
        except Exception as e:
            print(f"Error merging tokens: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    
    def get_balance(self, token_id: str) -> float:
        """
        Get balance for a specific token
        
        Args:
            token_id: Token ID to check balance for
            
        Returns:
            Balance as float, or 0.0 if error
        """
        if not self.client:
            return 0.0
        params = {
            "market": self.market,
            "status": "OPEN",
            "limit": 50,
            "user": os.getenv("FUNDER")
        }
        url = os.getenv("GET_POSITION_URL")
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.text != []:
                data = response.json()
                if data[0]["token"] == token_id:
                    return float(data[0]["positions"][0]["size"])
                else:
                    return float(data[1]["positions"][0]["size"])
            else:
                print("No data found for token_id: ", token_id)
                return 0.0
        except Exception as e:

                return 0.0
   
    
    def get_positions(self, token_ids: Dict[str, str]) -> Dict[str, float]:
        """
        Get positions (balances) for both UP and DOWN tokens
        
        Args:
            token_ids: Dictionary with 'up_token_id' and 'down_token_id'
            
        Returns:
            Dictionary with 'up_balance' and 'down_balance'
        """
        if not token_ids:
            return {"up_balance": 0.0, "down_balance": 0.0}
        
        up_balance = self.get_balance(token_ids.get("up_token_id"))
        down_balance = self.get_balance(token_ids.get("down_token_id"))
        print("up_balance", up_balance * 10 ** 6)
        print("down_balance", down_balance * 10 ** 6)
        return {
            "up_balance": up_balance,
            "down_balance": down_balance
        }
    
    def get_market_close_time(self, market: Optional[Dict[Any, Any]] = None) -> Optional[int]:
        """
        Get market close/expiration timestamp
        
        Args:
            market: Market data dictionary. If None, uses find_current_market()
            
        Returns:
            Unix timestamp of market close, or None if not found
        """
        if market:
            
            dt = datetime.fromisoformat(market.get("endDate").replace("Z", "+00:00"))
            return dt.timestamp()
        else:
            return None 
    
    def force_sell_all(self, token_ids: Dict[str, str]) -> Dict[str, Optional[Dict[Any, Any]]]:
        """
        Force sell all positions using market orders
        
        Args:
            token_ids: Dictionary with 'up_token_id' and 'down_token_id'
            
        Returns:
            Dictionary with 'up_order' and 'down_order' results
        """
        positions = self.get_positions(token_ids)
        results = {"up_order": None, "down_order": None}
        
        # Sell UP tokens if any
        if positions["up_balance"] > 0:
            print(f"🔄 Force selling {positions['up_balance']:.6f} UP tokens...")
            results["up_order"] = self.place_market_order(
                token_id=token_ids["up_token_id"],
                side="SELL",
                size=positions["up_balance"]
            )
        
        # Sell DOWN tokens if any
        if positions["down_balance"] > 0:
            print(f"🔄 Force selling {positions['down_balance']:.6f} DOWN tokens...")
            results["down_order"] = self.place_market_order(
                token_id=token_ids["down_token_id"],
                side="SELL",
                size=positions["down_balance"]
            )
        
        return results



