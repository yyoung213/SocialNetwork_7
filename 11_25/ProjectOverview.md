# 스킬 네트워크 분석 프로젝트 - SPEC 주도 구현계획

## 📋 프로젝트 개요

### 핵심 연구 질문
> **IT/데이터 직무에서 실제로 요구되는 스킬들이 서로 어떻게 연결되어 있고, 우리 학과 커리큘럼에서 강조하는 스킬 네트워크와 얼마나 맞아 떨어지는가?**

### 구현 목표
1. **채용 시장 스킬 네트워크** 구축 (원티드 채용 공고 기반)
2. **학과 커리큘럼 스킬 네트워크** 구축 (강의계획서/시행세칙 기반)
3. 두 네트워크의 **구조적 비교 분석** 및 **스킬 미스매치** 도출

### 기술 스택
- **코딩**: Python 3.x
- **네트워크 분석**: NetworkX
- **시각화**: Gephi (주요), Matplotlib (보조)
- **데이터 처리**: Pandas, NumPy

---

## 🏗️ 네트워크 구조 정의

### 1. 공고-스킬 Bipartite 네트워크
- **노드 타입 1**: 공고 노드 (Job Posting)
- **노드 타입 2**: 스킬 노드 (Skill)
- **엣지**: 특정 공고에서 요구된 각 스킬
  - 예: 공고 A가 Python, SQL, AWS 요구 → `(A, Python)`, `(A, SQL)`, `(A, AWS)`

### 2. 스킬-스킬 One-mode Projection 네트워크
- **노드**: 스킬 (기술 스택)
- **엣지**: 같은 채용 공고에서 함께 요구된 스킬 쌍
- **엣지 가중치**: 두 스킬이 같은 공고에서 함께 등장한 횟수
  - 예: Python-SQL이 120개 공고에서 함께 등장 → `weight = 120`

---

## 📐 SPEC 주도 구현 계획

### Phase 0: 프로젝트 환경 설정 및 스코프 정의

#### 0.1 프로젝트 디렉토리 구조
```
SocialNetwork_7/
├── 11_25/                    # 현재 작업 디렉토리
│   ├── ProjectOverview.md    # 본 문서
│   ├── scripts/              # 분석 스크립트
│   ├── data/                 # 데이터 파일
│   │   ├── raw/              # 원본 데이터
│   │   ├── processed/        # 전처리된 데이터
│   │   └── networks/         # 네트워크 파일 (.net, .gexf)
│   ├── results/              # 분석 결과
│   │   ├── figures/          # 시각화 이미지
│   │   ├── reports/          # 분석 보고서
│   │   └── gephi/            # Gephi 프로젝트 파일
│   └── requirements.txt      # Python 패키지 의존성
├── Current/                  # 기존 작업물
└── Past/                     # 과거 작업물
```

#### 0.2 Python 환경 설정
**파일**: `requirements.txt`
```txt
networkx>=3.0
pandas>=2.0
numpy>=1.24
matplotlib>=3.7
scipy>=1.10
openpyxl>=3.1
beautifulsoup4>=4.12
requests>=2.31
scikit-learn>=1.3
python-louvain>=0.16
```

#### 0.3 데이터 스코프 정의
- **기간**: 원티드 크롤링 추출 날짜 명시 (예: 2024-11-25)
- **직무 범위**: IT/데이터 관련 모든 구인공고
  - 데이터 분석가, 데이터 사이언티스트, 데이터 엔지니어
  - 백엔드 개발자, 프론트엔드 개발자
  - AI/ML 엔지니어, MLOps 엔지니어
  - 기타 IT 직무
- **지역**: 전국 (또는 특정 지역 지정)
- **데이터 출처**: 원티드 (wanted.co.kr)

---

### Phase 1: 데이터 수집 및 기본 전처리

#### 1.1 데이터 수집 자동화 시스템
**파일**: `scripts/01_data_collection.py`

**기능 명세**:
- 원티드 웹사이트에서 IT 직종별 구인공고 크롤링
- 각 공고에서 다음 정보 추출:
  - 기업명
  - 직무명
  - 주요업무
  - 필수역량
  - 우대사항
