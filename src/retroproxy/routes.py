
import logging
import requests
import re
import io
from urllib.parse import urlparse, urlunsplit
from flask import current_app, render_template, request, abort, Response, send_file
from bs4 import BeautifulSoup
from . import proxy

PORT_PATTERN = re.compile( r'(.*)(:[0-9]*)$' )
HTML_TYPE_PATTERN = re.compile( r'^([a-zA-Z]*/(html|HTML)).*' )
HEADER_ORIG_PATTERN = re.compile( r'^X-Archive-Orig-(.*)$' )

@current_app.route( '/retroproxy/config' )
def retroproxy_config():
    return render_template( 'config.html' )

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

    logger.info( 'response: {}'.format( response.status_code ) )
    if 404 == response.status_code:
        abort( 404 )

    # Grab the original headers from the archive.
    orig_headers = {}
    for hdr, val in response.headers.items():
        match = HEADER_ORIG_PATTERN.match( hdr )
        if match:
            logger.info( 'orig header "{}": "{}"'.format( match.groups()[0],
                val ) )
            orig_headers[match.groups()[0]] = val

    #clength = response.headers['content-length']
    ctype = response.headers['content-type']
    ctype_match = HTML_TYPE_PATTERN.match( ctype )
    if ctype_match:
        soup = BeautifulSoup( response.text, 'html.parser' )
        proxy.process_html_links( soup, url_port=url_port )
        proxy.process_html_imgs( soup, url_port=url_port )
        proxy.process_html_forms( soup, url_port=url_port )
        out = Response( str( soup ), mimetype=ctype )
        out.headers = orig_headers
        return out
    else:
        logger.info( 'unrecognized mimetype: {}'.format( ctype ) )
        text = response.content
        #print( text )
        return send_file( io.BytesIO( text ), mimetype=ctype )

