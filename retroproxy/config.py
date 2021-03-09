
import yaml

class Config( object ):
    def __init__( self, config_f ):

        # Grab config from the file and add it to this object.
        config = yaml.load( config_f )
        for k, v in config.items():
            setattr( self, k.upper(), v )

