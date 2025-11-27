# Bipartite Network 시각화 전략 가이드
## data_bipartite_skill_2mode.net 기반 인사이트 도출 전략

### 네트워크 구조
- **총 노드 수**: 1,034개
- **기업 (Mode 1)**: 539개
- **스킬 (Mode 2)**: 495개
- **엣지**: 기업-스킬 연결 (구인공고에서 요구하는 스킬)

---

## 전략 1: 기본 Bipartite 레이아웃 (양쪽 정렬)

### 목적
- 두 모드(기업 vs 스킬)를 명확히 구분하여 전체 구조 파악
- 어떤 기업이 어떤 스킬을 요구하는지 한눈에 확인

### 구현 방법
```python
import networkx as nx
import matplotlib.pyplot as plt

# 2-mode 네트워크 읽기
G = nx.read_pajek('data_bipartite_skill_2mode.net', encoding='utf-8')

# Bipartite 레이아웃 (양쪽 정렬)
# 기업: 왼쪽, 스킬: 오른쪽
pos = {}
companies = [n for n in G.nodes() if G.nodes[n].get('bipartite') == 0]
skills = [n for n in G.nodes() if G.nodes[n].get('bipartite') == 1]

# 기업을 왼쪽에 세로로 배치
for i, company in enumerate(companies):
    pos[company] = (0, i * 0.1)

# 스킬을 오른쪽에 세로로 배치
for i, skill in enumerate(skills):
    pos[skill] = (2, i * 0.1)
```

### 인사이트
- 기업별 스킬 요구 패턴 비교
- 스킬별 수요 기업 분포 확인
- 전체 네트워크 밀도 파악

---

## 전략 2: Degree 기반 노드 크기 및 위치

### 목적
- 인기 있는 스킬과 많은 스킬을 요구하는 기업을 강조
- 시장 트렌드 파악

### 구현 방법
```python
# Degree 계산
company_degrees = {n: G.degree(n) for n in companies}
skill_degrees = {n: G.degree(n) for n in skills}

# 노드 크기: degree에 비례
company_sizes = [company_degrees[n] * 10 for n in companies]
skill_sizes = [skill_degrees[n] * 10 for n in skills]

# 위치: degree 높은 순으로 정렬
sorted_companies = sorted(companies, key=lambda x: company_degrees[x], reverse=True)
sorted_skills = sorted(skills, key=lambda x: skill_degrees[x], reverse=True)
```

### 인사이트
- **핵심 스킬 식별**: 많은 기업이 요구하는 스킬 (Python, SQL, AWS 등)
- **스킬 집약 기업**: 많은 스킬을 요구하는 기업 (복잡한 역할)
- **시장 표준**: 대부분의 기업이 요구하는 공통 스킬

---

## 전략 3: 커뮤니티 탐지 기반 색상 코딩

### 목적
- 유사한 스킬 조합을 가진 기업 그룹 식별
- 스킬 클러스터 발견 (예: 데이터 분석 스킬 그룹, 인프라 스킬 그룹)

### 구현 방법
```python
import networkx.algorithms.community as nx_comm

# Projection: 기업-기업 네트워크 (공통 스킬 기반)
G_companies = nx.bipartite.weighted_projected_graph(G, companies)

# 커뮤니티 탐지 (Louvain)
communities = nx_comm.louvain_communities(G_companies)

# 각 기업에 커뮤니티 ID 할당
node_community = {}
for i, comm in enumerate(communities):
    for node in comm:
        node_community[node] = i

# 색상 매핑
colors = plt.cm.Set3(np.linspace(0, 1, len(communities)))
node_colors = [colors[node_community.get(n, 0)] for n in companies]
```

### 인사이트
- **직종별 그룹**: 데이터 분석가, 데이터 엔지니어, ML 엔지니어 등
- **기술 스택 유사성**: 비슷한 기술을 사용하는 기업들
- **시장 세그먼트**: 업종별 또는 서비스 유형별 구분

---

## 전략 4: 스킬-스킬 Co-occurrence 히트맵

### 목적
- 어떤 스킬들이 자주 함께 요구되는지 확인
- 스킬 조합 패턴 분석

