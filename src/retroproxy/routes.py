
import logging
import requests
import re
from urllib.parse import urlparse, urlunsplit
from flask import current_app, render_template, request, abort
from bs4 import BeautifulSoup
from . import util

PORT_PATTERN = re.compile( r'(.*)(:[0-9]*)$' )
ARCHIVE_PATTERN = re.compile( r'^((https?://web.archive.org)?/web/[0-9a-z_]*/)' )

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

    print( url )

    # Submit the request to archive.org.
    archive_url = 'https://web.archive.org/web/{}/{}'.format(
        current_app.config['WAYBACK_START'], url )
    response = requests.get( archive_url )

    if 404 == response.status_code:
        abort( 404 )

    soup = BeautifulSoup( response.text, 'html.parser' )
    for a in soup.findAll( 'a' ):
        a['href'] = ARCHIVE_PATTERN.sub( '', a['href'] )

        # Add our listening port to the netloc.
        a['href'] = util.fix_netloc_port( a['href'], url_port )

    # Fix for static CSS.
    # TODO: Should these just be stripped?
    for link in soup.findAll( 'link' ):
        if link['href'].startswith( '/_static/' ):
            link['href'] = 'https://web.archive.org{}'.format( link['href'] )

    # Fix for images relative to web.archive.org.
    for img in soup.findAll( 'img' ):
        if img['src'].startswith( '/web/' ):
            img['src'] = 'https://web.archive.org{}'.format( img['src'] )

    # Fix for optional base tag.
    for base in soup.findAll( 'base' ):
        base['href'] = ARCHIVE_PATTERN.sub( '', base['href'] )

        base['href'] = util.fix_netloc_port( base['href'], url_port )

    # Strip out archive modernity hacks.
    for script in soup.findAll( 'script', ):
        if 'src' in script.attrs and (
        'client-rewrite.js' in script.attrs['src'] or \
        'wbhack.js' in script.attrs['src'] ) or \
        'wbhack.' in script.text or \
        'WB_wombat_Init' in script.text:
            script.extract()

    return str( soup )

