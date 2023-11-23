from flask import Blueprint
from sqlalchemy import func, text

from db.model import Houses
from pyecharts.charts import Bar, Pie, Grid
from pyecharts import options as opts

from db.settings import db

charts = Blueprint("charts", __name__)


def execute_sql(sql):
    return list(db.session.execute(text(sql)).fetchall())


def gen_bar(title, subtitle, x_data, y_data, series_name):
    bar = Bar()
    bar.add_xaxis(x_data)
    bar.add_yaxis(series_name, y_data,
                  bar_width=25,
                  label_opts=opts.LabelOpts(color="#53C1ED", font_weight="bold", position="top"),
                  # 柱条最小高度，可用于防止某数据项的值过小而影响交互。
                  bar_min_height=5,
                  itemstyle_opts=opts.ItemStyleOpts(color="#53C1ED")
                  )
    bar.set_global_opts(
        title_opts=opts.TitleOpts(
            title=title,
            subtitle=subtitle,
            pos_left="16px",
            pos_top="8px",
            padding=[0, 0, 10, 0],
            title_textstyle_opts=opts.TextStyleOpts(font_weight="bold", font_size=18, color="#fffd00"),
            subtitle_textstyle_opts=opts.TextStyleOpts(font_size=13, color="#96afd3")
        ),
        legend_opts=opts.LegendOpts(is_show=False),
        xaxis_opts=opts.AxisOpts(
            splitline_opts=opts.SplitLineOpts(is_show=False),
            axislabel_opts=opts.LabelOpts(font_size=14, color="#fee5c2")
        ),
        yaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(color="#fee5c2"),
            splitline_opts=opts.SplitLineOpts(is_show=True,
                                              linestyle_opts=opts.LineStyleOpts(type_="dashed", color="#fed897",
                                                                                opacity=0.5))
        ),
        tooltip_opts=opts.TooltipOpts(
            formatter="<span style='color: #0f0f0f; font-size: 16px; font-weight: bold;'>{b}</span>"
                      "</br>"
                      "<span style='color: #737373; font-size: 14px; font-weight: bold;'>{a}: </span>"
                      "<span style='color: #5ec4ed; font-size: 16px; font-weight: bold;'>{c}</span>"
        ),
        graphic_opts=[
            opts.GraphicImage(
                graphic_item=opts.GraphicItem(
                    id_="background",
                    top=-1,
                    left=-1
                ),
                graphic_imagestyle_opts=opts.GraphicImageStyleOpts(
                    width=160,
                    height=30
                )
            )
        ]
    )
    return bar


def gen_pie(title, subtitle, data, series_name):
    pie = Pie()
    pie.add(series_name, data_pair=data,
            # 饼图的半径，数组的第一项是内半径，第二项是外半径
            radius=[0, 70],
            center=["50%", "62%"],
            label_opts=opts.LabelOpts(color="#fee5c2"),
            label_line_opts=opts.PieLabelLineOpts(smooth=True, length=10, length_2=10)
            )
    pie.set_global_opts(
        title_opts=opts.TitleOpts(
            title=title,
            subtitle=subtitle,
            subtitle_textstyle_opts=opts.TextStyleOpts(font_size=13, color="#96afd3"),
            pos_left="15px",
            pos_top="3px",
            title_textstyle_opts=opts.TextStyleOpts(font_weight="bold", font_size=18, color="#fffd00")
        ),
        tooltip_opts=opts.TooltipOpts(
            formatter="<span style='color: #0f0f0f; font-size: 16px; font-weight: bold;'>{b}</span>"
                      "</br>"
                      "<span style='color: #737373; font-size: 14px; font-weight: bold;'>{a}: </span>"
                      "<span style='color: #5ec4ed; font-size: 16px; font-weight: bold;'>{c}</span>"
        ),
        legend_opts=opts.LegendOpts(is_show=False),
        graphic_opts=[
            opts.GraphicImage(
                graphic_item=opts.GraphicItem(
                    id_="background",
                    top=-1,
                    left=-1
                ),
                graphic_imagestyle_opts=opts.GraphicImageStyleOpts(
                    width=150,
                    height=30
                )
            )
        ]
    )
    return pie


@charts.route("/charts/chart1")
def chart1():
    # 城市房源数量排行柱状图
    data = Houses.query.with_entities(Houses.city, func.count().label("count")) \
        .group_by(Houses.city) \
        .all()
    # .order_by(desc('count'))\
    x_data = [i[0] for i in data]
    y_data = [i[1] for i in data]
    bar = gen_bar(
        title="各城市房源数量",
        subtitle="直观对比各城市的房源数量",
        x_data=x_data,
        y_data=y_data,
        series_name="房源数量"
    )
    grid = Grid()
    grid.add(bar, grid_opts=opts.GridOpts(pos_bottom="10%", pos_top="30%", pos_left="15%"))

    return grid.dump_options_with_quotes()


@charts.route("/charts/chart2")
def chart2():
    # 将价格分为5段并查询各分段的数量
    sql = '''select case
                when price >= 0 and price <= 2000 then "2K以下"
                when price > 2000 and price <= 4000 then "2K~4K"
                when price > 4000 and price <= 6000 then "4K~6K"
                when price > 6000 and price <= 8000 then "6K~8K"
                when price > 8000 and price <= 10000 then "8K~10K"
                when price > 10000 then "10K以上"
                end  as price_segment,
            count(*) as segment_count
            from houses
            group by price_segment'''
    data = execute_sql(sql)
    pie = gen_pie(
        title="房源价格分布",
        subtitle="各价格段的房源数量",
        data=data,
        series_name="房源数量"
    )
    return pie.dump_options_with_quotes()


@charts.route("/charts/chart3")
def chart3():
    # 出租类型的占比情况
    data = Houses.query.with_entities(Houses.rent_type, func.count(Houses.rent_type)).group_by(Houses.rent_type).all()
    pie = gen_pie(
        title="出租类型分布",
        subtitle="出租类型的占比情况",
        data=data,
        series_name="房源数量"
    )
    return pie.dump_options_with_quotes()


@charts.route("/charts/chart4")
def chart4():
    # 各地区房源平均租金情况
    data = [(i[0], round(float(i[1]), 2)) for i in
            Houses.query.with_entities(Houses.city, func.avg(Houses.price)).group_by(Houses.city).all()]
    # print(data)
    bar = gen_bar(
        title="各城市平均租金",
        subtitle="直观显示各城市租房的价格对比",
        x_data=[i[0] for i in data],
        y_data=[i[1] for i in data],
        series_name="平均租金(元/月)"
    )
    grid = Grid()
    grid.add(bar, grid_opts=opts.GridOpts(pos_bottom="10%", pos_top="30%", pos_left="15%"))
    return grid.dump_options_with_quotes()

# @charts.route("/charts/chart5")
# def chart5():
# 箱线图
#     query_result = Houses.query.with_entities(Houses.price, Houses.city).all()
#     data = {}
#     for result in query_result:
#         if result.city not in data:
#             data[result.city] = []
#         data[result.city].append(float(result.price))
#
#     x_axis_data = list(data.keys())
#     y_axis_data = list(data.values())
#
#     return {"x_data": x_axis_data, "y_data": y_axis_data}
