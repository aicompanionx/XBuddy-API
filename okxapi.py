import asyncio
import hmac
import hashlib
import base64
import urllib.parse
import httpx
from datetime import datetime, timezone

API_KEY = "86722305-be09-426d-a918-d005e4cc8fd4"
SECRET   = "B6D1AE39FD30DFF65ED2B712EE07A920"
PASSPHRASE = "S4Qb*nx4B#3&Dc"
BASE = "https://www.okx.com/api/v5"

def sign(ts: str, method: str, path: str, body: str = "") -> str:
    msg = f"{ts}{method}{path}{body}"
    return base64.b64encode(hmac.new(SECRET.encode(), msg.encode(), hashlib.sha256).digest()).decode()

async def okx_private_get(path: str, params: dict | None = None):
    query_string = urllib.parse.urlencode(params or {})
    full_request_url = f"{BASE}{path}"
    if query_string:
        full_request_url += f"?{query_string}"

    # Correctly format the requestPath for signing
    base_uri_path_component = urllib.parse.urlparse(BASE).path
    path_for_signing = base_uri_path_component + path
    if query_string:
        path_for_signing += f"?{query_string}"

    # Generate timestamp in ISO 8601 format (YYYY-MM-DDTHH:mm:ss.SSSZ)
    ts = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

    signature = sign(ts, "GET", path_for_signing) # Body is empty for GET

    headers = {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "OK-ACCESS-TIMESTAMP": ts,
        "OK-ACCESS-SIGN": signature,
        "User-Agent": "okx-demo/0.2",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(60, connect=30), 
        headers=headers,
        verify=False
    ) as c:
        try:
            r = await c.get(full_request_url)
            r.raise_for_status()
            data = r.json()
            if data.get("code") != "0": # Safer access with .get()
                raise RuntimeError(f'OKX err {data.get("code", "N/A")}: {data.get("msg", "No message")}')
            return data.get("data")
        except httpx.ConnectTimeout:
            print(f"连接超时: {full_request_url}")
            if BASE == "https://www.okx.com/api/v5":
                print("尝试使用备用API地址...")
                alt_url = full_request_url.replace("https://www.okx.com/api/v5", "https://www.okx.me/api/v5")
                r = await c.get(alt_url)
                r.raise_for_status()
                data = r.json()
                if data.get("code") != "0":
                    raise RuntimeError(f'OKX err {data.get("code", "N/A")}: {data.get("msg", "No message")}')
                return data.get("data")
            else:
                raise  # 如果不是默认URL，则重新抛出异常

async def get_token_detail(symbol: str = "BTC"):
    currencies, instruments = await asyncio.gather(
        okx_private_get("/asset/currencies", {"ccy": symbol}),
        okx_private_get("/public/instruments", {"instType": "SPOT", "instId": f"{symbol}-USDT"}),
    )
    print(currencies)
    print(instruments)

if __name__ == "__main__":
    asyncio.run(get_token_detail("BTC"))
