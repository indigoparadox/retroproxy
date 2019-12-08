
import logging
import requests
import re
from urllib.parse import urlparse, urlunsplit
from flask import current_app, render_template, request, abort
from . import util

PORT_PATTERN = re.compile( r'(.*)(:[0-9]*)$' )

@current_app.route( '/', defaults={'path': ''} )
@current_app.route( '/<path:path>' )
def retroproxy_root( path ):

    logger = logging.getLogger( 'root' )

    # Get the requested URL.
    url = urlparse( request.url )
    url_netloc = url.netloc
    port_match = PORT_PATTERN.match( str( url_netloc ) )

    url_netloc_noport = PORT_PATTERN.sub( r'\1', url_netloc )

    # Grab the local listening port.
    url_port = ''
    if port_match:
        url_port = port_match.groups()[1]
    url = urlunsplit( (
        url.scheme,
        url_netloc_noport,
        url.path,
        url.query,
        url.fragment ) )

    logger.info( url )

    # Submit the request to archive.org.
    archive_url = 'https://web.archive.org/web/{}/{}'.format(
        current_app.config['WAYBACK_START'], url )
    response = requests.get( archive_url )

    if 404 == response.status_code:
        abort( 404 )

    return util.process_html_links( response.text, url_port=url_port )