- 데이터 저장 형식: CSV (직무별로 분리)

**구현 함수**:
```python
def crawl_wanted_jobs(job_categories: List[str]) -> pd.DataFrame
def extract_job_info(job_url: str) -> Dict[str, str]
def save_raw_data(df: pd.DataFrame, job_category: str) -> None
```

**출력 파일**:
- `data/raw/{직무명}.csv` (예: `data/raw/데이터_분석가.csv`)

#### 1.2 데이터 기본 전처리
**파일**: `scripts/02_data_preprocessing.py`

**기능 명세**:
- 중복 공고 제거
- 결측치 처리
- 텍스트 정제 (특수문자, 공백 정리)
- 데이터 통합 (모든 직무를 하나의 DataFrame으로)

**구현 함수**:
```python
def load_all_job_data(raw_data_dir: str) -> pd.DataFrame
def clean_text(text: str) -> str
def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame
def merge_all_jobs(df_list: List[pd.DataFrame]) -> pd.DataFrame
```

**출력 파일**:
- `data/processed/jobs_merged.csv`

---

### Phase 2: 스킬 추출 및 정규화

#### 2.1 스킬 사전 설계 및 구축
**파일**: `scripts/03_skill_dictionary.py`

**기능 명세**:
- 각 직종별 데이터셋 분석하여 포함된 스킬 정리
- 동의어/표기 차이 정규화
  - 예: "React.js", "리액트", "React" → `React`
- 스킬 타입 분류 (Tool/Language vs Concept/Method)

**스킬 사전 구조**:
```python
SKILL_DICT = {
    'python': 'Python',
    '파이썬': 'Python',
    'react.js': 'React',
    '리액트': 'React',
    # ... (996개 키워드)
}

SKILL_TYPES = {
    'Python': 'Programming Language',
    'SQL': 'Database',
    'AWS': 'Infrastructure',
    'ML': 'Concept/Method',
    # ...
}
```

**구현 함수**:
```python
def build_skill_dictionary(df: pd.DataFrame) -> Dict[str, str]
def normalize_skill_name(skill: str, skill_dict: Dict) -> str
def classify_skill_type(skill: str) -> str
def save_skill_dictionary(skill_dict: Dict, output_path: str) -> None
```

**출력 파일**:
- `data/processed/skill_dictionary.json`
- `data/processed/skill_dictionary.xlsx`

#### 2.2 텍스트에서 스킬 매칭
**파일**: `scripts/04_skill_extraction.py`

**기능 명세**:
- 공고 텍스트(주요업무, 필수역량, 우대사항)에서 스킬 추출
- 정규표현식 기반 매칭
  - 예: "Python을 활용", "Python 기반", "SQL 작성" 모두 인식
- 각 공고별 스킬 리스트 생성

**구현 함수**:
```python
def extract_skills_from_text(text: str, skill_dict: Dict) -> List[str]
def extract_skills_from_job(job_row: pd.Series, skill_dict: Dict) -> List[str]
def process_all_jobs(df: pd.DataFrame, skill_dict: Dict) -> pd.DataFrame
```

**출력 파일**:
- `data/processed/jobs_with_skills.csv` (컬럼: 기업명, 직무명, Skills_List)

#### 2.3 스킬 빈도 분석 (기초 통계)
**파일**: `scripts/05_skill_frequency_analysis.py`

**기능 명세**:
- 전체 스킬 등장 빈도 계산
- Top N 스킬 리스트 생성
- 빈도 기반 통계 리포트 생성

**구현 함수**:
```python
def calculate_skill_frequency(df: pd.DataFrame) -> pd.Series
def get_top_skills(frequency: pd.Series, n: int = 50) -> pd.DataFrame
def generate_frequency_report(frequency: pd.Series, output_path: str) -> None
```

**출력 파일**:
- `results/reports/skill_frequency_report.csv`
- `results/figures/skill_frequency_barplot.png`

**기대 인사이트**:
- 양적 중요성 (빈도 기반) vs 구조적 중요성 (네트워크 중심성) 비교 준비

---

### Phase 3: Bipartite 네트워크 구축 및 시각화

