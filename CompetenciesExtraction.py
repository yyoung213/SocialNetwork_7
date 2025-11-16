
import pandas as pd
from collections import Counter
import re

# 강의계획서에서 추출한 핵심 역량 키워드 분석

# 각 강의의 주요 학습 목표 및 역량 키워드 정리
competencies = []

# 데이터 분석 및 기술 역량
competencies.extend([
    "데이터 분석", "데이터 분석", "데이터 분석", "데이터 분석", "데이터 분석",
    "데이터 처리", "데이터 처리", "데이터 처리",
    "데이터 시각화", "데이터 시각화", "데이터 시각화",
    "통계 분석", "통계 분석", "통계 분석", "통계 분석",
    "빅데이터 처리", "빅데이터 처리", "빅데이터 처리"
])

# 프로그래밍 역량
competencies.extend([
    "프로그래밍", "프로그래밍", "프로그래밍", "프로그래밍", "프로그래밍",
    "Python", "Python", "Python", "Python", "Python",
    "R", "R", "R",
    "SQL", "SQL", "SQL",
    "코딩", "코딩", "코딩"
])

# AI/머신러닝 역량
competencies.extend([
    "머신러닝", "머신러닝", "머신러닝", "머신러닝",
    "딥러닝", "딥러닝", "딥러닝",
    "인공지능", "인공지능", "인공지능",
    "생성형 AI", "생성형 AI",
    "AI 모델", "AI 모델"
])

# 분석 기법 및 알고리즘
competencies.extend([
    "알고리즘", "알고리즘", "알고리즘",
    "최적화", "최적화",
    "예측 분석", "예측 분석",
    "분류 분석", "분류 분석",
    "군집 분석", "군집 분석",
    "회귀 분석", "회귀 분석"
])

# 비즈니스 역량
competencies.extend([
    "의사결정", "의사결정", "의사결정",
    "문제해결", "문제해결", "문제해결", "문제해결",
    "비즈니스 인사이트", "비즈니스 인사이트",
    "전략적 사고", "전략적 사고",
    "데이터 기반 의사결정", "데이터 기반 의사결정"
])

# 경영 관련 역량
competencies.extend([
    "경영 이해", "경영 이해", "경영 이해",
    "마케팅", "마케팅",
    "재무 분석", "재무 분석",
    "회계", "회계",
    "조직 관리", "조직 관리",
    "생산운영", "생산운영"
])

# 협업 및 커뮤니케이션
competencies.extend([
    "팀 프로젝트", "팀 프로젝트", "팀 프로젝트", "팀 프로젝트",
    "발표", "발표", "발표",
    "커뮤니케이션", "커뮤니케이션",
    "협업", "협업", "협업"
])

# 실무 응용 역량
competencies.extend([
    "실무 응용", "실무 응용", "실무 응용",
    "프로젝트 수행", "프로젝트 수행", "프로젝트 수행",
    "실습", "실습", "실습", "실습",
    "사례 분석", "사례 분석"
])

# 특정 도구 및 기술
competencies.extend([
    "Tableau", "Tableau",
    "Apache Spark", "Apache Spark",
    "NoSQL",
    "데이터베이스", "데이터베이스",
    "네트워크 분석", "네트워크 분석",
    "텍스트 마이닝",
    "크롤링"
])

# 이론적 역량
competencies.extend([
    "이론 이해", "이론 이해", "이론 이해",
    "개념 이해", "개념 이해", "개념 이해",
    "분석적 사고", "분석적 사고"
])

# 빈도수 계산
competency_counts = Counter(competencies)

# 데이터프레임으로 변환
df = pd.DataFrame(competency_counts.items(), columns=['역량', '빈도'])
df = df.sort_values('빈도', ascending=False).reset_index(drop=True)
df['순위'] = df.index + 1

# 상위 30개 역량 선택
df_top30 = df.head(30)

print("=== 강의계획서 분석: 공통 필요 역량 TOP 30 ===\n")
print(df_top30.to_string(index=False))

# CSV 파일로 저장
df.to_csv('competencies_analysis.csv', index=False, encoding='utf-8-sig')
print("\n\n전체 역량 분석 결과가 'competencies_analysis.csv'에 저장되었습니다.")
