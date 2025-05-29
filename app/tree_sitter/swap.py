import requests
from typing import Dict, List
import os
import json
from functools import lru_cache
import logging
from utils.general import similarity_score
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")
COINGECKO_BASE_URL = os.getenv('COINGECKO_BASE_URL')
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

class TokenService:
    """
    Resolves token names to symbols and selects the most popular token from a list.
    """

    def __init__(self):

        self.TOKEN_MAP = {
            "tether": "USDT",
            "bitcoin": "BTC",
            "ethereum": "ETH",
            "tron": "TRX",
            "solana": "SOL",
            "litecoin": "LTC",
            "ripple": "XRP",
            "binance coin": "BNB",
            "cardano": "ADA",
            "polkadot": "DOT",
            "dogecoin": "DOGE",
        }
        self._available_tokens = None
        self._available_chains = None

    @property
    def available_tokens(self):
        if not self._available_tokens:
            self.fetch_available_metadata()
        return self._available_tokens
    
    @property
    def available_chains(self):
        if not self._available_chains:
            self.fetch_available_metadata()
        return self._available_chains

    @staticmethod
    @lru_cache(maxsize=None)
    def _search_token_name(name: str)->List[str]|None:
        try:
            url = f"{COINGECKO_BASE_URL}/search"
            headers = {
                "accept": "application/json",
                "x-cg-api-key": COINGECKO_API_KEY
            }
            params = {'query': name} 
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            response = response.json()
            
            coins = response['coins']
            if len(coins) > 0:
                return coins
            return None        
            
        except json.JSONDecodeError as e:
            raise ValueError(f"failed to get symbol from api: {str(e)}")
        except requests.HTTPError:
            raise ValueError(f"failed to get symbol from api due to network error.")    

    def token_name_to_symbol(self, token_name: str) -> str:
        """
        Converts a human-readable token name to its symbol.
        """
        token_name_lower = token_name.lower()
        if token_name_lower in self.TOKEN_MAP:
            return self.TOKEN_MAP[token_name_lower]
        elif token_name in self.TOKEN_MAP.values():
            return token_name
        else:
            result = TokenService._search_token_name(token_name)
            if result:
                return result[0]['symbol']
            logger.warning(f"No token with name {token_name} found")

    @staticmethod
    def find_first_popular_token(candidates: List[Dict]) -> Dict:
        """
        Selects the first popular token from a list of candidates.
        """
        for token in candidates:
            if token["isPopular"]:
                return token
        return candidates[0] if candidates else {}

    @staticmethod
    def find_token_with_blockchain(candidates: List[Dict], blockchain: str) -> Dict:
        most_similar_token = None
        most_similar_score = 0
        for token in candidates:
            sim_score = similarity_score(token["blockchain"], blockchain)
            if sim_score > most_similar_score:
                most_similar_score = sim_score
                most_similar_token = token
        return most_similar_token


    def fetch_available_metadata(self) -> None:
        """
        Retrieves the available tokens and blockchains from the API.

        Returns:
            set: A set of available tokens and blockchains

        """
        try:
            response = requests.get(f"{BASE_URL}/basic/meta", params={"apiKey": API_KEY}, timeout=10)
            response.raise_for_status()
            response = response.json()

            token_map = {}
            blockchains = []
            for token in response["tokens"]:
                sym = token["symbol"]
                if sym not in token_map:
                    token_map[sym] = [token]
                else:
                    token_map[sym].append(token)

            for blockchain in response['blockchains']:
                blockchains.append({
                    'name': blockchain['name'],
                    'displayName': blockchain['displayName']
                })

            self._available_tokens = token_map
            self._available_chains = blockchains
        except Exception as e:
            logger.error(
                f"A problem occurred fetching available assets: {str(e)}"
            )
