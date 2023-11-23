import requests


# /	GET	api介绍	None
# /get	GET	随机获取一个代理	可选参数: ?type=https 过滤支持https的代理
# /pop	GET	获取并删除一个代理	可选参数: ?type=https 过滤支持https的代理
# /all	GET	获取所有代理	可选参数: ?type=https 过滤支持https的代理
# /count	GET	查看代理数量	None
# /delete	GET	删除代理	?proxy=host:ip


def get_proxy():
    proxy_json = requests.get("http://47.120.0.92:5010/get/")
    return proxy_json.json()


def delete_proxy(proxy):
    requests.get("http://47.120.0.92:5010/delete/?proxy={}".format(proxy))
