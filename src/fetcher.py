import httpx
from loguru import logger
import toml
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / "config" / "settings.toml"
DATA_DIR = BASE_DIR / "data"
DEBUG_PAGE_PATH = DATA_DIR / "debug_page.html"

def load_config():
    """Load configuration from settings.toml"""
    try:
        with open(CONFIG_PATH, "r") as f:
            return toml.load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found at {CONFIG_PATH}")
        raise
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise

def fetch_page():
    """Fetch the target page and save it to disk."""
    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)

    config = load_config()
    target_url = config.get("TARGET_URL")
    headers = config.get("USER_HEADERS", {})

    if not target_url:
        logger.error("TARGET_URL not found in config")
        return

    logger.info(f"Fetching {target_url}...")

    try:
        with httpx.Client(headers=headers) as client:
            response = client.get(target_url)
            response.raise_for_status()
            
            logger.success(f"Successfully fetched page. Status code: {response.status_code}")
            
            # Save to file
            with open(DEBUG_PAGE_PATH, "w", encoding="utf-8") as f:
                f.write(response.text)
            
            logger.info(f"Saved content to {DEBUG_PAGE_PATH}")

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e.response.status_code} - {e}")
    except httpx.RequestError as e:
        logger.error(f"Request error occurred: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    fetch_page()
