# models.py
#데이터베이스 모델을 정의

from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy 객체 생성
db = SQLAlchemy()

# Pattern 모델 정의
class Pattern(db.Model):
    __tablename__ = 'pattern'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50), nullable=False)
    detail = db.Column(db.String(200), nullable=False)

# Board 모델 정의
class Board(db.Model):
    __tablename__ = 'board'
    index = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, nullable=False)
    text = db.Column(db.Text, nullable=False)
    place = db.Column(db.String(50), nullable=True)
    url = db.Column(db.Text, nullable=False)
    id = db.Column(db.String(30), nullable=True)
    web = db.Column(db.String(30), nullable=False)
    picture = db.Column(db.Text, nullable=True)

# Report 모델 정의
class Report(db.Model):
    __tablename__ = 'report'
    index = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(30), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String(30), nullable=False)
    text = db.Column(db.Text, nullable=False)
    link = db.Column(db.Text, nullable=False)
    picture = db.Column(db.Text, nullable=True)
    result = db.Column(db.Boolean, default=False)
    check_drug = db.Column(db.Boolean, default=False)
