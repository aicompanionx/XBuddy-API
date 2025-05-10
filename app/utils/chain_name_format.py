import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# SDK supported blockchain mapping table
SDK_SUPPORTED_CHAINS = {
    "ethereum": "1",
    "bsc": "56",
    "arbitrum": "42161",
    "polygon": "137",
    "zksync era": "324",
    "linea mainnet": "59144",
    "base": "8453",
    "scroll": "534352",
    "optimism": "10",
    "avalanche": "43114",
    "fantom": "250",
    "cronos": "25",
    "okc": "66",
    "heco": "128",
    "gnosis": "100",
    "tron": "tron",
    "kcc": "321",
    "fon": "201022",
    "mantle": "5000",
    "opbnb": "204",
    "zkfair": "42766",
    "blast": "81457",
    "manta pacific": "169",
    "berachain": "80094",
    "abstract": "2741",
    "hashkey chain": "177",
    "sonic": "146",
    "story": "1514"
}

# API supported blockchain mapping table
API_SUPPORTED_CHAINS = {
    "ethereum": "1",
    "bsc": "56",
    "arbitrum": "42161",
    "polygon": "137",
    "opbnb": "204",
    "zksync era": "324",
    "linea mainnet": "59144",
    "base": "8453",
    "mantle": "5000",
    "scroll": "534352",
    "optimism": "10",
    "avalanche": "43114",
    "fantom": "250",
    "cronos": "25",
    "heco": "128",
    "gnosis": "100",
    "tron": "tron",
    "kcc": "321",
    "fon": "201022",
    "zkfair": "42766",
    "soneium": "1868",
    "story": "1514",
    "sonic": "146",
    "abstract": "2741",
    "hashkey": "177",
    "berachain": "80094",
    "monad": "10143",
    "world chain": "480",
    "morph": "2818",
    "gravity": "1625",
    "zircuit": "48899",
    "x layer mainnet": "196",
    "zklink nova": "810180",
    "bitlayer mainnet": "200901",
    "merlin": "4200",
    "manta pacific": "169",
    "blast": "81457",
    
    "okc": "66",
    "ethw": "10001",
}

SUPPORTED_CHAINS = {*SDK_SUPPORTED_CHAINS.keys(), *API_SUPPORTED_CHAINS.keys(), "solana", "sui"}

# Blockchain name standardization mapping table
CHAIN_NAME_MAPPING: Dict[str, str] = {
    # Main blockchain
    "eth": "ethereum",
    "ether": "ethereum",
    "ethereum": "ethereum",
    
    "bsc": "bsc",
    "bnb": "bsc",
    "binance": "bsc",
    "binance smart chain": "bsc",
    
    "arb": "arbitrum",
    "arbitrum": "arbitrum",
    "arbitrum one": "arbitrum",
    
    "matic": "polygon",
    "polygon": "polygon",
    
    "op": "optimism",
    "optimism": "optimism",
    
    "avax": "avalanche",
    "avalanche": "avalanche",
    
    "ftm": "fantom",
    "fantom": "fantom",
    
    "sol": "solana",
    "solana": "solana",
    
    "sui": "sui",
    
    # Other blockchain
    "zksync": "zksync era",
    "zksync era": "zksync era",
    "era": "zksync era",
    
    "linea": "linea mainnet",
    "linea mainnet": "linea mainnet",
    
    "base": "base",
    
    "scroll": "scroll",
    
    "cronos": "cronos",
    "cro": "cronos",
    
    "okc": "okc",
    "okx": "okc",
    
    "heco": "heco",
    "huobi": "heco",
    
    "gnosis": "gnosis",
    "xdai": "gnosis",
    
    "ethw": "ethw",
    
    "tron": "tron",
    "trx": "tron",
    
    "kcc": "kcc",
    
    "fon": "fon",
    
    "mantle": "mantle",
    
    "opbnb": "opbnb",
    
    "zkfair": "zkfair",
    
    "blast": "blast",
    
    "manta": "manta pacific",
    "manta pacific": "manta pacific",
    
    "bera": "berachain",
    "berachain": "berachain",
    
    "abstract": "abstract",
    
    "hashkey": "hashkey",
    "hashkey chain": "hashkey chain",
    
    "sonic": "sonic",
    
    "story": "story",
    
    "soneium": "soneium",
    
    "monad": "monad",
    
    "world": "world chain",
    "world chain": "world chain",
    
    "morph": "morph",
    
    "gravity": "gravity",
    
    "zircuit": "zircuit",
    
    "xlayer": "x layer mainnet",
    "x layer": "x layer mainnet",
    "x layer mainnet": "x layer mainnet",
    
    "zklink": "zklink nova",
    "zklink nova": "zklink nova",
    
    "bitlayer": "bitlayer mainnet",
    "bitlayer mainnet": "bitlayer mainnet",
    
    "merlin": "merlin"
}

def normalize_chain_name(chain_name: str) -> Optional[str]:
    """
    Normalize the blockchain name to the supported format
    """
    if not chain_name:
        return None
    
    # Convert to lowercase and remove leading and trailing spaces
    normalized = chain_name.lower().strip()
    
    # Directly look up the mapping table
    if normalized in CHAIN_NAME_MAPPING:
        return CHAIN_NAME_MAPPING[normalized]
    
    # Check if it is already a standard name
    if normalized in SUPPORTED_CHAINS:
        return normalized
    
    # Try partial matching
    for standard_name in SUPPORTED_CHAINS:
        if normalized in standard_name or standard_name in normalized:
            return standard_name
    
    return chain_name   
