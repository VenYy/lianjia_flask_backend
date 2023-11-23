def modify_data_type(houses):
    """将Decimal类型转换为Python中的float"""
    modified_houses = [
        {
            'title': item.title,
            "village_name": item.village_name,
            "img_src": item.img_src,
            "rent_type": item.rent_type,
            "area": item.area,
            "floor_type": item.floor_type,
            "floor_num": item.floor_num,
            "rooms": item.rooms,
            "city": item.city,
            "district": item.district,
            "facilities": item.facilities,
            "price": float(item.price) if item.price is not None else None
        }
        for item in houses
    ]
    return modified_houses