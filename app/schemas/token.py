from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.base import ApiBase

# ======================================================================
# Get CA from Twitter
# ======================================================================


class CAFromTwitterRequest(BaseModel):
    """
    Get CA from Twitter request
    """

    twitter_name: str = Field(..., description="Twitter username")


class CAFromTwitterData(BaseModel):
    """
    Get CA from Twitter response
    """

    chain: str = Field(..., description="Chain name")
    ca: str = Field(..., description="Contract address")


class CAFromTwitterResponse(ApiBase[CAFromTwitterData]):
    """
    Get CA from Twitter response
    """

    pass


# ======================================================================
# Get Twitter from CA
# ======================================================================


class TwitterFromCARequest(BaseModel):
    """
    Get Twitter from CA request
    """

    ca: str = Field(..., description="Contract address")


class TwitterFromCAData(BaseModel):
    """
    Get Twitter from CA response
    """

    twitter_name: str = Field(..., description="Twitter username")


class TwitterFromCAResponse(ApiBase[TwitterFromCAData]):
    """
    Get Twitter from CA response
    """

    pass


# ======================================================================
# Token security check
# ======================================================================


class CheckTokenRequest(BaseModel):
    """
    Token security check request
    """

    chain: str = Field(..., description="Chain name")
    ca: str = Field(..., description="Contract address")


class RiskOptions(BaseModel):
    """
    Risk options
    """

    is_open_source: bool = Field(False, description="Is the contract open source?")
    is_proxy: bool = Field(False, description="Is there a proxy contract?")
    is_mintable: bool = Field(False, description="Is the token mintable?")
    can_take_back_ownership: bool = Field(
        False, description="Can the owner take back ownership?"
    )
    owner_change_balance: bool = Field(
        False, description="Can the owner change the balance?"
    )
    hidden_owner: bool = Field(False, description="Is there a hidden owner?")
    selfdestruct: bool = Field(False, description="Can the contract self-destruct?")
    external_call: bool = Field(
        False, description="Is there an external contract call?"
    )
    gas_abuse: bool = Field(False, description="Is there a gas abuse?")
    buy_tax: float = Field(0, description="Buy tax rate")
    sell_tax: float = Field(0, description="Sell tax rate")
    is_honeypot: bool = Field(False, description="Is the token a honeypot?")
    transfer_pausable: bool = Field(False, description="Is the transfer pausable?")
    cannot_sell_all: bool = Field(
        False, description="Can the owner sell all the tokens?"
    )
    cannot_buy: bool = Field(False, description="Can the owner buy tokens?")
    trading_cooldown: bool = Field(False, description="Is there a trading cooldown?")
    is_anti_whale: bool = Field(False, description="Is the token anti-whale?")
    anti_whale_modifiable: bool = Field(
        False, description="Is the anti-whale modifiable?"
    )
    slippage_modifiable: bool = Field(False, description="Is the slippage modifiable?")
    is_blacklisted: bool = Field(False, description="Is the token blacklisted?")
    is_whitelisted: bool = Field(False, description="Is the token whitelisted?")
    personal_slippage_modifiable: bool = Field(
        False, description="Is the personal slippage modifiable?"
    )
    # Basic information
    token_name: Optional[str] = Field(None, description="Token name")
    token_symbol: Optional[str] = Field(None, description="Token symbol")
    total_supply: Optional[str] = Field(None, description="Total supply")
    holder_count: Optional[str] = Field(None, description="Holder count")
    top_holders_percent: Optional[float] = Field(
        None, description="Top 10 holders percent"
    )


class CheckTokenData(BaseModel):
    """
    Token security check response
    """

    chain: str = Field(..., description="Chain name")
    ca: str = Field(..., description="Contract address")
    risks: Optional[RiskOptions] = Field(..., description="Risk options")


class CheckTokenResponse(ApiBase[CheckTokenData]):
    """
    Token security check response
    """

    pass


# ======================================================================
# SOL token security check
# ======================================================================


class CheckSOLTokenRequest(BaseModel):
    """
    SOL token security check request
    """

    ca: str = Field(..., description="Contract address")


