# Pajek 네트워크 시각화 가이드

## 1. 파일 열기

### 기본 단계
1. **Pajek 실행**
   - Pajek 프로그램을 실행합니다
   - 메인 창이 열립니다

2. **네트워크 파일 로드**
   - 메뉴: `File` → `Network` → `Read`
   - 또는 단축키: `Ctrl + N`
   - `job_network_100.net` 파일 선택
   - 파일이 성공적으로 로드되면 하단 상태바에 노드 수와 엣지 수가 표시됩니다

3. **인코딩 확인**
   - 한글 노드 이름이 깨져 보이면:
     - `File` → `Preferences` → `Default Text Encoding`
     - `UTF-8` 선택

---

## 2. 레이아웃 설정 (가독성 향상)

### 2.1 기본 레이아웃 적용

1. **Force-Directed Layout (Spring Embedder)**
   - 메뉴: `Draw` → `Energy` → `Kamada-Kawai` 또는 `Fruchterman-Reingold`
   - 가장 일반적이고 가독성이 좋은 레이아웃
   - **Kamada-Kawai**: 더 균등한 노드 배치
   - **Fruchterman-Reingold**: 더 빠른 계산, 큰 네트워크에 적합

2. **레이아웃 실행**
   - `Draw` → `Energy` → `Kamada-Kawai` → `Free`
   - 또는 `Draw` → `Energy` → `Fruchterman-Reingold` → `Free`
   - 계산이 완료될 때까지 대기

### 2.2 레이아웃 조정

1. **수동 조정**
   - `Draw` → `Move` → `Move` 또는 `Move X/Y`
   - 마우스로 노드를 드래그하여 위치 조정

2. **레이아웃 재계산**
   - 레이아웃이 마음에 들지 않으면 다시 실행
   - `Draw` → `Energy` → `Kamada-Kawai` → `Free` (다시 실행)

---

## 3. 노드 스타일 설정

### 3.1 노드 크기 조정

1. **노드 크기 설정**
   - `Draw` → `Options` → `Size` → `of Vertices`
   - 기본값: 10-20
   - 큰 네트워크: 5-10
   - 작은 네트워크: 15-25

2. **노드 크기 자동 조정 (중심성 기반)**
   - `Net` → `Vector` → `Centrality` → `Degree` (연결 수 기반)
   - 또는 `Net` → `Vector` → `Centrality` → `Betweenness` (중개 중심성)
   - `Draw` → `Options` → `Size` → `of Vertices` → `Proportional to Values`
   - 중심성이 높은 노드가 더 크게 표시됩니다

### 3.2 노드 색상 설정

1. **단일 색상**
   - `Draw` → `Options` → `Colors` → `Vertices`
   - 색상 선택 (예: 파란색, 빨간색)

2. **그룹별 색상**
   - `Net` → `Partitions` → `Create` → `Random Network`
   - 또는 커뮤니티 탐지: `Net` → `Vector` → `Clustering` → `Louvain`
   - `Draw` → `Options` → `Colors` → `Vertices` → `by Partition`
   - 같은 그룹의 노드가 같은 색상으로 표시됩니다

3. **중심성 기반 색상 그라데이션**
   - `Net` → `Vector` → `Centrality` → `Degree`
   - `Draw` → `Options` → `Colors` → `Vertices` → `by Values`
   - 중심성이 높을수록 진한 색상으로 표시됩니다

### 3.3 노드 레이블 표시

1. **레이블 표시**
   - `Draw` → `Options` → `Labels` → `Show Labels`
   - 또는 단축키: `Ctrl + L`

2. **레이블 크기 조정**
   - `Draw` → `Options` → `Labels` → `Size`
   - 기본값: 10-12
   - 큰 네트워크: 8-10
   - 작은 네트워크: 12-15

3. **레이블 위치 조정**
   - `Draw` → `Options` → `Labels` → `Position`
   - `Below`, `Above`, `Left`, `Right` 중 선택

---

## 4. 엣지 스타일 설정