class BlockchainService:
    def __init__(self, available_blockchains):
        self.blockchains = available_blockchains

    def search_blockchains(self, query: str, limit: int = 1) -> List[Dict]:
        """
        Search blockchains by name, chain, shortName, or chainSlug with sophisticated matching.
        
        Args:
            query: The search query string
            limit: Maximum number of results to return (default 5)
            
        Returns:
            List of matching blockchain objects sorted by relevance score
        """
        query = query.lower().strip()
        
        # Short-circuit for empty query
        if not query:
            return [chain for chain in self.blockchains[:limit]]
        
        # Preprocess the query for better matching
        query_parts = re.split(r'[ -_.]', query)
        query_parts = [part for part in query_parts if part]
        
        # Calculate scores for each blockchain
        scored_chains = []
        for chain in self.blockchains:
            # Initialize score components
            exact_match_score = 0
            partial_match_score = 0
            fuzzy_match_score = 0
            
            # Fields to check
            fields = [
                chain.get("name", "").lower(),
                chain.get("displayName", "").lower(),
            ]
            
            # Check for exact matches (highest priority)
            for field in fields:
                if field == query:
                    exact_match_score = 100  # Perfect match gets maximum score
                    break
                
                # Check if any field starts with the query
                if field.startswith(query):
                    exact_match_score = max(exact_match_score, 80)
                
                # Check if query starts with the field
                elif query.startswith(field):
                    exact_match_score = max(exact_match_score, 60)
            
            # Check for partial matches (medium priority)
            for field in fields:
                field_parts = re.split(r'[ -_.]', field)
                field_parts = [part for part in field_parts if part]
                
                # Check if any part is an exact match
                for part in field_parts:
                    if part == query:
                        partial_match_score = max(partial_match_score, 50)
                    
                    # Check if any query part matches a field part
                    for q_part in query_parts:
                        if q_part == part:
                            partial_match_score = max(partial_match_score, 40)
                        elif part.startswith(q_part) and len(q_part) >= 2:
                            partial_match_score = max(partial_match_score, 30)
            
            # Calculate fuzzy match scores (lowest priority)
            for field in fields:
                # Only consider fuzzy matching if the field isn't too long compared to query
                if len(field) <= max(len(query) * 3, 30):
                    score = similarity_score(query, field) * 25  # Max 25 points for fuzzy matching
                    fuzzy_match_score = max(fuzzy_match_score, score)
            
            # Total score (exact has priority, then partial, then fuzzy)
            total_score = exact_match_score + partial_match_score + fuzzy_match_score
            
            # Give higher score to main blockchains (based on common knowledge)
            main_chains = ["ethereum", "bitcoin", "binance", "polygon", "solana", "tron", "avalanche"]
            for main in main_chains:
                if main in str(fields).lower():
                    total_score += 5
                    break
            
            # Store score with chain
            scored_chains.append((total_score, chain))
        
        # Sort by score (descending) and return the chains
        scored_chains.sort(reverse=True, key=lambda x: x[0])
        
        # Return top results with their chains
        return list(chain['name'] for score, chain in scored_chains[:limit])  
    
class WalletService:
    """
    Handles wallet-related operations such as fetching the user's wallet address.
    """

    def fetch_user_wallet_address(self, token: str) -> str:
        """
        Retrieves the current user's wallet address.

        Args:
            token: API token to authenticate the request.

        Returns:
            str: The user's wallet address.

        Raises:
            ValueError: If the wallet address is not found or the API call fails.
        """
        try:
            response = requests.get(
                f"{BASE_URL}/user/wallet", params={"token": token}, timeout=5
            )
            response.raise_for_status()
            data = response.json()
            address = data.get("address")
            if not address:
                print("Wallet address not found.")
            logger.info(f"Fetched wallet address: {address}")
            return address
        except Exception as e:
            logger.error(
                f"A problem occurred fetching the user's wallet address. error: {str(e)}"
            )
            return None


class BalanceService:
    """
    Handles balance-related operations such as fetching token balances.
    """

    def fetch_user_balance(
        self, symbol: str, blockchain: str, wallet_address: str
    ) -> int:
        """
        Retrieves the user's token balance from a specified blockchain.

        Args:
            symbol: Token symbol (e.g., 'BTC').
            blockchain: Name of the blockchain.
            wallet_address: Address to query.

        Returns:
            int: The balance of the token.

        Raises:
            ValueError: If the API call fails.
        """
        try:
            response = requests.get(
                f"{BASE_URL}/basic/token-balance",
                params={
                    "blockchain": blockchain,
                    "symbol": symbol,
                    "walletAddress": wallet_address,
                },
            )
            response.raise_for_status()
            data = response.json()
            return float(data["balance"])
        except Exception as e:
            logger.error(f"A problem occurred fetching the user balance. error: {str(e)}")


