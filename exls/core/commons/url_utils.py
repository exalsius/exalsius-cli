import webbrowser


def open_url_in_browser(url: str) -> bool:
    """
    Open a URL in the user's default web browser.

    Args:
        url: The URL to open

    Returns:
        True if the URL was successfully opened, False otherwise
    """
    try:
        return webbrowser.open(url)
    except Exception:
        return False
