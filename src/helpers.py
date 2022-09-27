import urllib.parse
from settings import logger


def strip_url(url):
    """This function strips the url from all parameters, usernames and passwords.
    It is used to safely log errors without exposing keys and authentication parameters."""
    return urllib.parse.urlparse(url).hostname


def validate_protocol(url, protocol):
    if urllib.parse.urlparse(url).scheme == protocol:
        pass
    else:
        logger.error("Non {} endpoint provided for {}".format(protocol, strip_url(url)))
        exit(1)


def check_protocol(url, protocol):
    return urllib.parse.urlparse(url).scheme == protocol


def url_join(url, target_path):
    """Function takes url, and returns url + target path. This function also preserves 
    all of the url parameters if they are present. 
    This is important since different RPCs use different auth mechanisms (path or parameter)"""
    scheme, netloc, path, params, query, fragment = urllib.parse.urlparse(url)
    path = path + target_path
    path = path.replace('//', '/')
    return urllib.parse.urlunparse((scheme, netloc, path, params, query, fragment))


def generate_labels_from_metadata(rpc_metadata):
    labels = ['url', 'provider', 'blockchain', 'network_name', 'network_type']
    label_values = [
        rpc_metadata['url'], rpc_metadata['provider'], rpc_metadata['blockchain'], rpc_metadata['network_name'],
        rpc_metadata['network_type']
    ]

    if "chain_id" in rpc_metadata:
        labels.append("evmChainID")
        label_values.append(str(rpc_metadata['chain_id']))

    return labels, label_values