class SwapService:
    """
    Handles cross-chain token swaps and all related validations.
    """

    def __init__(self):
        self.token_resolver = TokenService()
        self.wallet_service = WalletService()
        self.balance_service = BalanceService()
        self.available_tokens = self.token_resolver.available_tokens
        self.blockchain_service = BlockchainService(self.token_resolver.available_chains)

    def validate_amount(self, amount: int) -> None:
        """
        Ensures the amount is a positive integer.

        Args:
            amount: Amount to validate.

        Raises:
            ValueError: If amount is not positive.
        """
        if amount <= 0:
            logger.error("amount must be a positive number.")

    def resolve_token_info(self, token_name: str, token_blockchain: str) -> Dict:
        """
        Resolves token info by name.

        Args:
            token_name: Human-readable token name.

        Returns:
            dict: Token information.

        Raises:
            ValueError: If no valid token info is found.
        """
        symbol = self.token_resolver.token_name_to_symbol(token_name)
        candidates = self.available_tokens.get(symbol)
        if not candidates:
            raise ValueError(f"no token found with name: {token_name} and symbol: {symbol}")
        
        if not token_blockchain:
            token = TokenService.find_first_popular_token(candidates)
        else:
            token = TokenService.find_token_with_blockchain(
                candidates, token_blockchain
            )
        if not token:
            logger.error(f"No token found with token name: {token_name} with blockchain: {token_blockchain}")

        return token

    def validate_user_balance(
        self, wallet_address: str, token: Dict, amount: int
    ) -> None:
        """
        Checks if user has sufficient balance.

        Args:
            wallet_address: User's wallet address.
            token: Token information.
            amount: Amount to check.

        Raises:
            ValueError: If balance is insufficient.
        """
        balance = self.balance_service.fetch_user_balance(
            symbol=token["symbol"],
            blockchain=token["blockchain"],
            wallet_address=wallet_address,
        )
        if balance < amount:
            logger("Insufficient source token balance for swap.")

    def build_transaction_params(
        self,
        source_token: Dict,
        destination_token: Dict,
        from_address: str,
        to_address: str,
        amount: int,
    ) -> Dict:
        """
        Builds transaction parameters for the swap API.

        Returns:
            dict: Parameters for swap request.
        """
        result = {
            "fromToken": source_token["symbol"],
            "fromBlockchain": source_token["blockchain"],
            "fromTokenAddress": source_token["address"],
            "toToken": destination_token["symbol"],
            "toBlockchain": destination_token["blockchain"],
            "toTokenAddress": destination_token["address"],
            "fromAmount": amount,
        }
        if to_address:
            result["to_address"] = to_address
        if from_address:
            result["fromAddress"]= from_address
            
        return result

    @staticmethod
    def create_rango_url(swap_params: dict) -> str:
        is_native = lambda address: address != None

        return (
            f"https://app.rango.exchange/bridge/?"
            f"fromBlockchain={swap_params['fromBlockchain']}"
            f"&fromToken={swap_params['fromToken']}{'--'+swap_params['fromTokenAddress'] if is_native(swap_params['fromTokenAddress']) else ''}"
            f"&toBlockchain={swap_params['toBlockchain']}"
            f"&toToken={swap_params['toToken']}{'--'+swap_params['toTokenAddress'] if is_native(swap_params['toTokenAddress']) else ''}"
            f"&fromAmount={swap_params['fromAmount']}"
        )

    def create_swap_transaction(
        self,
        source_token: str,
        source_blockchain: str | None,
        destination_token: str,
        destination_blockchain: str | None,
        destination_address: str,
        amount: int,
    ) -> tuple[str, bool]:
        """
        Args:
            source_token: Token to send (e.g. 'tron').
            destination_token: Token to receive (e.g. 'bitcoin').
            destination_address: Recipient wallet address on destination chain.
            amount: Amount of source token to swap (must be positive).

        Returns:
            str: Link redirecting user to the transaction confirmation page
        """
        self.validate_amount(amount)
        source_token_info = self.resolve_token_info(source_token, source_blockchain)
        destination_token_info = self.resolve_token_info(destination_token, destination_blockchain)

        if not source_token_info or not destination_token_info:
            logger.warning("Invalid token info.")
            return None, False
        
        params = self.build_transaction_params(
            source_token=source_token_info,
            destination_token=destination_token_info,
            from_address=None,
            to_address=destination_address,
            amount=amount,
        )

        return self.create_rango_url(params), True
