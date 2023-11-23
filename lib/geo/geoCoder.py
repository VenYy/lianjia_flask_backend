# 地理信息解析
import requests
import json
import re

AK = 'IaTZtrEoANLfr1IbHqcveSuuLoKVp8yZ'


# AK = "RKS4GTxZvImP31RXHSvECCMTKjXbEpWf"
# AK = "hrAGPKHldGBAa1yYo7LPSaYXINVmr9BH"


def geocoder(address):
    url = f'http://api.map.baidu.com/geocoding/v3/?address={address}&output=json&ak={AK}&ret_coordtype=bd09ll&callback=showLocation'
    res = requests.get(url)

    try:
        results = json.loads(re.findall(r'\((.*?)\)', res.text)[0])["result"]["location"]
        lng = results["lng"]
        lat = results["lat"]
        return lng, lat
    except (KeyError, IndexError):
        print("无法获取经纬度信息，请检查地址是否正确或者 API 请求是否出现问题。")
        return None, None


def reverseGeocoder(lat, lng):
    url = f'http://api.map.baidu.com/reverse_geocoding/v3/?ak={AK}&output=json&coordtype=bd09ll&location={lat},{lng}'
    res = requests.get(url)
    address = json.loads(res.text)["result"]["formatted_address"]

    return address



