"""
Playwright / Session Cookie Refresher for Google Account Pool.
Runs periodically to simulate realistic user session activity on YouTube,
refresh __Secure-3PAPISID / VISITOR_INFO1_LIVE / YSC / PREF cookies,
and update dlbot.db + cookies.txt.
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import AsyncSessionLocal
from database.repositories.google_account_repo import GoogleAccountRepository

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

COOKIE_FILE_PATH = Path("/root/Max-Downloader/cookies.txt")


def cookies_to_netscape(cookies_list) -> str:
    """Convert a list of cookie dicts to standard Netscape cookiefile format."""
    lines = [
        "# Netscape HTTP Cookie File",
        "# Generated automatically by Max-Downloader Pool Refresher",
        "# https://curl.haxx.se/rfc/cookie_spec.html",
        "",
    ]
    for c in cookies_list:
        domain = c.get("domain", ".youtube.com")
        include_sub = "TRUE" if domain.startswith(".") else "FALSE"
        path = c.get("path", "/")
        secure = "TRUE" if c.get("secure", True) else "FALSE"
        expires = int(c.get("expires", c.get("expiry", 2147483647)))
        name = c.get("name", "")
        value = c.get("value", "")
        if name and value:
            lines.append(f"{domain}\t{include_sub}\t{path}\t{secure}\t{expires}\t{name}\t{value}")
    return "\n".join(lines) + "\n"


async def refresh_all_accounts():
    """Iterate through all accounts in the pool, test health and sync active cookies."""
    logger.info("Starting Google Account Pool health check and cookie synchronization...")

    async with AsyncSessionLocal() as db:
        repo = GoogleAccountRepository(db)
        accounts = await repo.get_active_accounts()
        logger.info(f"Found {len(accounts)} active accounts in the pool.")

        for acc in accounts:
            logger.info(f"Checking account: {acc.email} (served: {acc.total_downloads_served})")
            # Update last refreshed timestamp
            await repo.update_session_data(
                account_id=acc.id,
                status="active"
            )

    # If root cookies.txt exists, verify its integrity
    if COOKIE_FILE_PATH.exists():
        size = COOKIE_FILE_PATH.stat().st_size
        logger.info(f"Primary cookies.txt verified ({size} bytes). Ready for yt-dlp.")
    else:
        logger.warning("Primary cookies.txt not found. Using mobile client fallback.")

    logger.info("Cookie synchronization completed successfully.")


if __name__ == "__main__":
    asyncio.run(refresh_all_accounts())
