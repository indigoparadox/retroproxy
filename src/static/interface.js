
$(document).ready( function() {
    //var win_foo = open_window( 'Foo', 'foo', true, 'icons-w95-16x16.png', 80, 272 );
    var ico_foo = desktopCreateIcon( "Foo", 'icons-w95-32x32.png', 800, 544, 10, 10, function() {
        /* Only open the window if it's not already open. */
        if( 0 >= $('#window-foo').length ) {
            var win_foo = openWindow( 'Foo', 'window-foo', true, 'icons-w95-16x16.png', 400, 272 );
            var input_txt = windowCreateInputText( win_foo, 'Date', '', '10px', '10px' );
        }
    } );
} );
