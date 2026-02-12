import requests
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def download_file(url: str, dest: Path) -> Path:
    """
    Downloads a file from the given URL to the destination path.
    """
    if dest.exists():
        logger.info(f"File {dest} already exists. Skipping download.")
        return dest

    logger.info(f"Downloading {url} to {dest}...")
    try:
        # Anvisa server often has SSL issues, so we disable verification
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = requests.get(url, stream=True, verify=False)
        response.raise_for_status()
        
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info("Download complete.")
        return dest
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        raise
