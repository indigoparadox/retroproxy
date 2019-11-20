
from urllib.parse import urlparse, urlunsplit

def fix_netloc_port( url_in, url_port ):
    nl_url = urlparse( url_in )
    if nl_url.netloc:
        netloc = nl_url.netloc + url_port
        return urlunsplit(
            (nl_url.scheme, netloc, nl_url.path,
            nl_url.query, nl_url.fragment) )

    else:
        return url_in

