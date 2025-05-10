from urllib.parse import urlparse, urlunsplit


def truncate_url_path(url: str, level: int = 0) -> str:
    """
    Truncate URL path to specified level
    
    Parameters:
        url: URL to be processed
        level: number of path levels to keep, 0 means only keep domain name, 
            1 means keep the first level of path, and so on
    
    Returns:
        Processed URL
    """
    # Parse URL
    parsed_url = urlparse(url)
    
    # If level is 0, return domain name directly
    if level <= 0:
        return urlunsplit((parsed_url.scheme, parsed_url.netloc, '', '', ''))
    
    # Split path
    path_parts = parsed_url.path.strip('/').split('/')
    
    # Keep specified level of path
    if level <= len(path_parts):
        new_path = '/' + '/'.join(path_parts[:level])
    else:
        # If specified level exceeds actual path level, return full path
        new_path = parsed_url.path
    
    # Reconstruct URL
    return urlunsplit((parsed_url.scheme, parsed_url.netloc, new_path, '', ''))