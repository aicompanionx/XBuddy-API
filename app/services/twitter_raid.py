import random

from app.utils.chain_name_format import normalize_chain_name
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Define a dictionary of push objects for each chain
push_objects = {
    "bsc": [
        # {"name": "Binance CEO: CZ", "url": "https://twitter.com/cz_binance"},
        # {"name": "Binance CEO: He Yi", "url": "https://twitter.com/heyibinance"},
        {"name": "BNB Chain", "url": "https://twitter.com/BNBCHAIN"},
        {"name": "Binance Wallet", "url": "https://twitter.com/BinanceWallet"},
        {"name": "Binance", "url": "https://twitter.com/binance"}
    ],
    "solana": [
        {"name": "Solana CEO: Anatoly Yakovenko", "url": "https://twitter.com/aeyakovenko"},
        {"name": "Solana Official", "url": "https://twitter.com/solana"},
        {"name": "a16z Founder: Marc Andreessen", "url": "https://twitter.com/pmdf"},
        {"name": "pump.fun", "url": "https://twitter.com/pumpdotfun"}
    ],
    "base": [
        {"name": "Coinbase CEO: Brian Armstrong", "url": "https://twitter.com/brian_armstrong"},
        {"name": "BASE Chain Founder: Jesse Pollak", "url": "https://twitter.com/jessepollak"},
        {"name": "BASE Ecosystem Lead: David Tso", "url": "https://twitter.com/davidtsocy"},
        {"name": "BASE Developer Lead: Xen BH", "url": "https://twitter.com/XenBH"}
    ],
    "ethereum": [
        {"name": "ETH Founder: Vitalik Buterin", "url": "https://twitter.com/VitalikButerin"},
        {"name": "ETH Co-Founder: Joseph Lubin", "url": "https://twitter.com/ethereumJoseph"}
    ],
    "trx": [
        {"name": "Justin Sun", "url": "https://twitter.com/justinsuntron"}
    ],
    "ripple": [
        {"name": "Ripple CEO: Brad Garlinghouse", "url": "https://twitter.com/bgarlinghouse"}
    ]
}

# Define a list of generic push objects
generic_push_objects = [
    {"name": "Elon Musk", "url": "https://twitter.com/elonmusk"},
    {"name": "Elon Musk's mom", "url": "https://twitter.com/mayemusk"},
    # {"name": "MicroStrategy CEO: Michael Saylor", "url": "https://twitter.com/saylor"},
    # {"name": "Three Arrows Capital Founder:", "url": "https://twitter.com/zhusu"},
    # {"name": "Chart master: WolfyXBT", "url": "https://twitter.com/Wolfy_XBT"},
    # {"name": "Meemcoin top trader: OX SUN", "url": "https://twitter.com/0xSunNFT"},
    # {"name": "Meemcoin top trader: CryptoD | 1000X GEM", "url": "https://twitter.com/CryptoDevinL"},
    # {"name": "Meemcoin top trader: 0xWizard", "url": "https://twitter.com/0xcryptowizard"},
    # {"name": "Meemcoin top trader:  brc20niubi", "url": "https://twitter.com/brc20niubi"},
    # {"name": "Meemcoin top trader: hexiecs", "url": "https://twitter.com/hexiecs"},
    # {"name": "Meemcoin top trader: coldguy", "url": "https://twitter.com/coldguy"}
]

# Design the selection algorithm


def get_random_raid_object(chain_name: str) -> dict:
    """
    Return a random push object (name and url) based on the given chain name.

    Rules:
    1. If the chain name is known (BNB, Solana, BASE, ETH, TRX, Ripple):
       - 50% probability to select from the specific list of that chain.
       - 50% probability to select from the generic list.
    2. If the chain name is unknown (other chains):
       - 100% probability to select from the generic list.
    """
    chain = normalize_chain_name(chain_name)

    specific_list = push_objects.get(chain)

    if specific_list:
        # Known chain: 50% specific vs 50% generic
        if random.random() < 0.5:
            # Select from specific list
            logger.info(f"Selecting {chain.upper()} specific list")
            return random.choice(specific_list)
        else:
            # Select from generic list
            logger.info("Selecting generic list")
            return random.choice(generic_push_objects)
    else:
        logger.info(f"Chain '{chain_name}' is unknown, selecting generic list")
        return random.choice(generic_push_objects)
