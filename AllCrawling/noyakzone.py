import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re #정규표현식 위해 import 

patterns = [
    r'(?:텔레그램|텔레|텔)\s*[@:【]?\s*([a-zA-Z][a-zA-Z0-9_]+)',  # "텔레그램", "텔레", "텔" 다음에 영문자로 시작하는 단어 추출
    r'텔\s*레\s*[@:【]?\s*([a-zA-Z][a-zA-Z0-9_]+)',  # "텔 레" 다음에 영문자로 시작하는 단어 추출
    r'텔\s*레\s*그\s*램\s*[@:【]?\s*([a-zA-Z][a-zA-Z0-9_]+)',  # "텔 레 그 램" 다음에 영문자로 시작하는 단어 추출
    r'TLE:\s*([a-zA-Z][a-zA-Z0-9_]+)',  # "TLE:" 다음에 영문자로 시작하는 단어 추출
    r'@\s*([a-zA-Z][a-zA-Z0-9_]+)'  # "@" 다음에 영문자로 시작하는 단어 추출
]


# Tumblr API 키 설정
api_key = 'C5z3IeO5LAe5fN3M17zx76m1mdD01T0fKk6lnRw3wdOqOUJYsI'

# DataFrame 초기화
crawling_data = pd.DataFrame(columns=['name', 'target', 'title', 'content', 'timestamp'])
crawling_data_temp = pd.DataFrame(columns=['name', 'target', 'title', 'content', 'timestamp'])  # crawling_data_temp 선언

# 검색하고자 하는 태그
tag = '아이스작대기'

# Tumblr API를 사용하여 태그 검색 결과 가져오기
url = f'https://api.tumblr.com/v2/tagged?tag={tag}&api_key={api_key}'
response = requests.get(url)
data = response.json()

# 검색 결과에서 내용, 사진, 비디오, URL, 작성 시간 추출
for post in data['response']:
    print(f"블로그 이름: {post['blog_name']}")
    print(f"포스트 ID: {post['id']}")
    print(f"포스트 타입: {post['type']}")
    
    # 게시물 URL 추출
    post_url = post['post_url']
    print(f"게시물 URL: {post_url}")
    
    # 텍스트 포스트 처리
    if post['type'] == 'text':
        # HTML 태그 파싱
        soup = BeautifulSoup(post['body'], 'html.parser')
        
        # <h1>과 <p> 태그 내부 텍스트 추출
        h1_text = soup.find('h1').get_text() if soup.find('h1') else ''
        p_text = soup.find('p').get_text() if soup.find('p') else ''
        total_text = h1_text + p_text
        
        # 게시물 작성 시간 추출
        post_timestamp = post['timestamp']
        post_datetime = datetime.fromtimestamp(post_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        telegram_id = ""
        for pattern in patterns:
            match = re.search(pattern,total_text)
            if match:
                candidate = match.group(1)
                if re.match(r'^[a-zA-Z][a-zA-Z0-9_]+$', candidate):
                    telegram_id = candidate
                    break
        print(f"제목: {h1_text}\n내용: {p_text}\n작성 시간: {post_datetime}\n텔레그램 ID : {telegram_id if telegram_id else 'x'}")
        
        # crawling_data_temp에 데이터 추가
        crawling_data_temp.loc[len(crawling_data_temp)] = [post['blog_name'], post_url, h1_text, p_text, post_datetime]
    
    # 사진 포스트 처리
    elif post['type'] == 'photo':
        print("사진 URL:")
        for photo in post['photos']:
            print(photo['original_size']['url'])
    
    # 비디오 포스트 처리
    elif post['type'] == 'video':
        print(f"비디오: {post['video_url']}")
    
    # crawling_data_temp에 데이터 추가
    crawling_data_temp.loc[len(crawling_data_temp)] = [post['blog_name'], post_url, '', '', post['timestamp']]
    print("\n")

# CSV 파일로 저장
base_dir = "C:\\Users\\okhi3\\Desktop\\RawData\\crawling"
os.makedirs(base_dir, exist_ok=True)
crawling_data = pd.concat([crawling_data, crawling_data_temp], ignore_index=True) 
crawling_data.to_csv(os.path.join(base_dir, "crawling_data.csv"), index=False, encoding='utf-8-sig')
