import pandas as pd

# CSV 파일에서 데이터 불러오기
crawling_data = pd.read_csv('crawling_data.csv')

# 'data' 열의 데이터 타입 확인
print(crawling_data['data'].dtypes)

# 'data' 열의 값이 문자열이 아닌 경우 처리
if crawling_data['data'].dtype != 'object':
    crawling_data['data'] = crawling_data['data'].astype(str)

# 데이터프레임의 값들의 공백 제거
crawling_data['data'] = crawling_data['data'].str.strip()

# 중복 제거
crawling_data.drop_duplicates(subset=['data'], inplace=True)

# 중복 제거 후 다시 값들이 가지고 있던 공백 추가
crawling_data['data'] = crawling_data['data'].apply(lambda x: ' '.join(x.split()))

# 중복 제거 및 공백 처리된 데이터프레임을 CSV 파일로 저장
crawling_data.to_csv('cleaned_crawling_data.csv', index=False, encoding='utf-8-sig')