#### 3.1 공고-스킬 Bipartite 네트워크 생성
**파일**: `scripts/06_build_bipartite_network.py`

**기능 명세**:
- NetworkX Bipartite Graph 생성
- 노드 속성 설정:
  - 공고 노드: 기업명, 직무명, 직무 카테고리
  - 스킬 노드: 스킬명, 스킬 타입
- 엣지: 공고-스킬 연결 (가중치 없음 또는 공고별 스킬 중요도)

**구현 함수**:
```python
def create_bipartite_network(df: pd.DataFrame) -> nx.Graph
def add_node_attributes(G: nx.Graph, df: pd.DataFrame) -> None
def calculate_bipartite_statistics(G: nx.Graph) -> Dict
def save_bipartite_network(G: nx.Graph, output_path: str, format: str = 'gexf') -> None
```

**출력 파일**:
- `data/networks/job_skill_bipartite.gexf` (Gephi용)
- `data/networks/job_skill_bipartite.net` (Pajek용)
- `data/networks/job_skill_bipartite.graphml` (GraphML)

#### 3.2 Bipartite 네트워크 시각화 전략
**파일**: `scripts/07_visualize_bipartite.py`

**시각화 명세**:
- 공고 노드: 작게 표시
- 스킬 노드: 크게 표시 (해당 스킬을 요구하는 공고 수에 비례)
- 직무별 색상 구분:
  - 데이터 관련: 파란색 계열
  - 백엔드: 초록색 계열
  - 프론트엔드: 주황색 계열
  - AI/ML: 보라색 계열
- 레이아웃: Bipartite Layout (두 레이어로 분리)

**구현 함수**:
```python
def visualize_bipartite_network(G: nx.Graph, output_path: str) -> None
def assign_job_colors(G: nx.Graph, job_categories: Dict) -> Dict
def calculate_skill_degrees(G: nx.Graph) -> Dict
```

**출력 파일**:
- `results/figures/bipartite_network_visualization.png`
- `results/gephi/bipartite_network.gexf` (Gephi에서 추가 편집용)

**기대 인사이트**:
- 어떤 스킬이 여러 직무에 공통으로 요구되는지 시각적 확인
- 예: Python이 데이터 분석가, 백엔드, AI 연구원 모두와 연결되는 허브 역할

---

### Phase 4: One-mode Projection 및 필터링

#### 4.1 스킬-스킬 네트워크 생성 (One-mode Projection)
**파일**: `scripts/08_build_skill_skill_network.py`

**기능 명세**:
- Bipartite 네트워크에서 스킬 노드만 추출
- 같은 공고에서 함께 등장한 스킬 쌍을 엣지로 연결
- 엣지 가중치: 두 스킬이 함께 등장한 공고 수

**구현 함수**:
```python
def project_to_skill_network(bipartite_G: nx.Graph) -> nx.Graph
def calculate_cooccurrence_weights(bipartite_G: nx.Graph) -> Dict[Tuple, int]
def create_weighted_skill_network(cooccurrence: Dict) -> nx.Graph
```

**출력 파일**:
- `data/networks/skill_skill_network.gexf`
- `data/networks/skill_skill_network.net`

#### 4.2 네트워크 필터링
**파일**: `scripts/09_filter_network.py`

**기능 명세**:
- 최소 가중치 임계값 설정 (예: weight ≥ 3, 5)
- 너무 약한 엣지 제거하여 핵심 구조만 유지
- 고립 노드 제거 (degree = 0)

**구현 함수**:
```python
def filter_by_weight(G: nx.Graph, min_weight: int = 3) -> nx.Graph
def remove_isolated_nodes(G: nx.Graph) -> nx.Graph
def filter_by_degree(G: nx.Graph, min_degree: int = 1) -> nx.Graph
```

**출력 파일**:
- `data/networks/skill_skill_network_filtered.gexf` (필터링된 버전)

---

### Phase 5: Max-Component 분석

#### 5.1 연결 성분 분석
**파일**: `scripts/10_analyze_components.py`

