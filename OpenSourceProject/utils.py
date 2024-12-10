# utils.py
#크롤링, OCR, 텔레그램 ID 추출 등의 유틸리티 함수를 정의

import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import cv2
import numpy as np
import easyocr
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from datetime import datetime

# 텔레그램 ID 추출 패턴 정의
patterns = [
    r'(?:텔레그램|텔레|텔)\s*[@:【]?\s*([a-zA-Z][a-zA-Z0-9_]+)',  # 텔레그램 관련 패턴 1
    r'텔\s*레\s*[@:【]?\s*([a-zA-Z][a-zA-Z0-9_]+)',               # 텔레그램 관련 패턴 2
    r'텔\s*레\s*그\s*램\s*[@:【]?\s*([a-zA-Z][a-zA-Z0-9_]+)',      # 텔레그램 관련 패턴 3
    r'TLE:\s*([a-zA-Z][a-zA-Z0-9_]+)',                            # 텔레그램 관련 패턴 4
    r'@\s*([a-zA-Z][a-zA-Z0-9_]+)'                                # @패턴으로 텔레그램 ID 추출
]

def extract_telegram_id(text):
    """
    주어진 텍스트에서 텔레그램 ID를 추출하는 함수
    """
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            candidate = match.group(1)
            if re.match(r'^[a-zA-Z][a-zA-Z0-9_]+$', candidate):
                return candidate
    return ''

def extract_text_from_elements(child_divs):
    """
    주어진 요소들에서 텍스트를 추출하는 함수
    """
    total_text = ''
    for child_div in child_divs:
        p_tags = child_div.find_elements(By.TAG_NAME, 'p')
        h1_tags = child_div.find_elements(By.TAG_NAME, 'h1')
        for p_tag in p_tags:
            total_text += p_tag.text
        for h1_tag in h1_tags:
            total_text += h1_tag.text

    return total_text

def tumblr_crawling(tag, crawling_data_temp):
    """
    텀블러에서 주어진 태그로 크롤링하는 함수
    """
    options = webdriver.ChromeOptions()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get(f'https://www.tumblr.com/search/%23{tag}?src=typed_query')
    
    time.sleep(5)

    login_button_aria = driver.find_element(By.XPATH, "//button[@aria-label='로그인']")
    login_button_aria.click()

    time.sleep(2)

    email_button_aria = driver.find_element(By.XPATH, "//button[@aria-label='이메일로 로그인']")
    email_button_aria.click()

    time.sleep(5)
    email_input = driver.find_element(By.XPATH, "//input[@aria-label='email']")
    email_input.send_keys("rkdhsekdhs1@naver.com")

    time.sleep(2)
    next_button = driver.find_element(By.XPATH, "//button[@aria-label='다음']")
    next_button.click()

    time.sleep(2)
    password_input = driver.find_element(By.XPATH, "//input[@name='password']")
    password_input.send_keys("tbvjemforhs!2")

    time.sleep(5)
    try:
        wait = WebDriverWait(driver, 10)
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='Kz53t']//button[@aria-label='로그인']")))

        login_button.click()
    except Exception as e:
        print(f"Error: {e}")

    print("로그인 완료")
    time.sleep(5)
    
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//div[@class="hyiL2"]'))
    )

    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        
        loaded_article = driver.find_elements(By.XPATH, '//article[@class="FtjPK"]')
        
        for tumblr in loaded_article:
            post_url, post_datetime, child_divs = extract_post_details(tumblr, driver)
            if post_url and post_datetime and child_divs:
                total_text = extract_text_from_elements(child_divs)
                telegram_id = extract_telegram_id(total_text)
                crawling_data_temp.append([total_text, post_datetime, post_url, telegram_id, 'tumblr'])
                print(crawling_data_temp)
        
        last_height = new_height

    driver.quit()
    
def extract_post_details(tumblr, driver):
    """
    포스트의 세부 정보를 추출하는 함수
    """
    post_url = ''
    post_datetime = ''
    child_divs = []
    
    try: 
        driver.execute_script("arguments[0].scrollIntoView();", tumblr)
        time.sleep(1)

        try:
            more_option_button = WebDriverWait(tumblr, 10).until(
                EC.element_to_be_clickable((By.XPATH, './/header//span//span//span//button'))
            )
            
            driver.execute_script("arguments[0].click();", more_option_button)
            url_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#glass-container > div > div > div > a'))
            )
            post_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#glass-container > div > div > div > a.X1uIE.XOf8k.qYCWv.YNFqG.v_1X3 > span'))
            )
            post_url = url_element.get_attribute("href")
            time.sleep(3)
            try:
                post_time = post_element.get_attribute('innerHTML')
                if post_time:
                    post_time = post_time.replace("오전", "AM").replace("오후", "PM")
                    try:
                        post_datetime = datetime.strptime(post_time, "%m월 %d일, %p %I:%M")
                        post_datetime = post_datetime.replace(year=2024)
                        post_datetime = post_datetime.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError as e:
                        print(f"날짜 형식 오류: {e}")
            except NoSuchElementException:
                print("포스트 시간 요소를 찾을 수 없습니다.")
                post_time = None
                                
            driver.execute_script("document.body.click();")
            time.sleep(2)
            parent_div = driver.find_element(By.CLASS_NAME, 'GzjsW')
            child_divs = parent_div.find_elements(By.CLASS_NAME, 'k31gt')
                
        except NoSuchElementException as e:
            print("요소를 찾는 중 에러 발생:", e)
            return None, None, None
    except StaleElementReferenceException as e:
        print("StaleElementReferenceException occured")
        return None, None, None
    
    return post_url, post_datetime, child_divs