### 4.1 엣지 두께 조정

1. **가중치 기반 두께**
   - `Draw` → `Options` → `Size` → `of Lines`
   - `Proportional to Values` 선택
   - 가중치가 높은 엣지가 더 두껍게 표시됩니다

2. **엣지 두께 범위 설정**
   - `Draw` → `Options` → `Size` → `of Lines`
   - `Min`과 `Max` 값 조정
   - 예: Min=1, Max=5

### 4.2 엣지 색상 설정

1. **단일 색상**
   - `Draw` → `Options` → `Colors` → `Lines`
   - 기본값: 회색 또는 검은색

2. **가중치 기반 색상**
   - `Draw` → `Options` → `Colors` → `Lines` → `by Values`
   - 가중치가 높을수록 진한 색상으로 표시됩니다

### 4.3 엣지 표시 옵션

1. **엣지 숨기기/보이기**
   - `Draw` → `Options` → `Lines` → `Show Lines`
   - 또는 단축키: `Ctrl + E`

2. **엣지 방향 표시**
   - 무방향 그래프이므로 화살표는 표시하지 않습니다
   - 방향 그래프인 경우: `Draw` → `Options` → `Arrows` → `Show Arrows`

---

## 5. 네트워크 필터링 (가독성 향상)

### 5.1 연결되지 않은 노드 제거

1. **Isolated Nodes 제거**
   - `Net` → `Transform` → `Remove` → `Isolated Vertices`
   - 연결되지 않은 노드를 제거하여 네트워크를 단순화합니다

### 5.2 가중치 기반 필터링

1. **약한 연결 제거**
   - `Net` → `Transform` → `Remove` → `Lines` → `with Value` → `Lower than`
   - 예: 100 미만인 엣지 제거 (이미 `job_network_100.net`에는 적용됨)

2. **강한 연결만 표시**
   - `Net` → `Transform` → `Extract` → `SubNetwork` → `with Value` → `Higher than`
   - 예: 200 이상인 엣지만 표시

---

## 6. 커뮤니티 탐지 및 시각화

### 6.1 커뮤니티 탐지

1. **Louvain 알고리즘**
   - `Net` → `Vector` → `Clustering` → `Louvain`
   - 네트워크를 커뮤니티로 분할합니다

2. **Modularity 최적화**
   - `Net` → `Vector` → `Clustering` → `Modularity`
   - 모듈성을 최대화하는 커뮤니티를 찾습니다

### 6.2 커뮤니티 시각화

1. **커뮤니티별 색상 지정**
   - `Draw` → `Options` → `Colors` → `Vertices` → `by Partition`
   - 같은 커뮤니티의 노드가 같은 색상으로 표시됩니다

2. **커뮤니티 레이아웃**
   - `Draw` → `Layout` → `by Partition`
   - 커뮤니티별로 노드를 그룹화하여 배치합니다

---

## 7. 중심성 분석 및 시각화

### 7.1 중심성 계산

1. **연결 중심성 (Degree Centrality)**
   - `Net` → `Vector` → `Centrality` → `Degree`
   - 연결 수가 많은 노드를 찾습니다

2. **중개 중심성 (Betweenness Centrality)**
   - `Net` → `Vector` → `Centrality` → `Betweenness`
   - 네트워크에서 중개 역할을 하는 노드를 찾습니다

3. **근접 중심성 (Closeness Centrality)**
   - `Net` → `Vector` → `Centrality` → `Closeness`
   - 다른 노드들과 가까운 노드를 찾습니다

### 7.2 중심성 시각화

1. **노드 크기로 표시**
   - `Draw` → `Options` → `Size` → `of Vertices` → `Proportional to Values`
   - 중심성이 높은 노드가 더 크게 표시됩니다

2. **노드 색상으로 표시**
   - `Draw` → `Options` → `Colors` → `Vertices` → `by Values`
   - 중심성이 높은 노드가 더 진한 색상으로 표시됩니다

---

## 8. 최종 시각화 조정

### 8.1 배경 및 전체 스타일