### 구현 방법
```python
from collections import defaultdict
import numpy as np
import seaborn as sns

# 각 기업의 스킬 리스트
company_skills = defaultdict(list)
for company, skill in G.edges():
    company_skills[company].append(skill)

# Top 스킬 선택 (예: 상위 30개)
top_skills = sorted(skills, key=lambda x: G.degree(x), reverse=True)[:30]

# Co-occurrence 행렬 생성
cooccurrence = np.zeros((len(top_skills), len(top_skills)))
for i, skill1 in enumerate(top_skills):
    for j, skill2 in enumerate(top_skills):
        if i != j:
            # 두 스킬을 모두 요구하는 기업 수
            companies_with_both = sum(1 for comp in companies 
                                    if skill1 in G[comp] and skill2 in G[comp])
            cooccurrence[i][j] = companies_with_both

# 히트맵 시각화
sns.heatmap(cooccurrence, 
            xticklabels=top_skills, 
            yticklabels=top_skills,
            cmap='YlOrRd',
            annot=False)
```

### 인사이트
- **스킬 조합 패턴**: Python + SQL, AWS + Docker 등
- **기술 생태계**: 함께 사용되는 기술 스택
- **학습 경로**: 어떤 스킬을 함께 배워야 하는지

---

## 전략 5: 기업별 스킬 다양성 시각화

### 목적
- 기업별로 요구하는 스킬의 다양성 비교
- 전문성 vs 범용성 분석

### 구현 방법
```python
# 기업별 스킬 개수 및 다양성 지표
company_stats = {}
for company in companies:
    skills_list = list(G[company].keys())
    company_stats[company] = {
        'skill_count': len(skills_list),
        'unique_categories': categorize_skills(skills_list),  # 스킬 카테고리화
        'diversity': calculate_diversity(skills_list)
    }

# 산점도: 스킬 개수 vs 다양성
x = [company_stats[c]['skill_count'] for c in companies]
y = [company_stats[c]['diversity'] for c in companies]
plt.scatter(x, y, alpha=0.5)
```

### 인사이트
- **전문 기업**: 특정 도메인에 집중 (낮은 다양성, 높은 전문성)
- **범용 기업**: 다양한 스킬 요구 (높은 다양성)
- **역할 복잡도**: 많은 스킬을 요구하는 포지션

---

## 전략 6: 시간/트렌드 분석 (가능한 경우)

### 목적
- 스킬 인기도 변화 추이
- 신기술 등장 패턴

### 구현 방법
```python
# 만약 데이터에 시간 정보가 있다면
# 스킬별 등장 빈도 시계열
skill_trends = defaultdict(list)
for year in range(2020, 2025):
    # 해당 연도의 구인공고만 필터링
    year_companies = filter_by_year(companies, year)
    for skill in skills:
        count = sum(1 for comp in year_companies if skill in G[comp])
        skill_trends[skill].append(count)

# 시계열 그래프
for skill in top_skills:
    plt.plot(years, skill_trends[skill], label=skill)
```

### 인사이트
- **성장 스킬**: 점점 더 많이 요구되는 스킬 (AI, LLM 등)
- **쇠퇴 스킬**: 요구가 줄어드는 스킬
- **트렌드 예측**: 향후 인기 스킬 예측

---

## 전략 7: 이분 그래프 Projection (1-mode 변환)

### 목적
- 기업-기업 유사성 네트워크
- 스킬-스킬 공존 네트워크

### 구현 방법
```python
# 기업-기업 네트워크 (공통 스킬 기반)
G_company_company = nx.bipartite.weighted_projected_graph(G, companies)

# 스킬-스킬 네트워크 (같은 기업에서 요구되는 스킬)
G_skill_skill = nx.bipartite.weighted_projected_graph(G, skills)

# 각각 시각화
# 1. 기업 네트워크: 유사한 스킬 요구 패턴을 가진 기업들
# 2. 스킬 네트워크: 함께 요구되는 스킬들
```

### 인사이트
- **경쟁사 분석**: 비슷한 스킬을 요구하는 기업들
- **스킬 클러스터**: 함께 사용되는 스킬 그룹
- **시장 포지셔닝**: 기업 간 유사도

---

## 전략 8: 중심성 기반 핵심 노드 강조

### 목적
- 네트워크에서 중요한 역할을 하는 기업/스킬 식별
- 브로커 역할, 허브 역할 분석

### 구현 방법
```python
# 다양한 중심성 지표 계산
betweenness = nx.betweenness_centrality(G)
closeness = nx.closeness_centrality(G)
eigenvector = nx.eigenvector_centrality(G)

# 노드 크기/색상에 중심성 반영
node_sizes = [betweenness[n] * 10000 for n in G.nodes()]
node_colors = [eigenvector[n] for n in G.nodes()]
```

### 인사이트
- **브로커 스킬**: 다양한 기업에서 요구하는 핵심 스킬
- **전문 스킬**: 특정 기업/도메인에서만 요구
- **네트워크 영향력**: 중심성 높은 노드의 전략적 중요성

