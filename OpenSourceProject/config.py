# config.py
#Flask 애플리케이션의 설정을 관리

import os

class Config:
    # 데이터베이스 URI 설정
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://noyakzone:1234@54.180.94.138:5432/noyakzone')
    # SQLAlchemy 변경 사항 추적 비활성화
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 텀블러 API 키 설정
    TUMBLR_API_KEY = os.getenv('TUMBLR_API_KEY', 'C5z3IeO5LAe5fN3M17zx76m1mdD01T0fKk6lnRw3wdOqOUJYsI')
