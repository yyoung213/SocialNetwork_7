# Skill-Skill Network 분석 수행 어려운 부분

## 수행 완료된 분석

### ✅ 1. Max-Component 특징
- **상태**: 완료
- **결과**: 
  - 전체 네트워크가 하나의 연결 성분 (100% 연결)
  - 평균 클러스터링 계수: 0.7844 (높은 지역적 밀집도)
  - 밀도: 0.1982

### ✅ 2. PDF와 CCDF 시각화
- **상태**: 완료
- **결과 파일**: `degree_distribution_analysis.png`
- **포함 내용**:
  - PDF (선형/로그 스케일)
  - CCDF (선형/로그 스케일)
  - CDF (선형/로그 스케일)

### ✅ 3. Degree Distribution 계산
- **상태**: 완료
- **통계**:
  - 평균 Degree: 97.94
  - 중앙값: 75.00
  - 최대: 447 (Python)
  - 표준편차: 85.93

### ✅ 4. Power Law 분석 (CDF Power Tail)
- **상태**: 부분 완료
- **문제점**: 
  - Power Law 지수 계산이 불안정할 수 있음
  - CCDF 로그 그래프에서 수동 확인 필요
- **해결 방법**: 
  - CCDF 로그 그래프에서 직선 부분 확인
  - 상위 degree 노드 비율로 허브 존재 판단

### ✅ 5. 노드 속성 기반 시각화
- **상태**: 완료
- **결과 파일**: `network_node_attributes_visualization.png`
- **포함 내용**:
  - Degree 기반 시각화
  - Betweenness Centrality
  - Clustering Coefficient
  - Eigenvector Centrality
  - Degree vs Clustering 산점도
  - 허브 노드 강조

---

## 수행하기 어려운 부분 및 제약사항

### 1. Power Law 지수 정확한 계산
**문제점:**
- Power Law 피팅이 데이터에 따라 불안정할 수 있음
- 로그 공간에서 선형 회귀 시 이상치 영향
- CCDF의 tail 부분만 사용해야 하는데, 어디서부터 tail인지 판단이 주관적

**대안:**
- CCDF 로그 그래프에서 시각적으로 직선 부분 확인
- Kolmogorov-Smirnov 테스트 등 통계적 검정 필요 (추가 라이브러리 필요)
- `powerlaw` 라이브러리 사용 권장 (별도 설치 필요)

**권장 방법:**
```python
# powerlaw 라이브러리 사용 (설치 필요: pip install powerlaw)
import powerlaw
fit = powerlaw.Fit(degree_values)
gamma = fit.power_law.alpha
```

---

### 2. 대규모 네트워크 시각화 성능
**문제점:**
- 495개 노드, 24,239개 엣지는 시각화에 부담
- Spring layout 계산 시간이 오래 걸림 (현재 300 iterations)
- 모든 노드 레이블 표시 시 가독성 저하

**현재 해결책:**
- 상위 노드만 레이블 표시
- 서브그래프 사용 (필요시)
- 레이아웃 계산 시간 단축 (iterations 조정)

**추가 개선 가능:**
- ForceAtlas2 레이아웃 사용 (더 빠름, 별도 라이브러리 필요)
- 인터랙티브 시각화 (Plotly, Bokeh) - 탐색 용이

---

### 3. 노드 속성 계산 시간
**문제점:**
- Betweenness Centrality: O(V*E) 시간 복잡도 → 큰 네트워크에서 느림
- Eigenvector Centrality: 반복 계산 필요, 수렴 보장 어려움
- 495개 노드에서는 가능하지만, 더 큰 네트워크에서는 문제

**현재 상태:**
- ✅ 495개 노드에서는 정상 작동
- ⚠️ 1000개 이상 노드에서는 시간이 매우 오래 걸릴 수 있음

**대안:**
- 샘플링: 랜덤 샘플 또는 상위 노드만 분석
- 근사 알고리즘 사용
- 병렬 처리

---

### 4. Power Tail 정확한 식별
**문제점:**
- Power Tail의 시작점을 자동으로 판단하기 어려움
- 데이터에 따라 tail이 명확하지 않을 수 있음
- 지수 분포, 로그 정규 분포 등과 구분 필요

**현재 해결책:**
- 시각적 확인: CDF 로그 그래프에서 tail 영역 강조
- 상위 5% 노드를 허브로 정의

**추가 분석 필요:**
- 여러 분포 모델 비교 (Power Law, Exponential, Log-normal)
- Goodness-of-fit 테스트
- AIC/BIC를 통한 모델 선택

---

### 5. 네트워크 커뮤니티 탐지
**문제점:**
- Zachary's Karate Club처럼 명확한 커뮤니티 구조가 없을 수 있음
- 스킬 네트워크는 기술 스택 기반이라 연속적인 구조일 가능성

**현재 미구현:**
- 커뮤니티 탐지 알고리즘 (Louvain, Leiden 등)
- 모듈성 최적화

**구현 가능:**
```python
import networkx.algorithms.community as nx_comm
communities = nx_comm.louvain_communities(G)
```

---

### 6. 시간 복잡도가 높은 분석
**제약사항:**
- **Betweenness Centrality**: O(V*E) - 현재 네트워크에서 약간 느림
- **All-pairs shortest path**: O(V²) - 매우 느림
- **Exact triangle counting**: O(V³) - 비현실적

**현재 상태:**
- ✅ 기본 중심성 지표: 정상 작동
- ⚠️ 대규모 네트워크 확장 시 성능 문제 예상

---

## 권장 추가 분석

### 1. Power Law 정확한 검정
```python
# powerlaw 라이브러리 설치 필요
pip install powerlaw

import powerlaw
fit = powerlaw.Fit(degree_values)
# Power Law vs Exponential 비교
R, p = fit.distribution_compare('power_law', 'exponential')
```

### 2. 커뮤니티 탐지
```python
import networkx.algorithms.community as nx_comm
communities = nx_comm.louvain_communities(G)
# 또는
communities = nx_comm.greedy_modularity_communities(G)
```

### 3. 네트워크 모티프 분석
- 3-node, 4-node 모티프 카운팅
- 특정 패턴 탐지

### 4. 시간적 변화 분석
- 현재 데이터는 스냅샷
- 시간 정보가 있다면 트렌드 분석 가능

---

## 현재 분석 결과 요약

### ✅ 성공적으로 수행된 분석:
1. Max-Component: 전체 네트워크가 하나의 연결 성분
2. PDF/CCDF/CDF 시각화 완료
3. Degree Distribution 통계 계산
4. Power Tail 시각적 확인 (CDF 로그 그래프)
5. 허브 노드 식별 (상위 5%, Degree ≥ 274)
6. 노드 속성 기반 시각화 (4가지 중심성 지표)

### ⚠️ 제한사항:
1. Power Law 지수 계산이 수치적으로 불안정할 수 있음
2. 대규모 네트워크 확장 시 성능 문제
3. 정확한 Power Law 검정을 위해서는 추가 라이브러리 필요

### 📊 주요 발견:
- **허브 노드 존재 확인**: Python, AI, SQL 등이 매우 높은 degree
- **높은 클러스터링**: 평균 0.7844 → 스킬들이 지역적으로 밀집
- **Power Law 특성**: CCDF 로그 그래프에서 확인 가능



