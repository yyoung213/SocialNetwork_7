"""개발관련_raw 데이터 확인"""
import pandas as pd

df = pd.read_csv('developer_bipartite_skill_edges.csv', encoding='utf-8-sig')
print(f'총 행 수: {len(df)}')
print(f'고유 기업 수: {df["기업명"].nunique()}')
print(f'고유 스킬 수: {df["Skill"].nunique()}')
print(f'\n상위 5개 기업 (스킬 수 기준):')
company_skills = df.groupby('기업명')['Skill'].count().sort_values(ascending=False)
print(company_skills.head())
print(f'\n상위 5개 스킬 (기업 수 기준):')
skill_companies = df.groupby('Skill')['기업명'].count().sort_values(ascending=False)
print(skill_companies.head())



