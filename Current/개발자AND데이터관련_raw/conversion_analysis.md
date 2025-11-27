# Bipartite Skill Edges → Skill-Skill Network 변환 로직 분석

## 📋 변환 로직 분석

### 원본 스크립트 위치
- **파일**: `Current/데이터관련_raw/build_skill_skill_network.py`
- **목적**: `data_bipartite_skill_edges.csv` → `skill_skill_network.net` 변환

---

## 🔍 변환 프로세스 상세 분석

### 1단계: 데이터 로딩 (`load_skill_edges`)

**입력**: CSV 파일 (형식: `기업명,Skill`)

**처리 과정**:
```python
1. CSV 파일을 pandas로 읽기 (encoding='utf-8-sig')
2. 각 행을 순회하며:
   - 기업명과 스킬 추출
   - defaultdict(set)을 사용하여 기업별 스킬 집합 구성
   - 중복 제거: 같은 기업에서 같은 스킬이 여러 번 나와도 set으로 자동 제거
3. set을 정렬된 list로 변환
```

**출력**: `{기업명: [skill1, skill2, ...]}` 형태의 딕셔너리

**핵심 특징**:
- `defaultdict(set)` 사용으로 중복 스킬 자동 제거
- 각 기업별로 고유한 스킬 리스트 생성
- 정렬된 리스트로 반환하여 일관성 유지

---

### 2단계: Co-occurrence 계산 (`calculate_cooccurrence`)

**입력**: `{기업명: [skill1, skill2, ...]}` 딕셔너리

**처리 과정**:
```python
1. Counter 객체 생성
2. 각 기업의 스킬 리스트에 대해:
   - itertools.combinations를 사용하여 모든 스킬 쌍 생성
   - 정렬된 쌍으로 저장 (무방향 그래프)
   - 같은 쌍이 다른 기업에서도 등장하면 카운트 증가
3. Counter에 저장: {(skill1, skill2): count}
```

**출력**: `Counter({(skill1, skill2): count, ...})`

**핵심 특징**:
- **조합(Combinations) 사용**: 같은 기업 내에서 등장한 모든 스킬 쌍 생성
  - 예: [Python, SQL, AWS] → (Python, SQL), (Python, AWS), (SQL, AWS)
- **정렬된 쌍**: 무방향 그래프이므로 (A, B)와 (B, A)를 동일하게 처리
- **가중치 = co-occurrence 빈도**: 두 스킬이 함께 등장한 기업 수

**수학적 의미**:
- 각 기업에서 n개의 스킬이 있으면, nC2 = n(n-1)/2개의 스킬 쌍 생성
- 여러 기업에서 같은 스킬 쌍이 등장하면 가중치가 증가

---

### 3단계: 네트워크 구축 및 저장 (`build_network_and_save`)

**입력**: `Counter({(skill1, skill2): count})`

**처리 과정**:
```python
1. 모든 고유 스킬 추출
   - co-occurrence 딕셔너리에서 모든 스킬 수집
   - set으로 중복 제거 후 정렬

2. 노드 ID 매핑 생성
   - 정렬된 스킬 리스트에 대해 1부터 시작하는 ID 할당
   - {skill: node_id} 형태의 딕셔너리

3. Pajek .net 형식으로 저장
   a. *Vertices 섹션
      - 노드 수 헤더 작성
      - 각 노드에 대해: node_id "skill_name" 형식
      - 따옴표 이스케이프 처리
   
   b. *Edges 섹션
      - *Edges 헤더 작성
      - 각 엣지에 대해: node_id1 node_id2 weight 형식
      - 정렬된 순서로 저장
```

**출력**: Pajek `.net` 파일

**Pajek 형식 구조**:
```
*Vertices N
1 "Skill1"
2 "Skill2"
...
*Edges
1 2 5
1 3 3
...
```

**핵심 특징**:
- **정렬된 스킬 리스트**: 일관된 노드 ID 할당
- **가중치 포함**: 엣지에 co-occurrence 빈도 저장
- **따옴표 이스케이프**: 스킬명에 따옴표가 있어도 처리 가능

---

## 📊 변환 결과 비교

### 데이터관련 네트워크
- **입력**: `data_bipartite_skill_edges.csv` (6,917개 행)
- **출력**: `skill_skill_network.net`
  - 노드 수: 495개
  - 엣지 수: 24,239개
  - 최대 가중치: (확인 필요)

### 개발자+데이터 통합 네트워크
- **입력**: `data&developer_bipartite_skill_edges.csv` (20,124개 행)
- **출력**: `skill_skill_network.net`
  - 노드 수: **728개** (495개보다 233개 더 많음)
  - 엣지 수: **71,178개** (24,239개보다 2.9배 많음)
  - 평균 가중치: 4.39
  - 최소 가중치: 1
  - 최대 가중치: **299** (가장 자주 함께 등장하는 스킬 쌍)

---

## 🔑 핵심 알고리즘 요약

### 1. Bipartite → One-mode Projection
```
기업-스킬 Bipartite 네트워크
  ↓
같은 기업에서 등장한 스킬 쌍 추출
  ↓
스킬-스킬 One-mode 네트워크
```

### 2. Co-occurrence 계산
- **방법**: 각 기업 내 스킬 조합(combinations) 생성
- **가중치**: 두 스킬이 함께 등장한 기업 수
- **특징**: 무방향 그래프 (정렬된 쌍 사용)

### 3. 네트워크 저장
- **형식**: Pajek .net (표준 네트워크 분석 형식)
- **구조**: 
  - Vertices: 노드 정의
  - Edges: 엣지 정의 (가중치 포함)

---

## 💡 로직의 핵심 포인트

### 1. 중복 처리
- **기업별 스킬**: `set` 사용으로 자동 중복 제거
- **스킬 쌍**: 정렬된 쌍으로 (A, B)와 (B, A) 동일 처리

### 2. 가중치 의미
- **가중치 = co-occurrence 빈도**: 두 스킬이 함께 등장한 기업 수
- **높은 가중치**: 해당 스킬 쌍이 많은 기업에서 함께 요구됨
- **낮은 가중치**: 해당 스킬 쌍이 적은 기업에서만 함께 요구됨

### 3. 확장성
- **대용량 데이터 처리**: Counter와 set 사용으로 메모리 효율적
- **임의의 스킬 수**: 동적으로 노드 ID 할당

---

## ✅ 변환 완료 확인

### 개발자+데이터 통합 네트워크
- ✅ 파일 생성: `skill_skill_network.net`
- ✅ 노드 수: 728개
- ✅ 엣지 수: 71,178개
- ✅ 최대 가중치: 299 (가장 강한 연결)

### 통계 요약
- **입력 데이터**: 20,124개 기업-스킬 쌍
- **고유 기업**: 1,122개
- **고유 스킬**: 728개
- **스킬 쌍**: 71,178개
- **평균 가중치**: 4.39 (각 스킬 쌍이 평균 4.39개 기업에서 함께 등장)

---

**분석 완료일**: 2024-11-25  
**원본 스크립트**: `Current/데이터관련_raw/build_skill_skill_network.py`  
**변환 대상**: `Current/개발자AND데이터관련_raw/data&developer_bipartite_skill_edges.csv`  
**출력 파일**: `Current/개발자AND데이터관련_raw/skill_skill_network.net`