1. **배경 색상**
   - `Draw` → `Options` → `Colors` → `Background`
   - 흰색 또는 밝은 회색 권장

2. **그리드 표시**
   - `Draw` → `Options` → `Grid` → `Show Grid`
   - 필요시 그리드를 표시하여 정렬에 도움

### 8.2 줌 및 패닝

1. **줌 조정**
   - 마우스 휠 또는 `Draw` → `Zoom` → `In/Out`
   - 네트워크 크기에 맞게 조정

2. **패닝**
   - `Draw` → `Move` → `Pan`
   - 네트워크를 이동하여 원하는 영역을 확인

---

## 9. 이미지 저장

### 9.1 고해상도 이미지 저장

1. **이미지 내보내기**
   - `File` → `Export` → `2D` → `Bitmap` 또는 `Vector`
   - **Bitmap**: PNG, JPEG 형식
   - **Vector**: EPS, SVG 형식 (확대해도 선명함)

2. **해상도 설정**
   - `File` → `Export` → `2D` → `Bitmap`
   - 해상도 선택 (예: 300 DPI, 600 DPI)
   - 논문이나 프레젠테이션용으로는 300 DPI 이상 권장

3. **파일 형식 선택**
   - PNG: 투명 배경 지원, 고품질
   - JPEG: 작은 파일 크기, 압축
   - EPS/SVG: 벡터 형식, 무한 확대 가능

---

## 10. 추천 설정 (job_network_100.net용)

### 최적화된 설정값

1. **레이아웃**
   - `Draw` → `Energy` → `Kamada-Kawai` → `Free`
   - 반복 횟수: 100-200

2. **노드 스타일**
   - 크기: 12-15
   - 색상: 파란색 계열 (중심성 기반 그라데이션)
   - 레이블: 표시, 크기 10-12

3. **엣지 스타일**
   - 두께: 가중치에 비례 (Min=1, Max=3)
   - 색상: 회색 또는 가중치 기반 그라데이션

4. **필터링**
   - 이미 가중치 100 이상만 포함되어 있음
   - 추가 필터링 필요시: 150 이상만 표시

5. **커뮤니티 탐지**
   - `Net` → `Vector` → `Clustering` → `Louvain`
   - 커뮤니티별 색상 지정

---

## 11. 문제 해결

### 한글 깨짐 문제
- `File` → `Preferences` → `Default Text Encoding` → `UTF-8` 선택
- 파일을 다시 로드

### 노드가 겹쳐 보이는 문제
- 레이아웃을 다시 실행: `Draw` → `Energy` → `Kamada-Kawai` → `Free`
- 노드 크기를 줄이기: `Draw` → `Options` → `Size` → `of Vertices`

### 엣지가 너무 많아 보이는 문제
- 가중치 임계값을 높여 필터링
- 엣지 색상을 연하게 설정
- 엣지 두께를 줄이기

### 레이아웃이 느린 문제
- `Fruchterman-Reingold` 사용 (더 빠름)
- 반복 횟수 줄이기
- 연결되지 않은 노드 제거

---

## 12. 단축키 모음

- `Ctrl + N`: 네트워크 파일 열기
- `Ctrl + L`: 레이블 표시/숨기기
- `Ctrl + E`: 엣지 표시/숨기기
- `Ctrl + S`: 현재 설정 저장
- `Ctrl + Z`: 실행 취소
- `F5`: 레이아웃 다시 그리기

---

## 참고 자료

- Pajek 공식 웹사이트: http://mrvar.fdv.uni-lj.si/pajek/
- Pajek 매뉴얼: `Help` → `Manual` (프로그램 내장)
- 네트워크 분석 튜토리얼: Pajek 웹사이트의 예제 섹션 참조

---

**팁**: 처음에는 기본 설정으로 시작하여, 점진적으로 스타일을 조정하는 것이 좋습니다. 네트워크의 특성에 따라 최적의 설정이 달라질 수 있으므로, 여러 설정을 시도해보세요.

