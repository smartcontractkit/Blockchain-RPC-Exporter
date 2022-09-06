import urllib.parse

def strip_url(url):
    return urllib.parse.urlparse(url).netloc


def url_join(url, path):
    return urllib.parse.urljoin(url, path)
