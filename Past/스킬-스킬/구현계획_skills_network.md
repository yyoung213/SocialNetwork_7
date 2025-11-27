# Skills-Skills 네트워크 구축 구현 계획

## 1. 데이터 구조 분석

### 1.1 입력 파일 구조

#### `bipartite_skill_wide.csv`
- **구조**: 각 행은 하나의 구인공고를 나타냄
- **컬럼**:
  - `기업명`: 구인공고를 올린 기업명
  - `Skills_List`: 문자열 형태의 리스트 (예: `"['Python', 'AWS', 'AI']"`)
- **특징**: 
  - `Skills_List`는 문자열로 저장되어 있어 `ast.literal_eval()`로 파싱 필요
  - 각 구인공고마다 여러 스킬이 리스트 형태로 저장됨
  - 같은 기업이 여러 구인공고를 올릴 수 있음 (각 행이 독립적인 구인공고)

#### `unique_skills_list.txt`
- **구조**: 779개의 고유 스킬 목록
- **형식**: 
  ```
  총 고유 스킬 개수: 779
  
  1. .NET
  2. .NET Core
  ...
  ```
- **용도**: 네트워크 노드로 사용할 스킬 목록 확인용

#### `raw_data/` 폴더
- **구조**: 직군별 구인공고 원본 데이터
- **컬럼**: `기업명`, `주요업무`, `자격요건`, `우대사항`
- **참고**: 네트워크 구축에는 직접 사용하지 않지만, 데이터 출처 확인용

### 1.2 네트워크 구조 설계

#### 노드 (Nodes)
- **타입**: 스킬 (Skill)
- **개수**: 약 779개의 고유 스킬
- **속성**: 스킬명

#### 엣지 (Edges)
- **타입**: 무방향 그래프 (Undirected Graph)
- **생성 조건**: 두 스킬이 **같은 구인공고**에서 함께 언급된 경우
- **가중치**: 
  - 옵션 1: 두 스킬이 함께 나타난 구인공고의 개수 (co-occurrence count)
  - 옵션 2: 이진 값 (1 또는 0, 함께 나타났는지 여부만)
- **예시**: 
  - 구인공고 A: `['Python', 'AWS', 'AI']`
  - 생성되는 엣지: `Python-AWS`, `Python-AI`, `AWS-AI` (각각 가중치 1)

## 2. 구현 단계

### 2.1 데이터 로딩 및 전처리

#### 단계 1: `bipartite_skill_wide.csv` 파일 읽기
- pandas를 사용하여 CSV 파일 로드
- 각 행의 `Skills_List` 컬럼을 파싱하여 실제 리스트로 변환
- 파싱 오류 처리 (try-except)

#### 단계 2: 스킬 리스트 추출
- 각 구인공고(행)에서 스킬 리스트 추출
- 빈 리스트나 None 값 처리
- 스킬명 정규화 (공백 제거, 대소문자 통일 등 필요시)

### 2.2 네트워크 엣지 생성

#### 단계 3: Co-occurrence 계산
- 각 구인공고마다:
  - 해당 구인공고의 스킬 리스트에서 모든 스킬 쌍(combination) 생성
  - 같은 구인공고 내에서만 쌍을 생성 (다른 구인공고와는 독립적)
- 모든 구인공고를 순회하며 스킬 쌍의 출현 횟수 집계
- 결과: `{(skill1, skill2): count}` 형태의 딕셔너리

#### 단계 4: 엣지 리스트 생성
- 집계된 스킬 쌍을 엣지 리스트로 변환
- 무방향 그래프이므로 `(A, B)`와 `(B, A)`는 동일하게 처리
- 가중치가 0인 엣지는 제외 (선택사항)

### 2.3 네트워크 그래프 생성

#### 단계 5: NetworkX 그래프 객체 생성
- `networkx.Graph()` 또는 `networkx.Graph()` 사용
- 노드 추가: 모든 고유 스킬을 노드로 추가
- 엣지 추가: 생성된 엣지 리스트를 기반으로 엣지 추가
- 가중치가 있는 경우 `weight` 속성으로 저장

#### 단계 6: 네트워크 통계 계산
- 노드 수, 엣지 수
- 평균 degree, 최대 degree
- 연결성 (connected components)
- 밀도 (density)
- 클러스터링 계수 (clustering coefficient)

### 2.4 결과 저장

#### 단계 7: 네트워크 파일 저장
- **GraphML 형식**: `.graphml` (NetworkX 기본 형식)
- **Edge List 형식**: `.csv` (노드1, 노드2, 가중치)
- **GEXF 형식**: `.gexf` (Gephi 호환)

