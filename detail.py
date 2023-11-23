from flask import render_template, Blueprint, request, jsonify
from sqlalchemy import func, distinct

from charts import execute_sql
from db.model import City, District, Houses
from db.settings import db

detail = Blueprint("detail", __name__)


@detail.route("/detail")
def house_detail():
    city = request.args.get("city")
    district = request.args.get("district")
    village_name = request.args.get("village_name")

    if city:
        pass
    if city and district:
        pass
    if city and district and village_name:
        pass

    city_list = [i[0] for i in City.query.with_entities(City.city_zh).all()]

    return render_template("detail.html",
                           city_list=city_list,
                           city=city,
                           district=district,
                           village_name=village_name)


@detail.route("/selector_city", methods=["POST"])
def selector_city():
    # 获取前端发送的请求, 返回对应城市的下级区县列表
    selected_city = request.form["city"]
    result = db.session.query(City.city_zh, District.district_zh) \
        .join(District) \
        .filter(City.city_zh == selected_city).all()
    sub_district = [i[1] for i in result]
    return sub_district


@detail.route("/selector_district", methods=["POST"])
def selector_district():
    # 获取前端发送的请求, 返回对应城市的小区列表
    selected_district = request.form["district"]
    result = Houses.query.with_entities(distinct(Houses.village_name)) \
        .filter(Houses.district == selected_district).all()
    sub_village = [i[0] for i in result]
    return sub_village


# 查询小区详细信息
@detail.route("/village_detail", methods=["POST", "GET"])
def village_detail():
    # 获取前端发送的请求数据
    city = request.args.get("city")
    district = request.args.get("district")
    village_name = request.args.get("village_name")
    # print(city, district, village_name)

    sql = f'''select case
                    when price >= 0 and price <= 1000 then "1K以下"
                    when price > 1000 and price <= 2000 then "1K~2K"
                    when price > 2000 and price <= 3000 then "2K~3K"
                    when price > 3000 and price <= 4000 then "3K~4K"
                    when price > 4000 and price <= 5000 then "4K~5K"
                    when price > 5000 and price <= 6000 then "5K~6K"
                    when price > 6000 and price <= 7000 then "6K~7K"
                    when price > 7000 and price <= 8000 then "7K~8K"
                    when price > 8000 then "8K以上"
                    end  as price_segment,
                count(*) as segment_count
                from houses
                where city = '{city}' and district = '{district}' and village_name = '{village_name}'
                group by price_segment'''
    price_data = execute_sql(sql)
    # 最低租金和最高租金
    max_price, min_price = Houses.query \
        .with_entities(func.max(Houses.price), func.min(Houses.price)) \
        .filter(
        (Houses.city == city) &
        (Houses.district == district) &
        (Houses.village_name == village_name)) \
        .all()[0]
    # 最高租金的房源
    max_price_house = Houses.query.filter(
        (Houses.city == city) &
        (Houses.district == district) &
        (Houses.village_name == village_name) &
        (Houses.price == max_price)
    ).all()[0]
    # 最低租金的房源
    min_price_house = Houses.query.filter(
        (Houses.city == city) &
        (Houses.district == district) &
        (Houses.village_name == village_name) &
        (Houses.price == min_price)
    ).all()[0]

    # 户型分布情况饼图
    rooms_data = Houses.query \
        .with_entities(Houses.rooms, func.count(Houses.rooms)) \
        .filter(
        (Houses.city == city) &
        (Houses.district == district) &
        (Houses.village_name == village_name)) \
        .group_by(Houses.rooms) \
        .all()

    # 房源数量最多的户型名称
    max_rooms_count = max(rooms_data, key=lambda x: x[1])[1]
    max_rooms_name = [i[0] for i in rooms_data if i[1] == max_rooms_count][0]

    # 房屋面积与价格的关系散点图
    scatter_data = [[float(i[0].rstrip("㎡")), float(i[1])] for i in
                    Houses.query.with_entities(Houses.area, Houses.price).filter(
                        (Houses.city == city) &
                        (Houses.district == district) &
                        (Houses.village_name == village_name)
                    ).all()]

    # 不同户型的价格比较, 横轴表示房型，纵轴表示平均价格。
    bar_data = Houses.query.with_entities(Houses.rooms, func.avg(Houses.price)).filter(
        (Houses.city == city) &
        (Houses.district == district) &
        (Houses.village_name == village_name)
    ).group_by(Houses.rooms).all()
    rooms_list = [i[0] for i in bar_data]
    avg_price_list = [float(i[1]) for i in bar_data]

    response_data = {
        "status": 1,
        "data": {
            "price_data": [{"name": i[0], "value": i[1]} for i in price_data],
            "rooms_data": [{"name": i[0], "value": i[1]} for i in rooms_data],
            "max_price": max_price,
            "min_price": min_price,
            "max_price_house": max_price_house.__repr__(),
            "min_price_house": min_price_house.__repr__(),
            "max_rooms_name": max_rooms_name,
            "max_rooms_count": max_rooms_count,
            "scatter_data": scatter_data,
            "rooms_list": rooms_list,
            "avg_price_list": avg_price_list
        }
    }
    return jsonify(response_data)
