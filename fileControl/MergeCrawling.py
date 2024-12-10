import os
import pandas as pd
import chardet

# 파일 경로
folder_path = "C:\\Users\\okhi3\\Desktop\\crawling"
output_file = 'crawling_data.csv'

# 폴더 내의 모든 CSV 파일을 하나의 데이터프레임으로 통합
all_data = pd.DataFrame()
for file in os.listdir(folder_path):
    if file.endswith('.csv'):
        print('ㅎㅇ' + file)
        with open(os.path.join(folder_path, file), 'rb') as f:
            result = chardet.detect(f.read())
        encoding = result['encoding']
        current_data = pd.read_csv(os.path.join(folder_path, file), encoding=encoding)
        
        # 1. data 열의 공백 제거
        current_data['data'] = current_data['data'].str.strip()
        
        # 2. 중복 제거
        current_data = current_data.drop_duplicates(subset=['data'])
        
        # 3. 중복 제거 후 공백 추가
        current_data['data'] = current_data['data'].str.strip()
        
        all_data = pd.concat([all_data, current_data[['data', 'target']]], ignore_index=True)

# 4. 통합된 데이터프레임을 CSV 파일로 저장
all_data.to_csv(os.path.join(folder_path, output_file), index=False)