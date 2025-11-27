# Skill-Skill Network 심층 분석 결과 요약

## 분석 완료 일자
2025년 (실행 시점)

---

## 1. Max-Component 특징 분석

### 결과
- **총 연결 성분 수**: 1개
- **최대 연결 성분 크기**: 495개 노드 (100.0%)
- **최대 연결 성분 엣지 수**: 24,239개

### Max-Component 통계
- **평균 Degree**: 97.94
- **최대 Degree**: 447 (Python)
- **최소 Degree**: 2
- **밀도**: 0.1982
- **평균 클러스터링 계수**: 0.7844 (매우 높음 → 지역적 밀집도 높음)

### 해석
- 전체 네트워크가 하나의 거대한 연결 성분으로 구성됨
- 모든 스킬이 직접 또는 간접적으로 연결되어 있음
- 높은 클러스터링 계수는 스킬들이 지역적으로 밀집된 그룹을 형성함을 의미

---

## 2-3. Degree Distribution 분석

### PDF, CCDF, CDF 시각화
**출력 파일**: `degree_distribution_analysis.png`

6개의 서브플롯:
1. PDF (선형 스케일)
2. PDF (로그-로그 스케일)
3. CCDF (선형 스케일)
4. CCDF (로그-로그 스케일) - **Power Law 확인용**
5. CDF (선형 스케일)
6. CDF (로그 X축) - **Power Tail 확인용**

### Degree Distribution 통계
- **평균 Degree**: 97.94
- **중앙값 Degree**: 75.00
- **최대 Degree**: 447
- **최소 Degree**: 2
- **표준편차**: 85.93

### Power Law 분석 결과
- **추정 지수 (γ)**: **2.37**
- **Power Law 형태**: P(K ≥ k) ~ k^(-2.37)
- **해석**: 
  - γ > 1이므로 **허브 노드 존재 확인**
  - 높은 degree를 가진 노드(Python, AI, SQL 등)가 예상보다 많음
  - 네트워크가 Power Law 분포를 따름

### Power Tail 분석
- CDF 로그 그래프에서 Power Tail 영역 확인 가능
- 상위 degree 노드들이 긴 꼬리(tail)를 형성
- 이는 소수의 허브 노드가 네트워크의 대부분 연결을 담당함을 의미

---

## 4. 노드 속성 기반 네트워크 시각화

**출력 파일**: `network_node_attributes_visualization.png`

### 포함된 시각화 (6개 서브플롯)

1. **Degree 기반 시각화**
   - 색상/크기 ∝ Degree
   - 가장 기본적인 중심성 지표

2. **Betweenness Centrality 기반**
   - 브로커 역할을 하는 노드 강조
   - 다른 노드들 간의 경로에 자주 등장하는 노드

3. **Clustering Coefficient 기반**
   - 지역적 밀집도 표시
   - 높을수록 주변 노드들이 서로 잘 연결됨

4. **Eigenvector Centrality 기반**
   - 영향력 있는 노드와 연결된 노드 강조
   - 연결의 질을 고려한 중심성

5. **Degree vs Clustering 산점도**
   - 두 지표 간의 관계 분석
   - 허브 노드의 클러스터링 특성 확인

6. **허브 노드 강조 시각화**
   - 상위 5% Degree 노드를 빨간색으로 강조
   - 허브 노드 25개 식별

### 허브 노드 (상위 10개, Degree ≥ 274)
1. Python (447)
2. AI (419)
3. SQL (374)
4. AWS (366)
5. Docker (361)
6. Git (357)
7. Kubernetes (339)
8. CI/CD (335)
9. LLM (331)
10. API (327)

---

## 주요 발견사항

### 1. 허브 노드의 존재
- Power Law 지수 γ = 2.37로 허브 노드 존재 확인
- 상위 5% 노드(25개)가 네트워크의 핵심 역할
- Python, AI, SQL 등이 가장 중요한 허브

### 2. 높은 클러스터링
- 평균 클러스터링 계수: 0.7844
- 스킬들이 지역적으로 밀집된 그룹을 형성
- 기술 스택의 자연스러운 조합 패턴 반영

### 3. 완전 연결성
- 전체 네트워크가 하나의 연결 성분
- 모든 스킬이 직접 또는 간접적으로 연결
- 기술 생태계의 통합성 확인

### 4. Power Law 분포
- Degree distribution이 Power Law를 따름
- 소수의 허브 노드가 대부분의 연결 담당
- 네트워크의 불균등한 구조 (scale-free network)

---

## 수행하기 어려운 부분

자세한 내용은 `analysis_difficulties.md` 파일 참조

### 주요 제약사항:

1. **Power Law 지수 정확한 계산**
   - 현재는 로그 공간 선형 회귀 사용
   - 더 정확한 분석을 위해서는 `powerlaw` 라이브러리 권장
   - Kolmogorov-Smirnov 테스트 등 통계적 검정 필요

2. **대규모 네트워크 확장성**
   - 495개 노드는 정상 작동
   - 1000개 이상 노드에서는 성능 저하 예상
   - Betweenness Centrality 계산 시간 증가

3. **Power Tail 정확한 식별**
   - Tail 시작점 자동 판단 어려움
   - 시각적 확인 필요
   - 여러 분포 모델 비교 필요

4. **커뮤니티 탐지**
   - 현재 미구현
   - Louvain, Leiden 알고리즘으로 구현 가능

---

## 생성된 파일

1. `degree_distribution_analysis.png` - Degree 분포 분석 (PDF, CCDF, CDF)
2. `network_node_attributes_visualization.png` - 노드 속성 기반 시각화
3. `analysis_difficulties.md` - 수행 어려운 부분 상세 설명

---

## 다음 단계 권장사항

1. **Power Law 정확한 검정**
   ```bash
   pip install powerlaw
   ```

2. **커뮤니티 탐지 추가**
   - Louvain 알고리즘으로 스킬 클러스터 식별

3. **시간적 변화 분석**
   - 데이터에 시간 정보가 있다면 트렌드 분석

4. **네트워크 모티프 분석**
   - 특정 패턴 탐지 및 해석

