import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns

# Windows 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'   # 맑은 고딕 (Windows 기본 한글 폰트)
plt.rcParams['axes.unicode_minus'] = False       # 마이너스 기호 깨짐 방지
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (classification_report,
                             confusion_matrix,
                             accuracy_score)
import pickle
import os

# ══════════════════════════════════════════════════════
# 1. 데이터 불러오기
# ══════════════════════════════════════════════════════
df = pd.read_csv("final_dataset.csv")

print("=== 데이터 기본 정보 ===")
print(f"총 행 수: {len(df)}")
label_map = {0:"정상", 1:"눈감김", 2:"하품", 3:"고개숙임"}
for label, count in df["Label"].value_counts().sort_index().items():
    print(f"  {label_map[int(label)]}: {count}행")

# ══════════════════════════════════════════════════════
# 2. 결측치 제거
# ══════════════════════════════════════════════════════
df.dropna(inplace=True)

# ══════════════════════════════════════════════════════
# 3. 입력(X) / 정답(y) 분리
# ══════════════════════════════════════════════════════
X = df[["EAR", "MAR", "HeadAngle"]].values
y = df["Label"].values

# ══════════════════════════════════════════════════════
# 4. 학습 / 테스트 데이터 분리 (8:2)
# ══════════════════════════════════════════════════════
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\n학습 데이터: {len(X_train)}행")
print(f"테스트 데이터: {len(X_test)}행")

# ══════════════════════════════════════════════════════
# 5. 정규화 (데이터 스케일 맞추기)
# ══════════════════════════════════════════════════════
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test  = scaler.transform(X_test)

# ══════════════════════════════════════════════════════
# 6. 모델 학습 (RandomForest)
# ══════════════════════════════════════════════════════
print("\n모델 학습 중...")
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42
)
model.fit(X_train, y_train)
print("✅ 학습 완료!")

# ══════════════════════════════════════════════════════
# 7. 성능 평가
# ══════════════════════════════════════════════════════
y_pred = model.predict(X_test)

acc = accuracy_score(y_test, y_pred)
print(f"\n=== 모델 성능 ===")
print(f"정확도: {acc * 100:.2f}%")
print("\n상세 리포트:")
print(classification_report(
    y_test, y_pred,
    target_names=["정상", "눈감김", "하품", "고개숙임"]
))

# ══════════════════════════════════════════════════════
# 8. 혼동 행렬 시각화
# ══════════════════════════════════════════════════════
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(7, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["정상","눈감김","하품","고개숙임"],
            yticklabels=["정상","눈감김","하품","고개숙임"])
plt.title("혼동 행렬 (Confusion Matrix)")
plt.xlabel("예측값")
plt.ylabel("실제값")
plt.tight_layout()
plt.savefig("confusion_matrix.png")
plt.show()
print("✅ confusion_matrix.png 저장 완료")

# ══════════════════════════════════════════════════════
# 9. 모델 저장 (나중에 실시간 감지에 사용)
# ══════════════════════════════════════════════════════
with open("drowsiness_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

print("✅ 모델 저장 완료: drowsiness_model.pkl")
print("✅ 스케일러 저장 완료: scaler.pkl")