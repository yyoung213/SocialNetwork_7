# 작업 내역 종합 정리

## 작업 기간
2025년 11월 16일 ~ 11월 17일

---

## 전체 작업 흐름

```
1. 원본 데이터 수집 (직종별 CSV 파일)
   ↓
2. Bipartite 네트워크 구축 (기업-스킬)
   ↓
3. Skill-Skill 네트워크 구축 (스킬 간 co-occurrence)
   ↓
4. Bipartite 네트워크 시각화 (4가지 전략)
   ↓
5. Skill-Skill 네트워크 시각화
   ↓
6. Skill-Skill 네트워크 심층 분석
   ↓
7. 분석 결과 문서화
```

---

## 1단계: 데이터 준비 및 전처리

### 1-1. 원본 데이터
**파일**: 직종별 CSV 파일들
- `BI 엔지니어.csv`
- `DBA.csv`
- `데이터 분석가.csv`
- `데이터 사이언티스트.csv`
- `데이터 엔지니어.csv`
- `머신러닝 엔지니어.csv`
- `빅데이터 엔지니어.csv`
- `프로덕트 매니저.csv`

**내용**: 각 파일은 구인공고 데이터로, 기업명과 요구 스킬 정보 포함

### 1-2. Bipartite 네트워크 데이터 생성
**작업**: 직종별 CSV 파일들을 통합하여 기업-스킬 관계 데이터 생성

**출력 파일**: 
- `data_bipartite_skill_edges.csv` (2025-11-16 23:49:42)
  - 형식: `기업명,Skill` (Long format)
  - 총 6,917개 행 (기업-스킬 쌍)

**내용**: 
- 각 행은 한 기업이 요구하는 하나의 스킬을 나타냄
- 예: `우아한형제들(배달의민족),SQL`

---

## 2단계: Bipartite 네트워크 구축

### 2-1. Pajek 형식 변환
**스크립트**: `convert_to_pajek.py` (2025-11-16 23:54:53)

**작업 내용**:
- `data_bipartite_skill_edges.csv`를 Pajek 2-mode 네트워크 형식으로 변환
- 기업 노드와 스킬 노드를 분리하여 표현

**출력 파일**: 
- `data_bipartite_skill_2mode.net` (2025-11-16 23:54:45)
  - 형식: Pajek 2-mode 네트워크
  - 총 노드: 1,034개 (기업 539개 + 스킬 495개)
  - 총 엣지: 6,915개

**파일 구조**:
```
*Vertices 1034 539
  1 "우아한형제들(배달의민족)" ...
  ...
  540 "SQL" ...
  ...
*Edges
  1 540 1
  ...
```

---

## 3단계: Skill-Skill 네트워크 구축

### 3-1. Co-occurrence 계산 및 네트워크 생성
**스크립트**: `build_skill_skill_network.py` (2025-11-17 00:09:00)

**작업 내용**:
1. `data_bipartite_skill_edges.csv` 로드
2. 기업별 스킬 리스트 추출
3. 같은 기업에서 함께 등장하는 스킬 쌍의 co-occurrence 계산
4. Skill-Skill 네트워크 구축 (가중치 = co-occurrence 빈도)
5. Pajek `.net` 형식으로 저장

**출력 파일**: 
- `skill_skill_network.net` (2025-11-17 00:08:45)
  - 노드: 495개 스킬
  - 엣지: 24,239개 (가중치 포함)
  - 형식: Pajek 1-mode 네트워크

**네트워크 특성**:
- 노드: 각 스킬
- 엣지: 두 스킬이 같은 구인공고에 함께 등장
- 가중치: 함께 등장한 구인공고 수

---

## 4단계: Skill-Skill 네트워크 시각화

### 4-1. 기본 시각화
**스크립트**: `visualize_skill_network.py` (2025-11-17 00:20:17)

**작업 내용**:
- `skill_skill_network.net` 파일 읽기
- Degree 기반 노드 크기 설정
- Spring layout으로 노드 배치
- 가독성 향상을 위한 간격 조정

**출력 파일**: 
- `skill_skill_network_visualization.png` (2025-11-17 00:18:31)
  - 크기: 약 13.8MB
  - 특징: Degree에 비례한 노드 크기, 가독성 좋은 레이아웃

---

## 5단계: Bipartite 네트워크 시각화 전략 수립 및 실행

