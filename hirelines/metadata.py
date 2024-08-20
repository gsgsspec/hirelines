import os
import configparser
from urllib.parse import urlsplit
from .settings import BASE_DIR



def getConfig():
    try:
        config = configparser.ConfigParser()
        config_file_path = os.path.normpath(os.path.join(BASE_DIR,'config.ini'))
        config.read(config_file_path)

        return config
    
    except Exception as e:
        raise


def check_referrer(request):

    try:

        if 'HTTP_ORIGIN' not in request.META:
            return False
        
        referrer = request.META['HTTP_ORIGIN']
        
        referrer_host = urlsplit(referrer).hostname

        media_response = getConfig()["REFERRER"]["allowed_domains"]
        allowed_referrers = media_response.split(',')
        
        if referrer_host not in allowed_referrers:
            return False

        return True
    
    except Exception as e:
        print("Error checking referrer: ", str(e))
        return False