class SOLRiskOptions(BaseModel):
    """
    SOL token risk options
    """

    is_mintable: bool = Field(False, description="Is the token mintable?")
    metadata_mutable: bool = Field(False, description="Is the metadata mutable?")
    freezable: bool = Field(False, description="Is the token freezable?")
    closable: bool = Field(False, description="Is the token closable?")
    non_transferable: bool = Field(False, description="Is the token non-transferable?")
    balance_mutable: bool = Field(False, description="Is the balance mutable?")
    transfer_fee: float = Field(0, description="Transfer fee")
    transfer_fee_upgradable: bool = Field(
        False, description="Is the transfer fee upgradable?"
    )
    transfer_hook: bool = Field(False, description="Is there a transfer hook?")
    default_account_state: str = Field("", description="Default account state")

    # Token basic information
    symbol: Optional[str] = Field(None, description="Token symbol")
    name: Optional[str] = Field(None, description="Token name")
    description: Optional[str] = Field(None, description="Token description")
    total_supply: Optional[str] = Field(None, description="Total supply")
    holder_count: Optional[str] = Field(None, description="Holder count")

    # Top 10 holders information
    top_holders_percent: Optional[float] = Field(
        None, description="Top 10 holders percent"
    )
    holders: Optional[list] = Field(None, description="Top 10 holders")

    # Dex information
    dex: Optional[list] = Field(None, description="Dex information")

    # Security rating
    trusted_token: Optional[int] = Field(None, description="Is the token trusted?")


class CheckSOLTokenData(BaseModel):
    """
    SOL token security check response
    """

    ca: str = Field(..., description="Contract address")
    risks: Optional[SOLRiskOptions] = Field(..., description="SOL token risk options")


class CheckSOLTokenResponse(ApiBase[CheckSOLTokenData]):
    """
    SOL token security check response
    """

    pass


# ======================================================================
# Token pairs information
# ======================================================================


class TokenPairsRequest(BaseModel):
    """
    Token pairs request
    """

    chain: str = Field(default="solana", description="Chain name")
    pa: str = Field(..., description="Pool address")


class TokenInfo(BaseModel):
    """
    Token information
    """

    ca: str = Field(..., description="Main token contract address")
    name: str = Field(..., description="Token name")
    symbol: str = Field(..., description="Token symbol")
    twitter: str = Field(..., description="Twitter link")
    imageUrl: str = Field(..., description="Logo URL")
    marketCap: int = Field(..., description="Market capitalization")
    priceUsd: float = Field(..., description="Price in USD")


class TokenPairsData(BaseModel):
    """
    Token pairs response
    """

    pa: str = Field(..., description="Pool address")
    token: TokenInfo = Field(..., description="Token information")


class TokenPairsResponse(ApiBase[TokenPairsData]):
    """
    Token pairs response
    """

    pass


# ======================================================================
# Get token details
# ======================================================================
class TokenDetailRequest(BaseModel):
    """
    Get token details request
    """

    chain: str = Field(..., description="Chain name")
    ca: str = Field(..., description="Contract address")


class TokenDetailData(BaseModel):
    """
    Token details data
    """

    symbol: str = Field(..., description="Token symbol")
    id: str = Field(..., description="Token ID")
    name: str = Field(..., description="Token name")
    platform: str = Field(..., description="Token platform")
    categories: list[str] = Field(..., description="Token categories")
    description: str = Field(..., description="Token description")
    public_notice: Optional[str] = Field(None, description="Public notice")
    twitter_url: Optional[str] = Field(None, description="Twitter URL")
    logo_url: Optional[str] = Field(None, description="Logo URL")


class TokenDetailResponse(ApiBase[TokenDetailData]):
    """
    Get token details response
    """

    pass


# ======================================================================
# Get token chain
# ======================================================================


class TokenChainRequest(BaseModel):
    """
    Get token chain request
    """

    ca: str = Field(..., description="Contract address")


class TokenChainData(BaseModel):
    """
    Get token chain response
    """

    chain: str = Field(..., description="Chain name")


class TokenChainResponse(ApiBase[TokenChainData]):
    """
    Get token chain response
    """

    pass
