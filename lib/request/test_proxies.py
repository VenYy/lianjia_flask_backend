import requests
from proxies import *

proxy = get_proxy().get("proxy")
# proxy = "127.0.0.1:7890"
try:
    requests.get('http://wenshu.court.gov.cn/', proxies={"http": "http://" + proxy})
except:
    print('connect failed')
else:
    print('success')