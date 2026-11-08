import requests
import json
import sys

RPC_URL = "https://api.mainnet-beta.solana.com"

def get_account_balance(pubkey: str):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [pubkey]
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(RPC_URL, json=payload, headers=headers, timeout=10)
        data = response.json()
        if "result" in data:
            lamports = data["result"]["value"]
            sol = lamports / 1_000_000_000
            print(f"[+] Wallet: {pubkey}")
            print(f"[+] Balance: {sol:.4f} SOL")
            return sol
        else:
            print("[-] Error in RPC response:", data.get("error"))
    except Exception as e:
        print(f"[-] Connection failed: {e}")

def get_recent_signatures(pubkey: str, limit: int = 5):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [pubkey, {"limit": limit}]
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(RPC_URL, json=payload, headers=headers, timeout=10)
        data = response.json()
        if "result" in data:
            print(f"\n[+] Last {limit} Transactions:")
            for tx in data["result"]:
                err_status = "FAILED" if tx.get("err") else "SUCCESS"
                print(f" - Signature: {tx['signature'][:20]}... | Status: {err_status}")
    except Exception as e:
        print(f"[-] Failed to fetch transactions: {e}")

if __name__ == "__main__":
    print("=== Solana Risk & Transaction Utility ===")
    wallet = input("Enter Solana Wallet Address: ").strip()
    if not wallet:
        wallet = "11111111111111111111111111111111"  # Default System Program
    
    get_account_balance(wallet)
    get_recent_signatures(wallet)