**기능 명세**:
- 모든 연결 성분(Component) 찾기
- 최대 연결 성분(Max-Component / Giant Component) 추출
- 각 성분의 통계 계산:
  - 노드 수, 엣지 수
  - 평균 degree, 밀도
  - 평균 클러스터링 계수

**구현 함수**:
```python
def find_connected_components(G: nx.Graph) -> List[Set]
def extract_max_component(G: nx.Graph) -> nx.Graph
def analyze_component_statistics(G: nx.Graph) -> Dict
def compare_components(components: List[Set]) -> pd.DataFrame
```

**출력 파일**:
- `results/reports/component_analysis.csv`
- `data/networks/skill_skill_network_max_component.gexf`

**기대 인사이트**:
- 직무 간 스킬 생태계의 연결성 정도 파악
- Giant Component가 크면 → 경력 이동이 쉬운 시장 구조
- Giant Component가 작으면 → 전문화가 심한 시장 구조

---

### Phase 6: Degree Distribution 분석 (PDF/CCDF/Power-law)

#### 6.1 Degree Distribution 계산 및 시각화
**파일**: `scripts/11_degree_distribution_analysis.py`

**기능 명세**:
- PDF (Probability Density Function) 계산
- CDF (Cumulative Distribution Function) 계산
- CCDF (Complementary CDF = 1 - CDF) 계산
- 로그-로그 스케일 시각화
- Power-law tail 확인

**구현 함수**:
```python
def calculate_degree_distribution(G: nx.Graph) -> Tuple[np.ndarray, np.ndarray, np.ndarray]
def plot_degree_distributions(degrees: np.ndarray, output_path: str) -> None
def fit_power_law(degrees: np.ndarray) -> Tuple[float, float]  # exponent, R²
def identify_hub_nodes(G: nx.Graph, percentile: float = 95) -> List
```

**출력 파일**:
- `results/figures/degree_distribution_analysis.png` (6개 서브플롯)
- `results/reports/power_law_analysis.txt`

**시각화 구성**:
1. PDF (선형 스케일)
2. PDF (로그-로그 스케일)
3. CCDF (선형 스케일)
4. CCDF (로그-로그 스케일) - Power Law 확인용
5. CDF (선형 스케일)
6. CDF (로그 X축 스케일)

**기대 인사이트**:
- 스킬 생태계의 구조적 불평등 확인
- 소수의 슈퍼 허브 존재 여부 (Python, SQL, AWS 등)
- 네트워크 중심성 분석의 기초 데이터 제공

---

### Phase 7: 중심성 분석 (Core Skills 찾기)

#### 7.1 중심성 지표 계산
**파일**: `scripts/12_centrality_analysis.py`

**기능 명세**:
다음 중심성 지표들을 모두 계산:
- **Degree Centrality**: 연결된 스킬 수
- **Weighted Degree (Strength)**: 가중치 합
- **Betweenness Centrality**: 다른 스킬 집단 사이를 잇는 경유 허브 역할
- **Closeness Centrality**: 모든 노드까지의 평균 거리
- **Eigenvector Centrality**: 중요 스킬들과의 연결 정도
- **PageRank**: 권위/명성 기반 중요도

**구현 함수**:
```python
def calculate_all_centralities(G: nx.Graph) -> pd.DataFrame
def get_top_skills_by_centrality(centralities: pd.DataFrame, metric: str, n: int = 10) -> pd.DataFrame
def compare_centrality_metrics(centralities: pd.DataFrame) -> pd.DataFrame
def save_centrality_report(centralities: pd.DataFrame, output_path: str) -> None
```

**출력 파일**:
- `results/reports/centrality_analysis.csv` (모든 중심성 지표 포함)
- `results/reports/top_skills_by_centrality.csv` (지표별 Top 10)

#### 7.2 중심성 지표 비교 분석
**파일**: `scripts/13_centrality_comparison.py`

**기능 명세**:
- 각 중심성 지표별 Top 10 스킬 리스트 생성
- 지표 간 상관관계 분석
- "양적 중요성 vs 구조적 중요성" 비교

**구현 함수**:
```python
def compare_top_skills(centralities: pd.DataFrame) -> Dict[str, List]
def analyze_centrality_correlations(centralities: pd.DataFrame) -> pd.DataFrame
def identify_structural_hubs(centralities: pd.DataFrame) -> List[str]
```

