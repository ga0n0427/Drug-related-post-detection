# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from models import db, Board, Report
from utils import tumblr_crawling, jazz_crawling, classify_text, extract_text_from_image
import threading
import time
import pandas as pd

# Flask 애플리케이션 초기화
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

def add_to_database(date, text, url, telegram_id, web, place=None, picture=None):
    """
    데이터를 데이터베이스에 추가하는 함수
    """
    new_record = Board(date=date, text=text, place=place, url=url, id=telegram_id, web=web, picture=picture)
    db.session.add(new_record)
    db.session.commit()

def check_and_update_reports():
    """
    보고서를 주기적으로 확인하고 업데이트하는 함수
    """
    while True:
        with app.app_context():
            reports = db.session.query(Report).filter_by(check_drug=False).all()
            for report in reports:
                text_result = classify_text(report.text)
                if report.picture:
                    try:
                        picture_text = extract_text_from_image(report.picture)
                        picture_result = classify_text(picture_text)
                    except Exception as e:
                        print(f"Error extracting text from image: {e}")
                        picture_result = None
                else:
                    picture_result = None

                if '0' in text_result or (picture_result is not None and '0' in picture_result):
                    report.result = True
                else:
                    report.result = False
                
                report.check_drug = True
            db.session.commit()
        time.sleep(30)

@app.route('/start_crawling', methods=['POST'])
def start_crawling():
    """
    /start_crawling 엔드포인트를 처리하는 함수
    """
    try:
        data = request.get_json()
        tag = data.get('text', '')
        crawling_data_temp = []

        tumblr_thread = threading.Thread(target=tumblr_crawling, args=(tag, crawling_data_temp))
        jazz_thread = threading.Thread(target=jazz_crawling, args=(crawling_data_temp, tag))

        tumblr_thread.start()
        jazz_thread.start()

        tumblr_thread.join()
        jazz_thread.join()

        columns = ['text', 'date', 'url', 'id', 'web']
        combined_df = pd.DataFrame(crawling_data_temp, columns=columns)
        combined_df['classification'] = combined_df['text'].apply(lambda x: classify_text(x)[0])
        filtered_df = combined_df[combined_df['classification'] == '0'].drop(columns=['classification'])

        result = []
        for _, row in filtered_df.iterrows():
            add_to_database(row['date'], row['text'], row['url'], row['id'], row['web'])
            result.append({
                'text': row['text'],
                'date': row['date'],
                'url': row['url'],
                'id': row['id'],
                'web': row['web'],
                'place': None,
                'picture': None
            })

        return jsonify({'status': 'success', 'data': result})

    except Exception as e:
        return jsonify({'error': str(e)})

def create_app():
    """
    Flask 애플리케이션을 생성하는 함수
    """
    with app.app_context():
        db.create_all()
    return app

if __name__ == "__main__":
    # 새 스레드에서 check_and_update_reports 함수 실행
    #print_thread = threading.Thread(target=check_and_update_reports)
    #print_thread.daemon = True  # 메인 스레드가 종료되면 함께 종료되도록 설정
    #print_thread.start()

    app.run(debug=True, host='0.0.0.0', port=5000)
