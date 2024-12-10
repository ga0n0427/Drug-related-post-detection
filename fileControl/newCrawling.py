import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import os

# 검색어 목록
search_terms = ["시원한 술", "나가사끼"]

# 네이버 크롤링할 때 필요한 헤더 (필요할 때 사용)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# URL 저장 리스트
all_urls = []

# 데이터 저장 함수
def save_data(urls, file_name):
    # 저장할 디렉토리 지정
    base_dir = "C:\\Users\\okhi3\\Desktop\\data\\crawling"
    full_path = os.path.join(base_dir, file_name)

    # 디렉터리 존재 확인 및 생성
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # 텍스트 파일로 저장
    with open(full_path, "w", encoding="utf-8") as file:
        for url in urls:
            
            # 블라인드 크롤링할 것이기 때문에 url 형식 변경
            url = f"https://www.teamblind.com{url}"
            file.write(f"{url}\n")

# 검색어를 순회하며 크롤링 수행
url_count = 0  # 총 URL 개수 카운트
for search_term in search_terms:
    page = 1
    total_entries = 0
    failed_entries = 0
    url_seperate_count = 0 # 각 카테고리당 url

    while True:  # 무한 루프
        try:
            encoded_search_query = quote(search_term)
            search_url = f"https://www.teamblind.com/kr/search/{encoded_search_query}?page={page}"
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()

            # 리디렉션된 URL 확인
            redirected_url = response.url
            print(f"Redirected URL: {redirected_url}")

            # 리디렉션된 URL로 새로운 요청 보내기
            response = requests.get(redirected_url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            print(soup)
            entries = soup.select('div.tit a')  # div 태그 중 class가 tit인 요소의 하위 a 태그 선택

            # 페이지에 결과가 없으면 다음 검색어로 넘어감
            if not entries:
                break

            total_entries += len(entries)  # 총 엔트리 개수 누적
            
            for entry in entries:
                try:
                    url = entry['href']
                    print(url)
                    if url:
                        all_urls.append(url)  # 모든 URL을 저장
                        url_count += 1  # URL 개수 카운트 증가
                        url_seperate_count += 1 # 각 카테고리당 url
                        print("s",url_seperate_count)
                        print("u",url_count)
                    else:
                        failed_entries += 1  # URL을 찾지 못한 경우
                except Exception as e:
                    print(f"Error processing entry: {e}")
                    failed_entries += 1  # 예외 발생 시 실패로 간주하고 카운트 증가
                    continue

            if url_seperate_count >= 500:  # 각 검색어당 200개의 URL을 가져왔으면 다음 검색어로 이동
                break

            page += 1
        except Exception as e:
            print(f"Error processing page {page} for {search_term}: {e}")
            break

    print(f"Search term: {search_term} - Total entries: {total_entries}, Failed entries: {failed_entries}")

# 중복 제거 후 URL 저장
unique_urls = list(set(all_urls))
print(f"Total number of unique URLs: {len(unique_urls)}")
save_data(unique_urls, 'unique_urls_after_deduplication.txt')