**출력 파일**:
- `results/reports/centrality_comparison.csv`
- `results/figures/centrality_correlation_heatmap.png`

**기대 인사이트**:
- 단순히 많이 언급된 스킬 vs 실제 네트워크 구조에서 허브 역할을 하는 스킬 구분
- 예: Python, SQL, AWS가 정말 "핵심 인프라"인지 검증

---

### Phase 8: 노드 속성 기반 시각화

#### 8.1 속성 기반 네트워크 시각화
**파일**: `scripts/14_visualize_with_attributes.py`

**기능 명세**:
Zachary's Karate Club Network 스타일의 시각화:
- **노드 크기**: 중심성 (Eigenvector 또는 PageRank)
- **노드 색상**: 커뮤니티 (나중에 Phase 9에서 할당)
- **노드 테두리 색상**: 스킬 타입 (Tool/Language vs Concept/Method)
- **엣지 두께**: 가중치

**구현 함수**:
```python
def visualize_network_with_attributes(G: nx.Graph, node_attributes: Dict, output_path: str) -> None
def assign_node_colors_by_community(G: nx.Graph, communities: Dict) -> Dict
def assign_node_border_by_type(G: nx.Graph, skill_types: Dict) -> Dict
def create_multiple_views(G: nx.Graph, output_dir: str) -> None
```

**출력 파일**:
- `results/figures/network_node_attributes_visualization.png` (6개 서브플롯)
- `results/gephi/skill_network_with_attributes.gexf` (Gephi에서 추가 편집)

**시각화 구성**:
1. Degree 기반 시각화
2. Betweenness Centrality 기반 (브로커 역할 강조)
3. Clustering Coefficient 기반 (지역적 밀집도)
4. Eigenvector Centrality 기반 (영향력 있는 노드와 연결)
5. Degree vs Clustering 산점도
6. 허브 노드 강조 시각화 (상위 5% Degree)

**기대 인사이트**:
- 데이터 군집 / 백엔드 군집 / 프론트 군집이 직관적으로 구분됨
- 교량 스킬(브릿지)이 시각적으로 튀어나옴

---

### Phase 9: 군집 분석 (Community Detection)

#### 9.1 커뮤니티 탐지
**파일**: `scripts/15_community_detection.py`

**기능 명세**:
- Louvain 알고리즘 적용
- Leiden 알고리즘 적용 (선택사항, 더 정확한 결과)
- 각 군집을 "직무/역할" 관점으로 해석

**구현 함수**:
```python
def detect_communities_louvain(G: nx.Graph) -> Dict[int, List]
def detect_communities_leiden(G: nx.Graph) -> Dict[int, List]
def interpret_communities(communities: Dict, G: nx.Graph, skill_types: Dict) -> pd.DataFrame
def visualize_communities(G: nx.Graph, communities: Dict, output_path: str) -> None
```

**출력 파일**:
- `results/reports/community_analysis.csv` (각 군집의 주요 스킬 리스트)
- `results/figures/community_visualization.png`
- `data/networks/skill_network_with_communities.gexf` (커뮤니티 ID 속성 포함)

#### 9.2 서브그래프별 z-score 계산
**파일**: `scripts/16_subgraph_zscore_analysis.py`

**기능 명세**:
각 커뮤니티(서브그래프)에 대해:
- 서브그래프 내부의 average degree 계산
- 네트워크 전체 평균 degree와 비교
- z-score = (community_degree_avg - network_avg) / std 계산

**구현 함수**:
```python
def calculate_subgraph_statistics(G: nx.Graph, communities: Dict) -> pd.DataFrame
def calculate_zscore(community_avg: float, network_avg: float, network_std: float) -> float
def compare_community_densities(G: nx.Graph, communities: Dict) -> pd.DataFrame
```

**출력 파일**:
- `results/reports/community_zscore_analysis.csv`

**기대 인사이트**:
- 군집별 스킬 응집도 비교
- z-score가 큰 군집 = 더 조밀하고 내부 연결이 강한 직무
- 예: 데이터 분석 군집 (높은 z-score) vs AI 군집 (낮은 z-score)

