# 用于向village表中新增的数据添加经纬度信息
from db.model import Village, db
from geoCoder import *
from app import app

with app.app_context():
    data = Village.query.with_entities(Village.city, Village.district, Village.village_name)\
        .filter(Village.lat.is_(None), Village.lng.is_(None))\
        .all()
    print(data)
    for item in data:
        print(item)
        city, district, village_name = item[0], item[1], item[2]
        address = city + district + village_name

        lng, lat = geocoder(address)
        # 根据city、district和village_name查询Village表中的记录
        village = db.session.query(Village).filter_by(city=city, district=district, village_name=village_name).first()
        # 更新经度和纬度字段
        village.lng = lng
        village.lat = lat
        db.session.commit()