---

## 전략 9: 인터랙티브 시각화 (Plotly, Bokeh)

### 목적
- 사용자가 탐색하며 인사이트 발견
- 필터링, 줌, 호버 기능

### 구현 방법
```python
import plotly.graph_objects as go
import plotly.express as px

# Plotly 네트워크 그래프
fig = go.Figure()

# 노드 추가
for node in G.nodes():
    x, y = pos[node]
    fig.add_trace(go.Scatter(
        x=[x], y=[y],
        mode='markers+text',
        text=[node],
        name=node
    ))

# 엣지 추가
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    fig.add_trace(go.Scatter(
        x=[x0, x1], y=[y0, y1],
        mode='lines',
        line=dict(width=0.5, color='gray')
    ))

fig.show()
```

### 인사이트
- **동적 탐색**: 사용자가 관심 있는 부분 집중
- **상호작용**: 클릭, 필터링으로 세부 분석
- **공유 용이**: 웹 기반 시각화

---

## 전략 10: 계층적 클러스터링 + Dendrogram

### 목적
- 스킬/기업의 계층적 그룹화
- 유사성 트리 구조

### 구현 방법
```python
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist, squareform

# 기업 간 거리 행렬 (스킬 벡터 기반)
company_vectors = []
for company in companies:
    vector = [1 if skill in G[company] else 0 for skill in skills]
    company_vectors.append(vector)

distance_matrix = pdist(company_vectors, metric='jaccard')
linkage_matrix = linkage(distance_matrix, method='ward')
dendrogram(linkage_matrix, labels=companies[:50])  # 상위 50개만
```

### 인사이트
- **계층적 그룹**: 유사한 기업들의 중첩된 그룹
- **거리 측정**: 기업 간 스킬 요구 패턴 유사도
- **클러스터 해석**: 각 그룹의 공통 특성

---

## 추천 시각화 조합

### 빠른 인사이트 (Quick Insights)
1. **전략 1 (기본 Bipartite)** + **전략 2 (Degree 기반 크기)**
   - 전체 구조 파악 + 핵심 노드 강조

### 심층 분석 (Deep Analysis)
2. **전략 3 (커뮤니티)** + **전략 4 (Co-occurrence)**
   - 그룹 식별 + 스킬 조합 패턴

### 전략적 분석 (Strategic Analysis)
3. **전략 7 (Projection)** + **전략 8 (중심성)**
   - 경쟁사 분석 + 네트워크 영향력

### 프레젠테이션용
4. **전략 9 (인터랙티브)** + **전략 10 (Dendrogram)**
   - 탐색 가능 + 계층 구조

---

## 구현 우선순위

### Phase 1: 기본 시각화
- [ ] 전략 1: 기본 Bipartite 레이아웃
- [ ] 전략 2: Degree 기반 노드 크기

### Phase 2: 분석 시각화
- [ ] 전략 4: Co-occurrence 히트맵
- [ ] 전략 7: Projection 네트워크

### Phase 3: 고급 시각화
- [ ] 전략 3: 커뮤니티 탐지
- [ ] 전략 8: 중심성 분석
- [ ] 전략 9: 인터랙티브 시각화

---

## 도구 및 라이브러리

### Python
- **NetworkX**: 네트워크 분석 및 기본 시각화
- **Matplotlib**: 정적 시각화
- **Plotly/Bokeh**: 인터랙티브 시각화
- **Seaborn**: 히트맵, 통계 시각화
- **Gephi**: 대규모 네트워크 시각화 (데스크톱)

### 웹 기반
- **D3.js**: 커스텀 인터랙티브 시각화
- **Cytoscape.js**: 네트워크 시각화 라이브러리
- **vis.js**: 네트워크 그래프

### 전문 도구
- **Gephi**: 대규모 네트워크 분석 및 시각화
- **Pajek**: 네트워크 분석 (이미 사용 중)
- **Cytoscape**: 생물정보학 네트워크 (일반 네트워크에도 사용 가능)

---

## 참고사항

1. **성능**: 1,034개 노드는 시각화에 부담이 될 수 있음
   - 필터링: 상위 N개 노드만 표시
   - 샘플링: 랜덤 샘플 또는 중요 노드만

2. **가독성**: 
   - 레이블: 상위 노드만 표시
   - 엣지: 투명도 조정 또는 가중치 기반 필터링
   - 색상: 명확한 대비

3. **인사이트 도출**:
   - 질문 먼저 정의: "어떤 스킬이 가장 인기 있는가?"
   - 시각화로 답변: Degree 기반 시각화
   - 검증: 통계적 분석과 비교