---

### Phase 10: 브릿지 스킬 분석

#### 10.1 브릿지 스킬 식별
**파일**: `scripts/17_bridge_skill_analysis.py`

**기능 명세**:
- Betweenness Centrality 기반 브릿지 스킬 식별
- 커뮤니티 간 연결 엣지 분석
- 예: 데이터 분석 군집과 백엔드 군집 사이를 연결하는 스킬

**구현 함수**:
```python
def identify_bridge_skills(G: nx.Graph, communities: Dict) -> List[str]
def analyze_inter_community_edges(G: nx.Graph, communities: Dict) -> pd.DataFrame
def find_career_path_skills(G: nx.Graph, communities: Dict) -> Dict[str, List[str]]
```

**출력 파일**:
- `results/reports/bridge_skills_analysis.csv`
- `results/figures/bridge_skills_visualization.png`

**기대 인사이트**:
- "한 학생이 스킬을 어떻게 조합해서 경로를 이동할 수 있는가?"
- 예: 데이터 분석가 → MLOps 엔지니어로 넘어가려면 어떤 브릿지 스킬이 핵심인지
- 커리어 경로 설계 관점에서 "경력 피벗(pivot) 시 필요한 스킬" 도출

---

### Phase 11: 학과 커리큘럼 스킬 네트워크 구축

#### 11.1 학과 커리큘럼 데이터 수집
**파일**: `scripts/18_collect_curriculum_data.py`

**기능 명세**:
- 강의계획서에서 데이터 추출
- 교육과정/시행세칙에서 "학습 목표", "주요 내용" 추출
- 각 과목별 스킬 리스트 생성

**데이터 소스**:
- 강의계획서 (PDF 또는 웹 스크래핑)
- 교육과정 문서 (Excel 또는 PDF)

**구현 함수**:
```python
def extract_course_info(course_file: str) -> Dict[str, str]
def extract_skills_from_course(course_text: str, skill_dict: Dict) -> List[str]
def build_curriculum_dataset(course_files: List[str], skill_dict: Dict) -> pd.DataFrame
```

**출력 파일**:
- `data/raw/curriculum_courses.csv` (컬럼: 과목명, 학점, 필수/선택, Skills_List)

#### 11.2 과목-스킬 Bipartite 네트워크 생성
**파일**: `scripts/19_build_curriculum_bipartite.py`

**기능 명세**:
- 채용 데이터와 동일한 스킬 사전 사용
- 과목-스킬 Bipartite 네트워크 생성
- 과목 속성: 학점, 필수/선택 여부

**구현 함수**:
```python
def create_curriculum_bipartite(df: pd.DataFrame) -> nx.Graph
def add_course_attributes(G: nx.Graph, df: pd.DataFrame) -> None
def calculate_course_skill_coverage(G: nx.Graph) -> pd.DataFrame
```

**출력 파일**:
- `data/networks/curriculum_bipartite.gexf`

#### 11.3 학과 스킬-스킬 네트워크 생성
**파일**: `scripts/20_build_curriculum_skill_network.py`

**기능 명세**:
- One-mode Projection으로 스킬-스킬 네트워크 생성
- 가중치: 같이 다루는 과목 수
- 선택적 가중치: 학점/필수 여부 반영

**구현 함수**:
```python
def project_curriculum_to_skill_network(bipartite_G: nx.Graph) -> nx.Graph
def calculate_weighted_cooccurrence(bipartite_G: nx.Graph, weight_by_credit: bool = False) -> Dict
```

**출력 파일**:
- `data/networks/curriculum_skill_network.gexf`

#### 11.4 학과 네트워크 동일 분석 수행
**파일**: `scripts/21_analyze_curriculum_network.py`

**기능 명세**:
- Phase 5-10과 동일한 분석을 학과 네트워크에 적용:
  - Max-Component 분석
  - Degree Distribution 분석
  - 중심성 분석
  - 커뮤니티 탐지
  - z-score 분석

**구현 함수**:
```python
def analyze_curriculum_network(G: nx.Graph) -> Dict
def generate_curriculum_reports(G: nx.Graph, output_dir: str) -> None
```

