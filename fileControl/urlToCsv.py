# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# import os

# script_dir = os.path.dirname(os.path.abspath(__file__))
# # 파일 목록
# a = [os.path.join(script_dir, 'unique_urls_after_deduplication.txt')]
# b = [os.path.join(script_dir, 'ameba.csv')]
# # 두 리스트를 함께 반복
# for i, (input_file, output_file) in enumerate(zip(a, b)):
#     # 텍스트 파일에서 URL 읽어오기
#     with open(input_file, 'r', encoding='utf-8') as file:
#             urls = [line.strip() for line in file.readlines()]

#         # 추출한 텍스트를 저장할 리스트
#     extracted_texts = []

#         # 각 URL에서 데이터 추출
#     for url in urls:
#         print(url)
#         response = requests.get(url)
#         soup = BeautifulSoup(response.content, 'html.parser')
            
#         # 각 URL의 모든 <p> 태그 텍스트를 하나로 합침
#         combined_text = ' '.join(p.text.strip() for p in soup.find_all('p', class_='article-body__content') if p.text.strip())
#         print(combined_text)
#         if combined_text:
#             extracted_texts.append(combined_text)

#         # 중복 제거
#         unique_texts = list(set(extracted_texts))

#         # 데이터프레임 생성
#         df = pd.DataFrame({'data': unique_texts, 'target': 0})

#         # 데이터프레임 저장 또는 출력
#         df.to_csv(output_file, index=False)
#         print(f"Processing {input_file} to {output_file}")
#         print(df)


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import pandas as pd
from selenium.webdriver.chrome.options import Options
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-extensions")

# 웹 드라이버 초기화
driver = webdriver.Chrome(options=chrome_options)

script_dir = os.path.dirname(os.path.abspath(__file__))
# 파일 목록
a = [os.path.join(script_dir, 'unique_urls_after_deduplication.txt')]
b = [os.path.join(script_dir, 'ameba.csv')]
cnt = 0
for i, (input_file, output_file) in enumerate(zip(a, b)):
    # 텍스트 파일에서 URL 읽어오기
    with open(input_file, 'r', encoding='utf-8') as file:
            urls = [line.strip() for line in file.readlines()]

            # 추출한 텍스트를 저장할 리스트
            extracted_texts = []
            for url in urls:
                print(url)
                # URL 열기
                driver.get(url)

                # 동적으로 생성되는 콘텐츠 대기
                wait = WebDriverWait(driver, 100)
                try:
                    content = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'contents-txt')))
                    text = content.text
                    # div 클래스 article-view-head에 있는 h2 태그의 텍스트 가져오기
                    article_head = driver.find_element(By.CLASS_NAME, 'article-view-head')
                    h2_text = article_head.find_element(By.TAG_NAME, 'h2').text

                    # contents-txt 클래스의 텍스트와 h2 태그의 텍스트를 합치기
                    combined_text = h2_text + ' ' + text
                    print(combined_text)
                    cnt+=1
                    print(cnt)
                    if combined_text:
                        extracted_texts.append(combined_text)
                    else:
                        print(f"No content found for URL: {url}")
                        continue
                except:
                    print(f"Error occurred for URL: {url}")
                    continue

            # 중복 제거
            unique_texts = list(set(extracted_texts))

            # 데이터프레임 생성
            df = pd.DataFrame({'data': unique_texts, 'target': 0})

            # 데이터프레임 저장 또는 출력
            df.to_csv(output_file, index=False)
            print(f"Processing {input_file} to {output_file}")
            print(df)

# 웹 드라이버 종료
driver.quit()

