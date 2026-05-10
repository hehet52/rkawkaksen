import pandas as pd
import glob

csv_files = glob.glob("csv/*.csv")

if not csv_files:
    print("❌ csv/ 폴더에 파일이 없습니다.")
else:
    df_list  = [pd.read_csv(f) for f in csv_files]
    final_df = pd.concat(df_list, ignore_index=True)
    final_df.to_csv("final_dataset.csv", index=False)

    print("✅ final_dataset.csv 생성 완료!")
    print(f"   총 행 수: {len(final_df)}")
    print("\n라벨별 데이터 수:")
    label_map = {0:"정상", 1:"눈감김", 2:"하품", 3:"고개숙임"}
    for label, count in final_df['Label'].value_counts().sort_index().items():
        print(f"  {label_map[label]} (label={label}): {count}행")
    print("\n미리보기:")
    print(final_df.head())