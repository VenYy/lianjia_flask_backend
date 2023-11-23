import json
import math
import random

from flask import Blueprint, request, jsonify
from sqlalchemy import not_, or_

from db.model import Houses, City, District
from db.settings import db
from db.modify_data_type import modify_data_type

list_page = Blueprint("list_page", __name__)


@list_page.route("/house/list")
def house_list():
    user_input = request.args.get("param")
    city = request.args.get("city", "", type=str)
    district = request.args.get("district", "", type=str)
    rent_type = request.args.get("rent_type", "", type=str)
    rooms = request.args.get("rooms", "", type=str)
    direction = request.args.get("direction", "", type=str)
    price_range = request.args.get("price", "", type=str)

    # 创建请求参数的副本
    query_params = dict(request.args.copy())

    # 转换为URL编码
    # encoded_params = urlencode(query_params)

    result = db.session.query(City.city_zh, District.district_zh).join(District).all()
    city_districts = {}
    for city_zh, district_zh in result:
        if city_zh not in city_districts:
            city_districts[city_zh] = []
        city_districts[city_zh].append(district_zh)

    # print(city_districts)

    # 创建查询对象
    query = Houses.query

    # 按用户输入筛选
    if user_input:
        query = query.filter(
            (Houses.city.like(f"%{user_input}%")) |
            (Houses.district.like(f"%{user_input}%")) |
            (Houses.village_name.like(f"%{user_input}%")) |
            (Houses.title.like(f"%{user_input}%"))
        )

    # 按城市名称筛选
    if city:
        query = query.filter(Houses.city == city)
    # 按区县名称筛选
    if district:
        query = query.filter(Houses.district == district)
    # 按出租类型筛选
    if rent_type:
        query = query.filter(Houses.rent_type == rent_type)
    # 按户型筛选
    if rooms:
        if rooms == "5室以上":
            # 使用正则表达式提取数字并比较
            query = query.filter(Houses.rooms.op("REGEXP")('[5-9]室|[1-9][0-9]室'))
        else:
            query = query.filter(Houses.rooms.like(f"%{rooms}%"))
    # 按朝向筛选
    if direction:
        if direction == "其他":
            query = query.filter(not_(Houses.direction.in_(["东", "西", "南", "北", "南/北"])))
        else:
            query = query.filter(Houses.direction == direction)
    # 按价格区间筛选
    if price_range:
        if price_range == "1000元以下":
            query = query.filter(Houses.price.between(0, 1000))
        elif price_range == "1000-2000元":
            query = query.filter(Houses.price.between(1000, 2000))
        elif price_range == "2000-3000元":
            query = query.filter(Houses.price.between(2000, 3000))
        elif price_range == "3000-4000元":
            query = query.filter(Houses.price.between(3000, 4000))
        elif price_range == "4000-5000元":
            query = query.filter(Houses.price.between(4000, 5000))
        elif price_range == "5000元以上":
            query = query.filter(Houses.price >= 5000)

    per_page = 30  # 每页的显示数量
    total_count = query.count()  # 总的记录数
    total_page_num = math.ceil(total_count / per_page)  # 总的页面数量
    current_page = request.args.get("page", 1, type=int)  # 当前页码

    # 执行分页查询
    pagination = query.paginate(page=current_page, per_page=per_page)

    resp = {
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "items": [item.__repr__() for item in pagination.items]  # 将每个项目转换为字典或JSON可序列化对象
        },
        "page_num": current_page,
        "param": user_input,
        "city": city,
        "district": district,
        "rent_type": rent_type,
        "rooms": rooms,
        "direction": direction,
        "price": price_range,
        "city_districts": city_districts,
        "total_count": total_count,
        "total_page_num": total_page_num,
        "query_params": query_params
    }

    return resp


@list_page.route("/house/suggest", methods=["POST"])
def search_suggest():
    """基于用户输入的内容进行相似搜索"""
    user_input = request.form.get("search_input")
    suggest_list = Houses.query.distinct().filter(
        or_(
            (Houses.title.like(f"%{user_input}%")),
            (Houses.rooms.like(f"%{user_input}%")),
            (Houses.city.like(f"%{user_input}%")),
            (Houses.district.like(f"%{user_input}%"))
        )).all()
    if len(suggest_list) == 0:
        return jsonify({"status": 0})
    return jsonify({"status": 1, "data": modify_data_type(random.choices(suggest_list, k=6))})


@list_page.app_template_filter("trans_city")
def trans_city(city_zh):
    """修改模板中的城市名称"""
    city_en = City.query.with_entities(City.city_en).filter(City.city_zh == city_zh).first()[0]
    return city_en


@list_page.app_template_filter("deal_facility")
def deal_facility(facilities):
    """分割设施列表"""
    facility_list = facilities.split(",")
    return facility_list


@list_page.app_template_filter("update_param")
def update_param(query_params, key, value=None):
    """修改请求参数, 若不传入值则删除指定的参数"""
    new_query_params = query_params.copy()
    try:
        # 用户每次筛选房源条件, 页数需要重新开始
        new_query_params.pop("page")
    except KeyError:
        pass
    if value:
        new_query_params[key] = value
    else:
        try:
            new_query_params.pop(key)
            new_query_params.pop("page")
        except KeyError:
            pass
    return new_query_params
