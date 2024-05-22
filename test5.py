import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode, quote_plus
import urllib3

# Testnet with read-only API key and secret
SecretKey = "OP9SsrwYt9Y7Sveici9XjRucDtqBB0lqbY2C"
AccessKey = "RpIwvnwYtPS380SxKV"

def bybit_spot_balance(AccessKey: str, SecretKey: str) -> dict:
    # Parameters for the request
    params = {
        "api_key": AccessKey,
        "timestamp": round(time.time() * 1000),
        "recv_window": 10000
    }

    # Create the parameter string
    param_str = urlencode(sorted(params.items()))

    # Generate the signature
    hash = hmac.new(bytes(SecretKey, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
    signature = hash.hexdigest()

    # Append the signature to the parameter string
    full_param_str = f"{param_str}&sign={signature}"

    # API request URL (testnet)
    url = "https://api-testnet.bybit.com/spot/v3/private/account"
    headers = {"Content-Type": "application/json"}

    # Disable SSL warnings (use cautiously)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Make the API request
    try:
        response = requests.get(f"{url}?{full_param_str}", headers=headers, verify=False)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Debugging information
        print(f"Request URL: {url}?{full_param_str}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Text: {response.text}")

        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed: {e}")
        return {}

# Example usage
balance = bybit_spot_balance(AccessKey, SecretKey)
print(balance)
