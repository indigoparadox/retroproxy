
import logging

@app.route( '/' )
def retroproxy_root():
    return render_template( 'root.html' )

