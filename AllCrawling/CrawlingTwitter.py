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
import re #정규표현식 위해 import 

patterns = [
    r'(?:텔레그램|텔레|텔)\s*[@:【]?\s*([a-zA-Z][a-zA-Z0-9_]+)',  # "텔레그램", "텔레", "텔" 다음에 영문자로 시작하는 단어 추출
    r'텔\s*레\s*[@:【]?\s*([a-zA-Z][a-zA-Z0-9_]+)',  # "텔 레" 다음에 영문자로 시작하는 단어 추출
    r'텔\s*레\s*그\s*램\s*[@:【]?\s*([a-zA-Z][a-zA-Z0-9_]+)',  # "텔 레 그 램" 다음에 영문자로 시작하는 단어 추출
    r'TLE:\s*([a-zA-Z][a-zA-Z0-9_]+)',  # "TLE:" 다음에 영문자로 시작하는 단어 추출
    r'@\s*([a-zA-Z][a-zA-Z0-9_]+)'  # "@" 다음에 영문자로 시작하는 단어 추출
]

options = webdriver.ChromeOptions()
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://twitter.com/home")

# 로그인 입력 필드를 찾고 값을 입력하기 위해 페이지가 로드될 때까지 잠시 대기
time.sleep(5)

login_button_start = driver.find_element(By.XPATH,"//*[@id='react-root']/div/div/div[2]/main/div/div/div[1]/div[1]/div/div[3]/div[4]/a")
login_button_start.click()

time.sleep(5)

# 로그인 입력 필드 찾기 (name 속성 사용)
login_input = driver.find_element(By.NAME, "text")
login_input.send_keys("cheongaon9543")
time.sleep(2)
next_button = driver.find_element(By.XPATH, "//*[@id='layers']/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]")
next_button.click()

# 비밀번호 입력 필드 찾기
time.sleep(2)
password_input = driver.find_element(By.NAME, "password")
password_input.send_keys("tbvjemforhs!2")
time.sleep(2)
login_button = driver.find_element(By.XPATH, "//span[contains(text(), 'Log in')]")
login_button.click()

# 로그인 후 페이지 로딩 대기
time.sleep(15)

search_input = driver.find_element(By.XPATH, '//input[@data-testid="SearchBox_Search_Input"]')
search_input.send_keys("#시원한술" + Keys.ENTER)

WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.XPATH, '//article[@data-testid="tweet"]'))
)

# 검색 결과 로딩 대기
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]'))
)

# 현재 로드된 트윗들을 가져옵니다.
loaded_tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')

# 스크롤 높이 초기화
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    loaded_tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
    for tweet in loaded_tweets:
        try: 
            
            driver.execute_script("arguments[0].scrollIntoView();", tweet)
            time.sleep(1)
            
            # 사용자 이름, 게시 시간, 그리고 트윗 내용 가져오기
            try:
                user_name = tweet.find_element(By.XPATH, ".//span[contains(@class, 'css-1jxf684')]").text
                post_time_div = tweet.find_element(By.XPATH, ".//div[contains(@class, 'css-175oi2r r-18u37iz r-1q142lx')]")
                post_time = post_time_div.find_element(By.TAG_NAME, "time").get_attribute('datetime')
                content = tweet.find_element(By.XPATH, ".//div[contains(@class, 'css-146c3p1 r-8akbws r-krxsd3 r-dnmrzs r-1udh08x r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-bnwqim')]").text
                a_tag = tweet.find_element(By.XPATH, ".//div[contains(@class, 'css-175oi2r r-18u37iz r-1q142lx')]//a")
                getUrl = a_tag.get_attribute('href')
                
                # 게시 시간 형식 변환
                post_time_obj = datetime.fromisoformat(post_time.replace('Z', '+00:00'))
                formatted_post_time = post_time_obj.strftime('%Y-%m-%d %H:%M:%S')
                
                telegram_id = ""
                for pattern in patterns:
                    match = re.search(pattern,content)
                    if match:
                        candidate = match.group(1)
                        if re.match(r'^[a-zA-Z][a-zA-Z0-9_]+$', candidate):
                            telegram_id = candidate
                            break
                print(f"사용자: {user_name}, 게시 시간: {formatted_post_time}, 내용: {content}, URL : {getUrl}, 텔레그램 ID : {telegram_id if telegram_id else 'x'}\n")
            except NoSuchElementException as e:
                print("요소를 찾는 중 에러 발생:", e)
                continue
        except StaleElementReferenceException as e:
            print("StaleElementReferenceException occured")
            continue
    last_height = new_height

# 브라우저 종료
driver.quit()