### 5-1. 시각화 전략 문서화
**파일**: `bipartite_network_visualization_strategies.md` (2025-11-17 00:30:40)

**내용**: 
- 10가지 시각화 전략 제안
- 각 전략의 목적과 방법 설명
- 인사이트 도출 방법

### 5-2. 시각화 스크립트 개발
**스크립트**: `visualize_bipartite_network.py` (2025-11-17 01:37:11)

**주요 함수**:
- `read_2mode_network()`: Pajek 2-mode 네트워크 파싱
- `strategy1_basic_bipartite()`: 기본 Bipartite 레이아웃
- `strategy2_degree_based()`: Degree 기반 시각화
- `strategy4_cooccurrence_heatmap()`: Co-occurrence 히트맵
- `strategy7_projection()`: Projection 네트워크

### 5-3. 전략별 실행

#### 전략 1: 기본 Bipartite 레이아웃
**스크립트**: `run_strategy1.py`, `fix_strategy1.py` (2025-11-17 00:43:27)

**작업 내용**:
- 초기 파싱 문제 해결 (NetworkX의 `read_pajek` 한계)
- 수동 파싱 로직 구현
- 기업(왼쪽) ↔ 스킬(오른쪽) 양쪽 정렬 레이아웃
- 상위 50개 기업, 상위 50개 스킬만 표시

**출력 파일**: 
- `bipartite_basic_improved.png` (2025-11-17 00:40:28)

**주요 개선사항**:
- Pajek 2-mode 형식 정확한 파싱
- 노드 ID 기반으로 기업/스킬 구분
- 한글 폰트 지원

#### 전략 2: Degree 기반 노드 크기 및 위치
**스크립트**: `run_strategy2.py` (2025-11-17 00:54:54)

**작업 내용**:
- Degree에 비례한 노드 크기
- Bipartite 레이아웃 유지
- 상위 노드 레이블 표시

**출력 파일**: 
- `bipartite_degree.png` (2025-11-17 00:54:45)

**주요 인사이트**:
- 상위 기업: 현대오토에버(68개 스킬), 우아한형제들(67개)
- 상위 스킬: Python(315개 기업), AI(286개), SQL(161개)

#### 전략 4: 스킬-스킬 Co-occurrence 히트맵
**스크립트**: `run_strategy4.py` (2025-11-17 00:58:27)

**작업 내용**:
- 상위 30개 스킬 선택
- 스킬 쌍의 co-occurrence 행렬 계산
- Seaborn 히트맵 시각화

**출력 파일**: 
- `cooccurrence_heatmap.png` (2025-11-17 00:58:19)

**주요 인사이트**:
- Python-AI: 189개 기업에서 함께 요구
- AI-LLM: 126개 기업
- Python-AWS: 117개 기업

#### 전략 7: Projection 네트워크
**스크립트**: `run_strategy7.py` (2025-11-17 01:14:00)

**작업 내용**:
- 기업-기업 네트워크: 공통 스킬 기반
- 스킬-스킬 네트워크: 같은 기업에서 요구
- Spring layout으로 시각화
- 노드 간 거리 조정 (k 값 증가)

**출력 파일**: 
- `projection_networks.png` (2025-11-17 01:36:59)

**주요 개선사항**:
- 노드 간 거리 증가 (k=23.22, k=22.25)
- 가독성 향상 (겹침 감소)
- 엣지 두께 및 투명도 조정

---

## 6단계: Skill-Skill 네트워크 심층 분석

### 6-1. 분석 스크립트 개발
**스크립트**: `analyze_skill_network.py` (2025-11-17 02:06:50)

**분석 항목**:
1. **Max-Component 특징 분석**
   - 연결 성분 탐지
   - 최대 연결 성분 통계
   - 밀도, 클러스터링 계수 계산

2. **Degree Distribution 분석**
   - PDF (Probability Density Function)
   - CDF (Cumulative Distribution Function)
   - CCDF (Complementary CDF)
   - Power Law 피팅

3. **Power Tail 분석**
   - 허브 노드 식별 (상위 5%)
   - Power Tail 영역 시각화

4. **노드 속성 기반 시각화**
   - Degree Centrality
   - Betweenness Centrality
   - Closeness Centrality
   - Eigenvector Centrality
   - Clustering Coefficient
   - 허브 노드 강조

### 6-2. 분석 결과