**출력 파일**:
- `results/reports/curriculum_network_analysis/` (모든 분석 결과)

**기대 인사이트**:
- 학과가 어떤 스킬 조합을 "함께 가르치고 있는지" 구조적으로 파악
- 예: Python과 SQL을 같이 가르치지 않는데, 산업에서는 항상 같이 등장 → 교육 설계상 갭

---

### Phase 12: 산업 vs 학과 네트워크 비교 분석

#### 12.1 노드(스킬) 수준 비교
**파일**: `scripts/22_compare_networks_node_level.py`

**기능 명세**:
- 두 네트워크의 중심성 지표 비교
- 산업 중심성 Top 20 vs 학과 중심성 Top 20
- 교집합 / 산업에만 있는 스킬 / 학과에만 있는 스킬 분리
- Coverage 지표: 산업 Top 20 중 학과 네트워크에 포함된 비율 (%)

**구현 함수**:
```python
def compare_centralities(industry_centralities: pd.DataFrame, 
                        curriculum_centralities: pd.DataFrame) -> pd.DataFrame
def calculate_coverage(industry_top: List[str], curriculum_skills: Set[str]) -> float
def identify_skill_gaps(industry_centralities: pd.DataFrame, 
                       curriculum_centralities: pd.DataFrame) -> Dict
```

**출력 파일**:
- `results/reports/network_comparison_node_level.csv`
- `results/figures/centrality_comparison_scatter.png`

#### 12.2 엣지/군집 수준 비교
**파일**: `scripts/23_compare_networks_edge_level.py`

**기능 명세**:
- 산업에서 강하게 연결된 스킬 쌍이 학과에서도 함께 다뤄지는지 확인
- 산업 네트워크 군집 vs 학과 네트워크 군집 구조 비교
- 차이 네트워크 생성:
  - 산업에서만 강한 엣지: 빨간색
  - 학과에서만 강한 엣지: 파란색
  - 둘 다 강한 엣지: 굵게 표시

**구현 함수**:
```python
def compare_edge_strengths(industry_G: nx.Graph, curriculum_G: nx.Graph) -> pd.DataFrame
def compare_communities(industry_communities: Dict, curriculum_communities: Dict) -> pd.DataFrame
def create_difference_network(industry_G: nx.Graph, curriculum_G: nx.Graph) -> nx.Graph
def visualize_difference_network(diff_G: nx.Graph, output_path: str) -> None
```

**출력 파일**:
- `results/reports/network_comparison_edge_level.csv`
- `results/reports/community_comparison.csv`
- `results/figures/difference_network_visualization.png`
- `data/networks/difference_network.gexf`

#### 12.3 스킬 미스매치 종합 분석
**파일**: `scripts/24_skill_mismatch_analysis.py`

**기능 명세**:
- 모든 비교 결과를 종합하여 스킬 미스매치 리포트 생성
- 교육과정 개선 제안 도출

**구현 함수**:
```python
def generate_mismatch_report(comparison_results: Dict) -> pd.DataFrame
def suggest_curriculum_improvements(mismatch_report: pd.DataFrame) -> List[str]
def create_executive_summary(all_results: Dict) -> str
```

**출력 파일**:
- `results/reports/skill_mismatch_comprehensive_report.csv`
- `results/reports/curriculum_improvement_suggestions.txt`
- `results/reports/executive_summary.md`

**기대 인사이트**:
- "우리 학과 커리큘럼이 산업에서 요구하는 스킬 네트워크를 어느 정도 커버하는가?"
- "어떤 스킬은 과도하게 강조되고, 어떤 스킬은 거의 다루지 않지만 산업에서는 핵심인가?"
- → 교육과정 개선 제안으로 자연스럽게 이어짐
  - 예: "데이터 엔지니어링·MLOps 관련 스킬 강화 필요"

---

### Phase 13: Gephi 시각화 및 최종 리포트

#### 13.1 Gephi용 네트워크 파일 최적화
**파일**: `scripts/25_prepare_gephi_files.py`

