import requests
from lxml import etree

from lib.request.headers import create_headers
from lib.request.proxies import get_proxy


def parse_html(url):
    proxy = get_proxy().get("proxy")
    resp = requests.get(url, headers=create_headers(), proxies={"http": f"http://{proxy}"})
    if resp.status_code != 200:
        print("error status code: ", resp.status_code)
        return
    resp_content = resp.content.decode("utf-8")
    root = etree.HTML(resp_content)
    return root
