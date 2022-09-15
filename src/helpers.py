import urllib.parse

def strip_url(url):
    """This function strips the url from all parameters, usernames and passwords.
    It is used to safely log errors without exposing keys and authentication parameters."""
    return urllib.parse.urlparse(url).hostname

def url_join(url, target_path):
    """Function takes url, and returns url + target path. This function also preserves 
    all of the url parameters if they are present. 
    This is important since different RPCs use different auth mechanisms (path or parameter)"""
    scheme, netloc, path, params, query, fragment = urllib.parse.urlparse(url)
    path = path + target_path
    path = path.replace('//', '/')
    return urllib.parse.urlunparse((scheme, netloc, path, params, query, fragment))
