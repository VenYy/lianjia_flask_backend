import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

import requests
from flask import Flask
from flask_cors import CORS
from sqlalchemy import func
from flask_restful import Resource, Api

from charts import charts
from list_page import list_page
from detail import detail


import os

# 设置项目根路径
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# 添加根路径到环境变量
os.environ["ROOT_DIR"] = ROOT_DIR

API_KEY = os.environ.get("API_KEY")

from db.settings import Config, db
from lib.geo.mapCity import map_city
from db.model import Houses, District, Village

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "123@123"

db.init_app(app)

# 注册蓝图
app.register_blueprint(charts)
app.register_blueprint(list_page)
app.register_blueprint(detail)

CORS(app)
api = Api(app)


def index():
    # 查询各 city 和 district 下的房源总数
    city_data = Houses.query.with_entities(Houses.city, func.count(Houses.id_), func.avg(Houses.price)).group_by(
        Houses.city).all()
    district_data = Houses.query.with_entities(
        Houses.city, Houses.district, func.count(Houses.id_), func.avg(Houses.price)
    ).group_by(Houses.city, Houses.district).all()

    # 将查询结果转换为 ECharts 所需的数据格式
    house_data = [{"name": map_city(city), "value": count} for city, count, _ in city_data]
    avg_price_data = [{"name": map_city(city), "value": round(float(avg_price), 2)} for city, _, avg_price in city_data]

    for city, district, count, avg_price in district_data:
        house_data.append({"name": map_city(district), "value": count})
        avg_price_data.append({"name": map_city(district), "value": round(float(avg_price), 2)})

    district_count = District.query.count()
    village_count = Village.query.count()
    house_count = Houses.query.count()

    return {
        "code": 200,
        "data": {
            "house_data": house_data,
            "avg_price_data": avg_price_data,
            "district_count": district_count,
            "village_count": village_count,
            "house_count": house_count
        }
    }


def get_current_city():
    """当前ip的城市定位"""
    url = f"https://restapi.amap.com/v3/ip?key={API_KEY}"
    resp = requests.get(url).json()
    return resp


def get_adcode():
    """当前城市所对应的adcode"""
    current_city = get_current_city()["city"]
    url = f"https://restapi.amap.com/v3/geocode/geo?address={current_city}&key={API_KEY}"
    resp = requests.get(url).json()
    return resp


def get_weather():
    """当前城市的天气情况"""
    adcode = get_adcode()["geocodes"][0]["adcode"]
    url = f"https://restapi.amap.com/v3/weather/weatherInfo?city={adcode}&key={API_KEY}"
    resp = requests.get(url).json()
    return resp


class Weather(Resource):
    def get(self):
        weather = get_weather()
        return weather


class IndexInfo(Resource):
    def get(self):
        return index()


api.add_resource(Weather, "/weather")
api.add_resource(IndexInfo, "/index/info")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