**출력 파일**:
- `degree_distribution_analysis.png` (2025-11-17 01:55:53)
  - 6개 서브플롯: PDF, CCDF, CDF (선형/로그 스케일)
- `network_node_attributes_visualization.png` (2025-11-17 01:56:35)
  - 6개 서브플롯: 다양한 중심성 지표 기반 시각화

**주요 발견**:
- **Max-Component**: 전체 네트워크가 하나의 연결 성분 (100%)
- **Power Law 지수**: γ = 2.37 (허브 노드 존재 확인)
- **클러스터링 계수**: 0.7844 (매우 높음)
- **허브 노드**: Python(447), AI(419), SQL(374) 등

---

## 7단계: 분석 결과 문서화

### 7-1. 분석 결과 요약
**파일**: `analysis_summary.md` (2025-11-17 02:06:50)

**내용**:
- 각 분석 항목별 결과 요약
- 주요 발견사항
- 생성된 파일 목록

### 7-2. 분석 어려운 부분 정리
**파일**: `analysis_difficulties.md` (2025-11-17 02:06:50)

**내용**:
- Power Law 지수 정확한 계산의 한계
- 대규모 네트워크 확장성 문제
- Power Tail 정확한 식별의 어려움
- 권장 추가 분석 방법

### 7-3. 분석 절차 및 결과 해석
**파일**: `analysis_procedure_and_interpretation.md` (2025-11-17 02:11:20)

**내용**:
- 상세한 분석 절차 설명
- 각 단계별 목적과 방법
- 결과 해석 (구조적/기능적/역동적 관점)
- 인사이트 및 시사점
- 실무적 활용 방안

---

## 최종 산출물

### 데이터 파일
1. `data_bipartite_skill_edges.csv` - 기업-스킬 관계 (Long format)
2. `data_bipartite_skill_2mode.net` - Bipartite 네트워크 (Pajek 형식)
3. `skill_skill_network.net` - Skill-Skill 네트워크 (Pajek 형식)

### 시각화 파일
1. `skill_skill_network_visualization.png` - Skill-Skill 네트워크 기본 시각화
2. `bipartite_basic_improved.png` - Bipartite 기본 레이아웃
3. `bipartite_degree.png` - Degree 기반 시각화
4. `cooccurrence_heatmap.png` - 스킬 Co-occurrence 히트맵
5. `projection_networks.png` - Projection 네트워크
6. `degree_distribution_analysis.png` - Degree 분포 분석
7. `network_node_attributes_visualization.png` - 노드 속성 시각화

### 분석 스크립트
1. `build_skill_skill_network.py` - Skill-Skill 네트워크 구축
2. `convert_to_pajek.py` - Pajek 형식 변환
3. `visualize_skill_network.py` - Skill-Skill 네트워크 시각화
4. `visualize_bipartite_network.py` - Bipartite 네트워크 시각화
5. `analyze_skill_network.py` - Skill-Skill 네트워크 심층 분석
6. `run_strategy1.py`, `run_strategy2.py`, `run_strategy4.py`, `run_strategy7.py` - 전략별 실행 스크립트

### 문서 파일
1. `bipartite_network_visualization_strategies.md` - 시각화 전략 가이드
2. `analysis_summary.md` - 분석 결과 요약
3. `analysis_difficulties.md` - 분석 제약사항 및 해결방안
4. `analysis_procedure_and_interpretation.md` - 분석 절차 및 해석 상세 문서

---

## 주요 성과

### 1. 네트워크 구축
- ✅ Bipartite 네트워크: 539개 기업 × 495개 스킬, 6,915개 엣지
- ✅ Skill-Skill 네트워크: 495개 스킬, 24,239개 엣지

### 2. 시각화
- ✅ 7가지 시각화 생성
- ✅ 다양한 관점에서 네트워크 구조 파악
- ✅ 가독성 높은 레이아웃 구현

### 3. 심층 분석
- ✅ Max-Component 분석: 완전 연결성 확인
- ✅ Power Law 분석: γ = 2.37, 허브 노드 존재 확인
- ✅ 중심성 지표 분석: 5가지 지표 계산 및 시각화
- ✅ 클러스터링 분석: 높은 지역적 밀집도 확인

### 4. 문서화
- ✅ 상세한 분석 절차 문서화
- ✅ 결과 해석 및 인사이트 정리
- ✅ 실무적 활용 방안 제시

---

## 기술적 도전과 해결

