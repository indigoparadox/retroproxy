
import unittest
import os
import sys
from urllib.parse import urlparse

sys.path.insert( 0, os.path.dirname( os.path.dirname( __file__ ) ) )

from retroproxy.filter import RetroFilter

TEST_URLS = [
    'https://google.com',
    'http://www.yahoo.com',
    'https://sketchysite.sk:120/stuff.php',
    'http://www.angelfire.com/geocities/old.html',
    'https://sketchysite.sk:8888/stuff.php',
    'http://content.example.com/style.css',
    'about:blank',
    '/help.html'
]

TEST_URL_FRAME = '''
<html>
<head>
<title>Test Frame</title>
<link rel="stylesheet" href="%s">
</head>
<body>
<form action="%f">
<a href="%l">Test Link</a>
<img src="%i" alt="Image">
</form>
</body>
</html>
'''

class TestRetroProxy( unittest.TestCase ):

    def test_fix_netloc_port( self ):

        body = TEST_URL_FRAME
        parser = RetroFilter( body, 8888 )

        for url in TEST_URLS:
            url_fixed = parser.fix_netloc_port( url )
            url_test = urlparse( url_fixed )
            if 'about:blank' == url or '/help.html' == url:
                self.assertIsNone( url_test.port )
            else:
                self.assertEqual( url_test.port, 8888 )

    def test_process_html_links( self ):

        for url in TEST_URLS:
            body = TEST_URL_FRAME.replace( '%l', url )
            parser = RetroFilter( body, 8888 )

            parser.process_html_links()

            if 'about:blank' != url and '/help.html' != url:
                self.assertRegex( str( parser ), r'https?://.*?:8888' )

    def test_process_html_scripts( self ):

        for url in TEST_URLS:
            body = TEST_URL_FRAME.replace( '%s', url )
            parser = RetroFilter( body, 8888 )

            parser.process_html_scripts()

            if 'about:blank' != url and '/help.html' != url:
                self.assertRegex( str( parser ), r'https?://.*?:8888' )

    def test_process_html_imgs( self ):

        for url in TEST_URLS:
            body = TEST_URL_FRAME.replace( '%i', url )
            parser = RetroFilter( body, 8888 )

            parser.process_html_imgs()

            if 'about:blank' != url and '/help.html' != url:
                self.assertRegex( str( parser ), r'https?://.*?:8888' )

    def test_process_html_forms( self ):

        for url in TEST_URLS:
            body = TEST_URL_FRAME.replace( '%f', url )
            parser = RetroFilter( body, 8888 )

            parser.process_html_forms()

            if 'about:blank' != url and '/help.html' != url:
                self.assertRegex( str( parser ), r'https?://.*?:8888' )