#### 단계 8: 통계 정보 저장
- 네트워크 통계를 텍스트 파일 또는 JSON으로 저장
- 노드별 degree 정보 저장 (선택사항)

## 3. 구현 세부사항

### 3.1 주요 함수 설계

```python
def load_bipartite_data(csv_file):
    """bipartite_skill_wide.csv 파일을 로드하고 파싱"""
    # CSV 읽기
    # Skills_List 파싱
    # 반환: DataFrame

def extract_skill_pairs_from_job(skills_list):
    """하나의 구인공고에서 모든 스킬 쌍 추출"""
    # combinations 사용
    # 반환: [(skill1, skill2), ...] 리스트

def build_cooccurrence_matrix(df):
    """모든 구인공고를 순회하며 co-occurrence 계산"""
    # 각 구인공고에서 스킬 쌍 추출
    # Counter로 집계
    # 반환: {(skill1, skill2): count} 딕셔너리

def create_skill_network(cooccurrence_dict, min_weight=1):
    """NetworkX 그래프 생성"""
    # Graph 생성
    # 노드 추가
    # 엣지 추가 (가중치 포함)
    # 반환: NetworkX Graph 객체

def calculate_network_statistics(G):
    """네트워크 통계 계산"""
    # 기본 통계
    # 반환: 딕셔너리

def save_network(G, output_prefix):
    """네트워크를 여러 형식으로 저장"""
    # GraphML, CSV, GEXF 등
```

### 3.2 데이터 처리 고려사항

1. **스킬명 정규화**
   - 공백 제거
   - 대소문자 통일 (필요시)
   - `unique_skills_list.txt`와 일치하는지 확인

2. **중복 처리**
   - 같은 구인공고 내에서 같은 스킬이 중복으로 나타나는 경우
   - 집합(set)을 사용하여 중복 제거

3. **엣지 가중치**
   - 기본: 두 스킬이 함께 나타난 구인공고 개수
   - 정규화 옵션: Jaccard similarity, cosine similarity 등

4. **필터링 옵션**
   - 최소 가중치 임계값 설정 (너무 적게 나타나는 엣지 제거)
   - 최소 degree 임계값 설정 (고립된 노드 제거)

### 3.3 성능 최적화

1. **메모리 효율성**
   - 대용량 데이터의 경우 Counter 사용
   - 필요시 청크 단위 처리

2. **계산 효율성**
   - combinations는 itertools 사용
   - 대용량 네트워크의 경우 sparse matrix 고려

## 4. 예상 결과물

### 4.1 파일 출력
- `skill_network.graphml`: NetworkX GraphML 형식
- `skill_network_edges.csv`: 엣지 리스트 (노드1, 노드2, weight)
- `skill_network_stats.txt`: 네트워크 통계 정보
- `skill_network.gexf`: Gephi 호환 형식 (선택사항)

### 4.2 네트워크 특성
- **노드 수**: 약 779개 (고유 스킬 수)
- **엣지 수**: 예상 수천~수만 개 (스킬 쌍의 co-occurrence)
- **네트워크 타입**: 무방향, 가중치 그래프
- **예상 밀도**: 낮음 (sparse network)

### 4.3 분석 가능한 내용
- 어떤 스킬들이 자주 함께 요구되는가?
- 스킬 간의 연결성과 클러스터 구조
- 중심성 높은 스킬 (degree centrality)
- 커뮤니티 구조 (community detection)

## 5. 구현 순서 요약

1. ✅ 데이터 파일 구조 확인 및 이해
2. ⬜ `bipartite_skill_wide.csv` 로딩 및 파싱 함수 구현
3. ⬜ 구인공고별 스킬 쌍 추출 함수 구현
4. ⬜ Co-occurrence 계산 함수 구현
5. ⬜ NetworkX 그래프 생성 함수 구현
6. ⬜ 네트워크 통계 계산 함수 구현
7. ⬜ 결과 저장 함수 구현
8. ⬜ 메인 함수 통합 및 테스트
9. ⬜ 결과 검증 및 시각화 (선택사항)

## 6. 추가 고려사항

### 6.1 데이터 검증
- `bipartite_skill_wide.csv`의 모든 행이 올바르게 파싱되는지 확인
- 추출된 스킬이 `unique_skills_list.txt`와 일치하는지 확인

### 6.2 시각화 옵션
- NetworkX 기본 시각화
- Gephi로 export하여 고급 시각화
- Python 시각화 라이브러리 (matplotlib, plotly 등)

### 6.3 확장 가능성
- 직군별 네트워크 분리 생성
- 시간에 따른 네트워크 변화 분석 (시계열 데이터가 있는 경우)
- 스킬 카테고리별 서브네트워크 분석

