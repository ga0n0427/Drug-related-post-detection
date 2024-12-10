## 프로젝트 개요

이 프로젝트는 주요 사이트에서 자동으로 크롤링한 데이터를 활용하여 게시물이 마약 관련 글인지 판단하는 시스템을 제공합니다. KcBERT 모델을 기반으로 마약 게시물을 분류하며, 게시물 데이터는 PostgreSQL에서 읽어 처리합니다.

## 주요 기능

### 크롤링:

- 주요 웹사이트에서 자동으로 게시물을 크롤링하여 최신 데이터를 확보합니다.

### 게시물 분류:

- PostgreSQL 데이터베이스에서 크롤링된 게시물을 불러와 분석합니다.
- 게시물이 마약 관련 내용인지 아닌지 분류합니다.

### AI 기반 마약 게시물 탐지:

- 파인튜닝된 KoBERT 모델(beomi/kcbert-base)을 활용하여 게시물의 내용을 분석합니다.
- 높은 정확도로 마약 게시물을 탐지합니다.

## 설치 가이드

아래 명령어를 통해 필요한 패키지를 설치하세요.

```bash
# Huggingface Transformers 및 기타 필수 패키지 설치
!pip install -q -U git+https://github.com/huggingface/transformers.git
!pip install -q -U git+https://github.com/huggingface/accelerate.git
!pip install -q datasets
!pip install -q torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
!pip install pandas scikit-learn numpy
```
## 사용 방법

### 1. 데이터 준비

- 크롤링된 데이터를 CSV 파일 형태로 저장합니다.
- `data` 열에 게시물 텍스트, `target` 열에 레이블(0: 마약, 1: 일반)을 포함해야 합니다.

### 2. 모델 학습

- 데이터셋을 전처리한 후, KoBERT 모델을 Fine-Tuning합니다.
- 학습된 모델은 입력 텍스트를 분석하여 게시물의 레이블을 예측합니다.

### 3. 예측 실행

다음과 같은 방식으로 데이터를 입력하고 예측 결과를 확인할 수 있습니다.

```python
# 입력 데이터 예시
input_data = [
    "아이스작대기 텔레 @blueseal1004...",
    "이 글은 GPU 관련 정보입니다.",
    ...
]

# 예측 결과 출력
for i, input_text in enumerate(input_data):
    predicted_label = predicted_labels[i].item()
    print(f"Input: {input_text} - Predicted Label: {valid_label(predicted_label)}")
```

## 라이센스 
MIT 라이센스를 따릅니다. 더 자세한 내용은 LICENSE 파일을 참조하세요.
