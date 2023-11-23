import json

from db.settings import db


class Houses(db.Model):
    __tablename__ = 'houses'

    id_ = db.Column(db.String(255), primary_key=True)
    title = db.Column(db.String(255))
    village_name = db.Column(db.String(255))
    img_src = db.Column(db.String(255))
    price = db.Column(db.DECIMAL(10, 2))
    rent_type = db.Column(db.String(32))
    rooms = db.Column(db.String(32))
    area = db.Column(db.String(32))
    direction = db.Column(db.String(32))
    floor_type = db.Column(db.String(32))
    floor_num = db.Column(db.Integer)
    facilities = db.Column(db.String(255))
    city = db.Column(db.String(32), db.ForeignKey('city.city_zh'))
    district = db.Column(db.String(32), db.ForeignKey('district.district_zh'))

    city_ref = db.relationship('City')
    district_ref = db.relationship('District')

    def __repr__(self):
        house_dict = {
            "id_": self.id_,
            "title": self.title,
            "price": float(self.price),
            "village_name": self.village_name,
            "img_src": self.img_src,
            "rent_type": self.rent_type,
            "rooms": self.rooms,
            "area": self.area,
            "direction": self.direction,
            "floor_type": self.floor_type,
            "floor_num": self.floor_num,
            "facilities": self.facilities,
            "city": self.city,
            "district": self.district
        }
        return json.dumps(house_dict)


class City(db.Model):
    __tablename__ = 'city'

    city_en = db.Column(db.String(32), primary_key=True)
    city_zh = db.Column(db.String(32))

    def __repr__(self):
        return f"<City(city_en='{self.city_en}', city_zh='{self.city_zh}')>"


class District(db.Model):
    __tablename__ = 'district'

    city_en = db.Column(db.String(32), db.ForeignKey('city.city_en'))
    district_en = db.Column(db.String(32), primary_key=True)
    district_zh = db.Column(db.String(32))
    city = db.relationship('City')

    __table_args__ = (
        db.Index('city_en', 'city_en'),
    )

    def __repr__(self):
        return f"<District(district_en='{self.district_en}', district_zh='{self.district_zh}')>"


class Village(db.Model):
    __tablename__ = 'village'

    city = db.Column(db.String(32), db.ForeignKey('city.city_zh'), primary_key=True)
    district = db.Column(db.String(32), db.ForeignKey('district.district_zh'), primary_key=True)
    village_name = db.Column(db.String(255), primary_key=True)
    lng = db.Column(db.DECIMAL(19, 15))
    lat = db.Column(db.DECIMAL(19, 15))

    city_ref = db.relationship('City')
    district_ref = db.relationship('District')

    def __repr__(self):
        return f"<Village(village_name='{self.village_name}', lng={self.lng}, lat={self.lat})>"