**기능 명세**:
- 모든 네트워크를 Gephi 호환 형식(.gexf)으로 저장
- 노드 속성 포함:
  - 중심성 지표들
  - 커뮤니티 ID
  - 스킬 타입
  - 등장 빈도
- 엣지 속성:
  - 가중치
  - 커뮤니티 간 연결 여부

**구현 함수**:
```python
def prepare_gephi_file(G: nx.Graph, node_attributes: Dict, output_path: str) -> None
def create_gephi_project_file(network_files: List[str], output_path: str) -> None
```

**출력 파일**:
- `results/gephi/industry_skill_network.gexf`
- `results/gephi/curriculum_skill_network.gexf`
- `results/gephi/difference_network.gexf`
- `results/gephi/gephi_project.gephi` (Gephi 프로젝트 파일)

#### 13.2 Gephi 시각화 가이드
**파일**: `results/reports/gephi_visualization_guide.md`

**내용**:
- Gephi에서 네트워크 로드 방법
- 레이아웃 알고리즘 추천 (ForceAtlas2, Yifan Hu 등)
- 노드 크기/색상 설정 방법
- 엣지 두께/색상 설정 방법
- 필터링 방법
- 고품질 이미지 내보내기 방법

#### 13.3 최종 종합 리포트 생성
**파일**: `scripts/26_generate_final_report.py`

**기능 명세**:
- 모든 분석 결과를 종합한 최종 리포트 생성
- Markdown 형식의 종합 보고서
- 주요 인사이트 요약
- 시각화 이미지 포함

**구현 함수**:
```python
def generate_final_report(all_results: Dict, output_path: str) -> None
def create_insights_summary(analysis_results: Dict) -> List[str]
def compile_all_figures(figure_dir: str, output_path: str) -> None
```

**출력 파일**:
- `results/reports/final_comprehensive_report.md`
- `results/reports/final_comprehensive_report.pdf` (선택사항)

---

## 📊 분석 결과물 체크리스트

### 필수 포함 Points 확인

- [x] **Max-Component 분석** (Phase 5)
- [x] **Degree Distribution (PDF/CCDF)** (Phase 6)
- [x] **Power-law tail 분석** (Phase 6)
- [x] **노드 속성 기반 시각화** (Phase 8)
- [x] **서브그래프 z-score 분석** (Phase 9.2)

### 추가 분석 항목

- [x] 중심성 분석 (다양한 지표)
- [x] 커뮤니티 탐지
- [x] 브릿지 스킬 분석
- [x] 산업 vs 학과 네트워크 비교

---

## 🔄 구현 우선순위 및 일정

### Phase 1-4: 기초 구축 (1-2주)
- 데이터 수집 및 전처리
- 스킬 추출 및 정규화
- Bipartite 네트워크 구축

### Phase 5-7: 핵심 분석 (1주)
- Max-Component 분석
- Degree Distribution 분석
- 중심성 분석

### Phase 8-10: 심화 분석 (1주)
- 노드 속성 시각화
- 커뮤니티 탐지
- 브릿지 스킬 분석

### Phase 11-12: 비교 분석 (1-2주)
- 학과 네트워크 구축
- 산업 vs 학과 비교

### Phase 13: 최종 정리 (3-5일)
- Gephi 시각화
- 최종 리포트 작성

---

## 📝 참고사항

### 스킬 정의의 수준 통일
- **Tool/Language**: Python, SQL, React, AWS, Docker 등
- **Concept/Method**: ML, DL, Statistics, A/B Testing 등
- 분석 시 두 레벨을 구분하여 태깅하고, 필요시 별도 분석 수행

### 해석 프레임
- **학생 입장**: 어떤 스킬 조합을 갖추면 어떤 커리어 군집에 접근 가능한지
- **학과 입장**: 어떤 과목/트랙을 보완하면 산업 네트워크와 더 잘 align 되는지

---

## 🚀 다음 단계

1. **프로젝트 디렉토리 구조 생성**
2. **Python 환경 설정** (`requirements.txt` 설치)
3. **Phase 1부터 순차적으로 구현 시작**
4. **각 Phase 완료 시 중간 검토 및 수정**

---

**작성일**: 2024-11-25  
**버전**: 1.0

