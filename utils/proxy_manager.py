import os
import random
import logging

PROXY_FILE = "/app/proxies.txt"

def get_random_proxy() -> str | None:
    """Read proxies.txt and return a random proxy, or None if empty/missing."""
    if not os.path.exists(PROXY_FILE):
        return None
    try:
        with open(PROXY_FILE, 'r', encoding='utf-8') as f:
            # Filter empty lines and comments
            proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not proxies:
            return None
            
        # Select a random proxy from the list
        selected_proxy = random.choice(proxies)
        
        # Ensure it has http:// or https:// prefix
        if not selected_proxy.startswith('http://') and not selected_proxy.startswith('https://') and not selected_proxy.startswith('socks5://'):
            selected_proxy = f"http://{selected_proxy}"
            
        return selected_proxy
    except Exception as e:
        logging.error(f"Error reading proxy file: {e}")
        return None
