import socket
import ipaddress
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

def is_public_url(url: str) -> bool:
    """
    Validates if a URL's hostname resolves to a public IP address.
    Prevents requests to private, loopback, or reserved IP ranges.
    """
    try:
        hostname = urlparse(url).hostname
        if not hostname:
            logger.warning(f"Could not parse hostname from URL: {url}")
            return False

        ip_addr = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_addr)

        if ip.is_private or ip.is_loopback or ip.is_reserved:
            logger.warning(f"URL {url} resolves to a non-public IP: {ip_addr}")
            return False
        
        return True
    except socket.gaierror:
        logger.error(f"Could not resolve hostname: {hostname} for URL: {url}")
        return False
    except Exception as e:
        logger.error(f"Error validating URL {url}: {str(e)}")
        return False

# Example usage (optional, for testing the function directly)
# if __name__ == '__main__':
#     test_urls = [
#         "http://google.com",
#         "http://127.0.0.1",
#         "http://192.168.1.1",
#         "http://localhost",
#         "https://api.example.com/image.jpg",
#         "http://10.0.0.1/path"
#     ]
#     for t_url in test_urls:
#         print(f"URL: {t_url}, Is Public: {is_public_url(t_url)}")
