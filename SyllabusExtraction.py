
# 역량을 카테고리별로 재분류하여 더 명확한 인사이트 제공

import pandas as pd

# 카테고리별 역량 분류
categories = {
    "데이터 & 분석 기술": [
        "데이터 분석", "데이터 처리", "데이터 시각화", "통계 분석", 
        "빅데이터 처리", "예측 분석", "분류 분석", "군집 분석", 
        "회귀 분석", "텍스트 마이닝", "네트워크 분석", "크롤링"
    ],
    "프로그래밍 & 도구": [
        "프로그래밍", "Python", "R", "SQL", "코딩",
        "Tableau", "Apache Spark", "NoSQL", "데이터베이스", "알고리즘"
    ],
    "AI & 머신러닝": [
        "머신러닝", "딥러닝", "인공지능", "생성형 AI", "AI 모델"
    ],
    "비즈니스 & 경영": [
        "의사결정", "문제해결", "비즈니스 인사이트", "전략적 사고",
        "데이터 기반 의사결정", "경영 이해", "마케팅", "재무 분석",
        "회계", "조직 관리", "생산운영", "최적화"
    ],
    "협업 & 커뮤니케이션": [
        "팀 프로젝트", "발표", "커뮤니케이션", "협업"
    ],
    "실무 & 응용": [
        "실무 응용", "프로젝트 수행", "실습", "사례 분석"
    ],
    "이론 & 개념": [
        "이론 이해", "개념 이해", "분석적 사고"
    ]
}

# 원본 데이터 불러오기
df = pd.read_csv('competencies_analysis.csv')

# 각 역량을 카테고리에 매핑
def categorize_competency(competency):
    for category, items in categories.items():
        if competency in items:
            return category
    return "기타"

df['카테고리'] = df['역량'].apply(categorize_competency)

# 카테고리별 통계
category_stats = df.groupby('카테고리')['빈도'].agg(['sum', 'count']).reset_index()
category_stats.columns = ['카테고리', '총 빈도', '역량 수']
category_stats = category_stats.sort_values('총 빈도', ascending=False).reset_index(drop=True)

print("=== 카테고리별 역량 분석 ===\n")
print(category_stats.to_string(index=False))
print(f"\n총 역량 항목 수: {len(df)}")
print(f"총 빈도 합계: {df['빈도'].sum()}")

# 카테고리별 상세 역량 출력
print("\n\n=== 카테고리별 상세 역량 (빈도순) ===\n")
for category in category_stats['카테고리']:
    print(f"\n【{category}】")
    category_df = df[df['카테고리'] == category].sort_values('빈도', ascending=False)
    for idx, row in category_df.iterrows():
        print(f"  • {row['역량']}: {row['빈도']}회")

# 카테고리별 결과 저장
category_stats.to_csv('competencies_by_category.csv', index=False, encoding='utf-8-sig')
df.to_csv('competencies_categorized.csv', index=False, encoding='utf-8-sig')

print("\n\n분석 결과가 저장되었습니다:")
print("- competencies_by_category.csv (카테고리별 통계)")
print("- competencies_categorized.csv (역량별 카테고리 매핑)")
