import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from urllib.parse import quote
import time
import os
import re

# DataFrame 초기화
crawling_data = pd.DataFrame(columns=['data', 'target'])
crawling_data_temp = pd.DataFrame(columns=['data', 'target'])  # crawling_data_temp 선언
s = 0
v = 0
# Chrome 드라이버 설정
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
# Tumblr로 이동
driver.get("https://www.tumblr.com/")

wait = WebDriverWait(driver, 20)
login_button_selector = ".TRX6J.CxLjL.qjTo7.IMvK3"
login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, login_button_selector)))
login_button.click()

email_login_button_selector = "button[aria-label='Continue with email']"
email_login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, email_login_button_selector)))
email_login_button.click()

email_input_selector = "input[type='email']"
email_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, email_input_selector)))
email_input.send_keys("rkdhsekdhs1@naver.com")

password_input_selector = "input[type='password']"
password_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, password_input_selector)))
password_input.send_keys("tbvjemforhs!2")

login_submit_button_selector = "span.EvhBA"
login_submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, login_submit_button_selector)))


# 로그인 완료 후 충분히 기다림
time.sleep(5)
a = ["사끼", "브액","케타민", "빙두", "아이스작대기", "시원한술", "차가운술"]
for i, j in enumerate(a):
    
    # 한글 URL 인코딩
    encoded_search_query = quote(j)
    search_url = f"https://www.tumblr.com/search/{j}?src=typed_query"

    # 검색 결과 페이지로 이동
    driver.get(search_url)

    # 검색 결과 로딩을 위해 기다림
    time.sleep(10)

    wait = WebDriverWait(driver, 10)
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    found_p_tags = set()  # 발견된 p 태그의 텍스트를 저장할 집합

    while True:
        div_elements = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "GzjsW")))
        for div_element in div_elements:
            author_element = div_element.find_element(By.CSS_SELECTOR, "a[rel='author']")
            author_url = author_element.get_attribute("href")
            author_name = author_url.split("/")[-1]
            print(f"작성자: {author_name}")
            crawling_data_temp.loc[len(crawling_data_temp)] = [text_content, author_name]
            
            text_content = ''
            k31gt_elements = div_element.find_elements(By.CLASS_NAME, "k31gt")
            for k31gt_element in k31gt_elements:
                # XPath를 사용해 p, h1, h2 태그의 텍스트 추출
                text_elements = k31gt_element.find_elements(By.XPATH, ".//*[self::p or self::h1 or self::h2]")
                for element in text_elements:
                    text_content = text_content + element.text
            if text_content not in found_p_tags:  # 새로운 텍스트라면 출력하고 저장
                print(text_content)
                found_p_tags.add(text_content)
                crawling_data_temp.loc[len(crawling_data_temp)] = [text_content, 0]  # crawling_data_temp에 데이터 추가
                if len(crawling_data_temp) >= 100:  # 일정 크기 이상이 되면 통합
                    crawling_data = pd.concat([crawling_data, crawling_data_temp], ignore_index=True)
                    crawling_data_temp = pd.DataFrame(columns=['data', 'target'])  # crawling_data_temp 초기화
                    s += 1
        # 스크롤 다운
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 로딩 대기
        
        # 스크롤이 더 이상 안 내려가는지 확인
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # 더 이상 스크롤이 내려가지 않으면 반복 종료
        last_height = new_height

    # 작업 완료 후 드라이버 종료
    # 남은 데이터 저장
    base_dir = "C:\\Users\\okhi3\\Desktop\\RawData\\crawling"
    os.makedirs(base_dir, exist_ok=True)

    # 통합된 데이터 저장
    if not crawling_data.empty:
        crawling_data = pd.concat([crawling_data, crawling_data_temp], ignore_index=True)  # 마지막으로 crawling_data_temp와 통합
        crawling_data.to_csv(os.path.join(base_dir, "crawling_data.csv"), index=False, encoding='utf-8-sig')

driver.quit()  # 드라이버 종료