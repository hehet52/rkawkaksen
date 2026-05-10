# 감자만두
# 졸음 감지 프로젝트

MediaPipe와 RandomForest를 이용한 실시간 졸음 감지 시스템

## 감지 상태
- 정상 (label=0)
- 눈감김 (label=1)
- 하품 (label=2)
- 고개숙임 (label=3)

## 모델 정확도
- 87.77%

## 설치 방법
pip install -r requirements.txt

## 실행 순서
1. 영상에서 특징값 추출
   python extract.py

2. CSV 파일 합치기
   python merge.py

3. 모델 학습
   python train.py

4. 테스트
   python test.py

## 파일 구조
drowsiness_project/
  extract.py
  merge.py
  train.py
  test.py
  drowsiness_model.pkl
  scaler.pkl
  final_dataset.csv
  confusion_matrix.png
  requirements.txt

  ## 모델 파일 안내
drowsiness_model.pkl은 용량 문제로 GitHub에 포함되지 않습니다.
저장소를 받은 후 아래 명령어로 직접 생성하세요.

pip install -r requirements.txt
python train.py