### 1. Pajek 2-mode 네트워크 파싱
**문제**: NetworkX의 `read_pajek`가 2-mode 네트워크를 제대로 파싱하지 못함

**해결**: 
- 수동 파싱 로직 구현
- 노드 ID 기반으로 기업/스킬 구분
- 엣지 가중치 정확히 읽기

### 2. Power Law 피팅
**문제**: 수치적으로 불안정할 수 있음

**해결**: 
- Tail 부분만 사용
- 로그 공간에서 선형 회귀
- 예외 처리 추가

### 3. 대규모 네트워크 시각화
**문제**: 495개 노드, 24,239개 엣지의 가독성

**해결**: 
- 상위 노드만 표시
- 레이아웃 파라미터 조정 (k 값 증가)
- 엣지 투명도 조정

---

## 주요 인사이트

### 1. 네트워크 구조
- **Scale-Free Network**: Power Law 분포 (γ = 2.37)
- **Small-World**: 완전 연결성 + 높은 클러스터링 (0.7844)
- **허브 노드**: Python, AI, SQL이 핵심

### 2. 기술 생태계
- **통합된 생태계**: 모든 스킬이 연결되어 있음
- **기술 조합 패턴**: 도메인별 표준 스킬 조합 존재
- **학습 경로**: 허브 스킬 중심 학습이 효율적

### 3. 시장 트렌드
- **핵심 스킬**: Python, AI, SQL이 압도적
- **최신 트렌드**: AI, LLM이 높은 연결성
- **인프라 스킬**: AWS, Docker, Kubernetes가 필수

---

## 향후 개선 가능한 부분

### 1. Power Law 정확한 검정
- `powerlaw` 라이브러리 사용
- Kolmogorov-Smirnov 테스트
- 여러 분포 모델 비교

### 2. 커뮤니티 탐지
- Louvain 알고리즘
- Leiden 알고리즘
- 모듈성 최적화

### 3. 시간적 변화 분석
- 시계열 데이터 수집
- 트렌드 분석
- 네트워크 진화 패턴

### 4. 인터랙티브 시각화
- Plotly, Bokeh 활용
- 노드 클릭 시 상세 정보
- 필터링 기능

---

## 작업 통계

### 파일 수
- Python 스크립트: 10개
- Markdown 문서: 4개
- 네트워크 파일: 3개
- 시각화 이미지: 7개
- CSV 데이터: 9개

### 코드 라인 수 (추정)
- `analyze_skill_network.py`: ~487줄
- `visualize_bipartite_network.py`: ~550줄
- `visualize_skill_network.py`: ~301줄
- `build_skill_skill_network.py`: ~166줄
- 기타 스크립트: ~100줄

**총 코드**: 약 1,600줄 이상

### 문서 분량
- `analysis_procedure_and_interpretation.md`: ~24,507자
- `bipartite_network_visualization_strategies.md`: ~12,403자
- 기타 문서: ~12,000자

**총 문서**: 약 49,000자 이상

---

## 작업 시간대

- **2025-11-16 17:26**: 원본 데이터 준비 (직종별 CSV)
- **2025-11-16 23:49**: Bipartite 데이터 생성
- **2025-11-16 23:54**: Pajek 변환 및 Bipartite 네트워크 구축
- **2025-11-17 00:08**: Skill-Skill 네트워크 구축
- **2025-11-17 00:18**: Skill-Skill 네트워크 시각화
- **2025-11-17 00:30**: 시각화 전략 문서화
- **2025-11-17 00:40~01:36**: Bipartite 네트워크 시각화 (전략 1, 2, 4, 7)
- **2025-11-17 01:55~02:06**: Skill-Skill 네트워크 심층 분석
- **2025-11-17 02:11**: 분석 결과 문서화 완료

**총 작업 시간**: 약 9시간 (2025-11-16 17:26 ~ 2025-11-17 02:11)

---

## 결론

이번 작업을 통해:
1. ✅ 구인공고 데이터로부터 네트워크 구축
2. ✅ 다양한 시각화 전략 구현
3. ✅ 네트워크 이론 기반 심층 분석
4. ✅ 상세한 문서화 및 해석

**최종 목표 달성**: Skill-Skill 네트워크와 Bipartite 네트워크의 구조적 특성을 파악하고, 실무적 인사이트를 도출하는 완전한 분석 파이프라인 구축 완료



