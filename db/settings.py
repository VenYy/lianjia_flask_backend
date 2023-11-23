from flask_sqlalchemy import SQLAlchemy
import pymysql
import os

HOST = os.getenv('DATABASE_HOST')
PORT = os.getenv("DATABASE_PORT")
USER = os.getenv('DATABASE_USER')
PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE = os.getenv("DATABASE_NAME")


pymysql.install_as_MySQLdb()

db = SQLAlchemy()

class Config:
    DEBUG = True
    # 数据库信息
    SQLALCHEMY_DATABASE_URI = f'mysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