def jazz_crawling(crawling_data_temp, tag):
    """
    한국 재즈 협회 웹사이트에서 주어진 태그로 크롤링하는 함수
    """
    urls = fetch_urls(tag,start_page=1)
    df = extract_data_to_df(urls)
    df = filter_by_tag(df, tag)
    for _, row in df.iterrows():
        crawling_data_temp.append(row.values.tolist())

def download_image_from_url(url):
    """
    주어진 URL에서 이미지를 다운로드하는 함수
    """
    response = requests.get(url)
    response.raise_for_status()  # HTTP 에러가 발생하면 예외를 발생시킴
    image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image

def increase_contrast(image):
    """
    CLAHE를 사용하여 이미지의 대비를 증가시키는 함수
    """
    lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab_image)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    contrast_image = cv2.merge((l, a, b))
    contrast_image = cv2.cvtColor(contrast_image, cv2.COLOR_LAB2BGR)
    return contrast_image

def extract_text_from_image(url):
    """
    주어진 URL에서 이미지를 다운로드하고 텍스트를 추출하는 함수
    """
    image = download_image_from_url(url)
    contrast_image = increase_contrast(image)
    reader = easyocr.Reader(['ko', 'en'])
    result = reader.readtext(contrast_image)
    extracted_text = ' '.join([detection[1] for detection in result])
    return extracted_text

def fetch_urls(tag, start_page=1):
    all_urls = []  # 모든 URL을 저장할 리스트
    while True:
        try:
            search_url = f"https://koreajazz.co.kr/recruitment/?pageid={start_page}&mod=list"  # 검색 URL
            response = requests.get(search_url)  # 페이지 요청
            response.raise_for_status()  # 상태 확인
            soup = BeautifulSoup(response.text, 'html.parser')  # HTML 파싱
            entries = soup.find_all('td', class_='kboard-list-title')  # 타이틀 목록 추출

            if len(entries) == 1:  # 엔트리가 하나일 경우 반복 종료
                break

            for entry in entries:  # 각 엔트리에 대해 링크 추출
                try:
                    tag_element = entry.select_one('a > div')
                    if tag_element and tag in tag_element.text:
                        a_tag = entry.find('a')
                        if a_tag and 'href' in a_tag.attrs:
                            url = a_tag['href']
                            full_url = f"https://koreajazz.co.kr{url}"
                            all_urls.append(full_url)
                except Exception as e:
                    continue

            start_page += 1  # 페이지 증가
        except Exception as e:
            break
    return list(set(all_urls))  # URL 중복 제거 후 반환

def extract_data_to_df(urls):
    """
    URL 목록에서 데이터를 추출하여 데이터프레임으로 변환하는 함수
    """
    print("start_extract")
    extracted_data = []
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        content_element = soup.select_one('div.content-view table td') or soup.select_one('div.content-view')
        content = content_element.text.strip() if content_element else ''
        date_element = soup.select_one('div.detail-attr.detail-date div.detail-value')
        date_str = date_element.text.strip() if date_element else None
        date = datetime.strptime(date_str, '%Y-%m-%d %H:%M').date() if date_str else None
        telegram_id = extract_telegram_id(content)
        website = '한국재즈협회'
        print(content)
        extracted_data.append([content, date, url, telegram_id, website])
    df = pd.DataFrame(extracted_data, columns=['text', 'date', 'url', 'id', 'web'])
    return df

def filter_by_tag(df, tag):
    """
    데이터프레임에서 주어진 태그로 필터링하는 함수
    """
    return df[df['text'].str.contains(tag, case=False, na=False)]

def classify_text(text):
    """
    주어진 텍스트를 분류하는 함수
    """
    if isinstance(text, str):
        text = [text]
    input_encodings = tokenizer(text, padding=True, truncation=True, return_tensors="pt").to(device)
    model.eval()
    with torch.no_grad():
        outputs = model(**input_encodings)
    logits = outputs.logits
    predicted_labels = logits.argmax(dim=1).tolist()
    return [str(label) for label in predicted_labels]

# 모델과 토크나이저 로드
model_path = "./model4"  # 모델 경로
tokenizer = AutoTokenizer.from_pretrained(model_path)  # 토크나이저 로드
model = AutoModelForSequenceClassification.from_pretrained(model_path, num_labels=2)  # 모델 로드
device = torch.device("cpu")  # 디바이스 설정 (CPU)
model = model.to(device)  # 모델을 디바이스로 이동
