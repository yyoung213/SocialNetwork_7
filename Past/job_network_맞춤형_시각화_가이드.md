# job_network.net 맞춤형 시각화 가이드 (Pajek 64 6.01 버전)

## 📊 네트워크 특성 분석

### 기본 통계
- **노드 수**: 39개 (모든 직군)
- **엣지 수**: 740개
- **네트워크 밀도**: 매우 높음 (거의 완전 그래프)
- **평균 연결 수**: 37.95개 (거의 모든 노드와 연결)
- **연결되지 않은 노드**: 0개

### 가중치 분석
- **가중치 범위**: 1 - 602
- **평균 가중치**: 102.77
- **중앙값 가중치**: 74
- **가중치 분포**:
  - 가중치 ≥ 100: 282개 (38.1%)
  - 가중치 ≥ 200: 92개 (12.4%)
  - 가중치 ≥ 300: 41개 (5.5%)
  - 가중치 ≥ 400: 20개 (2.7%)
  - 가중치 ≥ 500: 5개 (0.7%)

### 네트워크 특징
1. **매우 밀집된 네트워크**: 모든 직군이 거의 모든 직군과 연결됨
2. **가중치 차이가 큼**: 약한 연결(1)부터 매우 강한 연결(602)까지 다양
3. **균등한 연결성**: 대부분의 노드가 37-38개 연결을 가짐
4. **중개 중심성 낮음**: 모든 노드가 직접 연결되어 있어 중개 역할이 거의 없음

---

## 🎯 최적화된 시각화 전략

### 핵심 목표
이 네트워크는 **매우 밀집되어 있고 엣지가 많아** 가독성을 높이기 위해서는:
1. **가중치 기반 필터링**이 필수적
2. **엣지 스타일 최적화**로 시각적 혼잡 완화
3. **레이아웃 알고리즘 선택**이 중요
4. **노드 그룹화**로 구조 파악 용이

---

## 📋 단계별 시각화 가이드

### 1단계: 파일 로드 및 기본 설정

#### 1.1 파일 열기
```
File → Network → Read
→ job_network.net 선택
→ 또는 단축키: Ctrl + N
```

**Pajek 6.01 특징**:
- 파일 대화상자에서 `job_network.net` 선택
- 파일이 로드되면 하단 상태바에 정보 표시

#### 1.2 인코딩 설정 (한글 지원)
```
File → Options → Default Text Encoding
→ UTF-8 선택
→ 파일 다시 로드 (Ctrl + N)
```

**참고**: Pajek 6.01에서는 `Preferences` 대신 `Options` 메뉴 사용

#### 1.3 초기 확인
- 하단 상태바 확인: "39 vertices, 740 edges" 표시 확인
- 메인 창에 네트워크 정보 표시됨

---

### 2단계: 가중치 기반 필터링 (필수!)

#### 2.1 약한 연결 제거
**추천: 가중치 50 미만 제거**
```
Net → Transform → Remove → Lines
→ with Value → Lower than
→ 값 입력: 50
→ OK
```
- 결과: 약 200-250개 엣지로 감소 (가독성 향상)

**또는 더 강한 필터링: 가중치 100 미만 제거**
```
Net → Transform → Remove → Lines
→ with Value → Lower than
→ 값 입력: 100
→ OK
```
- 결과: 282개 엣지만 표시 (job_network_100.net과 유사)

**Pajek 6.01 팁**:
- 필터링 후 `Draw → Draw` 또는 `Ctrl + D`로 다시 그리기
- 필터링 전 원본을 저장하려면 `File → Network → Save`로 백업

#### 2.2 매우 강한 연결만 표시 (선택)
**가중치 200 이상만 표시**
```
Net → Transform → Extract → SubNetwork
→ with Value → Higher than
→ 값 입력: 200
→ OK
```
- 결과: 92개 엣지만 표시 (핵심 연결만)

**또는 가중치 범위 지정**:
```
Net → Transform → Extract → SubNetwork
→ with Value → Between
→ 최소값: 200, 최대값: 602
→ OK
```

---

### 3단계: 레이아웃 설정

#### 3.1 추천 레이아웃: Kamada-Kawai
**이유**: 밀집된 네트워크에서 균등한 노드 배치에 최적

```
Draw → Energy → Kamada-Kawai → Free
→ 또는 Draw → Energy → Kamada-Kawai → Fixed
```

**Pajek 6.01 설정 조정**:
- 대화상자에서 반복 횟수 입력: 200-300
- `Free` 모드: 자유 배치 (추천)
- `Fixed` 모드: 일부 노드 고정 후 배치

**팁**: 
- 레이아웃 계산 중 진행 상황 표시
- 완료되면 자동으로 그려짐

#### 3.2 대안: Fruchterman-Reingold
**이유**: 더 빠른 계산, 큰 네트워크에 적합

```
Draw → Energy → Fruchterman-Reingold → Free
```

**Pajek 6.01 설정 조정**:
- 대화상자에서 반복 횟수 입력: 100-150
- 온도 파라미터: 1.0-2.0 (기본값 사용 가능)

#### 3.3 기타 레이아웃 옵션
**Circular Layout** (원형 배치):
```
Draw → Layout → Circular
```
- 작은 네트워크에 적합
- 39개 노드에 적합한 크기

**Hierarchical Layout** (계층적 배치):
```
Draw → Layout → Hierarchical
```
- 계층 구조가 있는 경우 사용

#### 3.4 레이아웃 최적화 팁
1. **여러 번 실행**: 레이아웃이 마음에 들지 않으면 다시 실행
2. **수동 조정**: 
   - `Draw → Move → Move`로 개별 노드 위치 조정
   - 또는 마우스로 직접 드래그 (Pajek 6.01에서 지원)
3. **커뮤니티 기반 배치**: 커뮤니티 탐지 후 그룹별 배치
4. **레이아웃 저장**: `File → Network → Save`로 레이아웃 정보 저장

---

### 4단계: 엣지 스타일 최적화 (매우 중요!)

#### 4.1 엣지 두께 설정
**가중치에 비례한 두께 (필수)**

```
Draw → Options → Size → of Lines
→ Proportional to Values 선택
→ Min: 0.5 입력
→ Max: 3.0 입력
→ OK
```

**Pajek 6.01 특징**:
- 대화상자에서 직접 값 입력
- `Fixed` 옵션: 모든 엣지 동일 두께
- `Proportional to Values`: 가중치에 비례 (추천)

**이유**: 
- 가중치 차이가 크므로(1-602) 두께 차이를 명확히 표시
- 너무 두꺼우면 시각적 혼잡 증가

#### 4.2 엣지 색상 설정
**옵션 1: 가중치 기반 그라데이션 (추천)**
```
Draw → Options → Colors → Lines
→ by Values 선택
→ 색상 범위 설정: 회색 → 파란색
→ OK
```

**Pajek 6.01 색상 설정**:
- 색상 팔레트에서 시작 색상과 끝 색상 선택
- 그라데이션 자동 적용

**옵션 2: 가중치 구간별 색상**
```
Draw → Options → Colors → Lines
→ by Partition 선택
```
- 먼저 가중치 구간별로 Partition 생성 필요
- 각 구간을 다른 색상으로 지정

**옵션 3: 단일 색상**
```
Draw → Options → Colors → Lines
→ Fixed 선택
→ 색상: 회색 또는 검은색
```

#### 4.3 엣지 스타일 추가 설정
**엣지 표시/숨기기**:
```
Draw → Options → Lines → Show Lines
→ 체크/해제로 표시 제어
```

**엣지 스타일**:
```
Draw → Options → Lines → Style
→ Solid (실선) 또는 Dashed (점선) 선택
```

---

### 5단계: 노드 스타일 설정

#### 5.1 노드 크기
**균등한 크기 (추천)**
```
Draw → Options → Size → of Vertices
→ Fixed 선택
→ 값 입력: 12-15
→ OK
```

**가중치 중심성 기반 크기 (선택)**:
```
1. 먼저 중심성 계산: Net → Vector → Centrality → Weighted Degree
2. Draw → Options → Size → of Vertices
   → Proportional to Values 선택
   → OK
```

**이유**: 
- 모든 노드의 연결 수가 비슷함 (37-38개)
- 중심성 기반 크기 조정의 효과가 미미하지만, 가중치 중심성은 의미있을 수 있음

#### 5.2 노드 색상
**옵션 1: 단일 색상 (추천)**
```
Draw → Options → Colors → Vertices
→ Fixed 선택
→ 색상: 파란색 또는 회색 선택
→ OK
```

**옵션 2: 커뮤니티별 색상**
```
1. 먼저 커뮤니티 탐지 수행 (6단계 참조)
2. Draw → Options → Colors → Vertices
   → by Partition 선택
   → OK
```
- 같은 커뮤니티는 같은 색상으로 자동 지정

**옵션 3: 중심성 기반 색상**
```
1. 중심성 계산: Net → Vector → Centrality → Weighted Degree
2. Draw → Options → Colors → Vertices
   → by Values 선택
   → 색상 범위 설정 (연한 → 진한)
   → OK
```

#### 5.3 노드 레이블
**레이블 표시 (필수)**
```
Draw → Options → Labels → Show Labels
→ 또는 단축키: Ctrl + L
→ 체크박스로 표시/숨기기
```

**레이블 크기**:
```
Draw → Options → Labels → Size
→ 값 입력: 10-12 (39개 노드에 적합)
→ OK
```

**레이블 위치**:
```
Draw → Options → Labels → Position
→ Below (노드 아래) 선택
→ 또는 Above, Left, Right 선택
```

**레이블 색상**:
```
Draw → Options → Labels → Color
→ 검은색 또는 진한 회색 선택
→ 배경과 대비되도록 설정
```

**Pajek 6.01 레이블 팁**:
- 레이블이 겹치면 자동으로 조정되지 않으므로 수동 조정 필요
- `Draw → Move → Move`로 노드 위치 조정하여 레이블 겹침 방지

---

### 6단계: 커뮤니티 탐지 및 그룹화

#### 6.1 커뮤니티 탐지
**Louvain 알고리즘 (추천)**
```
Net → Vector → Clustering → Louvain
→ 대화상자에서 파라미터 설정 (기본값 사용 가능)
→ OK
```

**Pajek 6.01 결과 확인**:
- Partition 파일이 생성됨
- `Info → Partition`에서 커뮤니티 개수 확인
- 일반적으로 3-5개 커뮤니티 예상

**다른 알고리즘 옵션**:
- **Modularity**: `Net → Vector → Clustering → Modularity`
- **Walktrap**: `Net → Vector → Clustering → Walktrap`

#### 6.2 커뮤니티별 색상 지정
```
Draw → Options → Colors → Vertices
→ by Partition 선택
→ OK
```

**Pajek 6.01 특징**:
- 자동으로 각 커뮤니티에 다른 색상 할당
- 색상 팔레트에서 색상 변경 가능

#### 6.3 커뮤니티 기반 레이아웃
```
Draw → Layout → by Partition
→ 또는 Draw → Layout → Circular by Partition
```

**이유**: 같은 커뮤니티의 노드를 가까이 배치하여 구조 파악 용이

**Pajek 6.01 추가 옵션**:
- `Circular by Partition`: 각 커뮤니티를 원형으로 배치
- `Hierarchical by Partition`: 계층적 배치

---

### 7단계: 중심성 분석 및 시각화

#### 7.1 연결 중심성 계산
```
Net → Vector → Centrality → Degree
→ OK
```

**Pajek 6.01 결과 확인**:
- Vector 파일이 생성됨
- `Info → Vector`에서 중심성 값 확인
- 대부분의 노드가 비슷한 중심성 (네트워크 특성상)

#### 7.2 가중치 중심성 계산 (더 유용)
```
Net → Vector → Centrality → Weighted Degree
→ OK
```

**이유**: 가중치를 고려한 중심성이 더 의미있음

**Pajek 6.01 추가 중심성 옵션**:
- **Betweenness**: `Net → Vector → Centrality → Betweenness`
- **Closeness**: `Net → Vector → Centrality → Closeness`
- **Eigenvector**: `Net → Vector → Centrality → Eigenvector`

#### 7.3 중심성 시각화
**노드 크기로 표시**:
```
1. 중심성 Vector가 활성화되어 있는지 확인
2. Draw → Options → Size → of Vertices
   → Proportional to Values 선택
   → Min, Max 값 조정 (선택)
   → OK
```

**노드 색상으로 표시**:
```
1. 중심성 Vector가 활성화되어 있는지 확인
2. Draw → Options → Colors → Vertices
   → by Values 선택
   → 색상 범위 설정 (연한 → 진한)
   → OK
```

**Pajek 6.01 팁**:
- Vector 파일이 활성화되어 있어야 `by Values` 옵션 사용 가능
- `File → Vector → Read`로 Vector 파일 로드 가능

---

### 8단계: 최종 조정 및 최적화

#### 8.1 배경 설정
```
Draw → Options → Colors → Background
→ 색상 선택: 흰색 또는 밝은 회색
→ OK
```

**Pajek 6.01 추가 옵션**:
- 배경 이미지 추가 가능 (선택)
- 투명도 조정 가능

#### 8.2 그리드 및 축 설정
```
Draw → Options → Grid
→ Show Grid 체크 해제 (그리드 숨기기)
→ Show Axes 체크 해제 (축 숨기기)
```

**Pajek 6.01 특징**:
- 그리드와 축을 개별적으로 제어 가능
- 필요시 표시하여 정렬에 도움

#### 8.3 줌 및 패닝 조정
**줌 조정**:
- 마우스 휠로 줌 인/아웃
- 또는 `Draw → Zoom → In/Out`
- 전체 네트워크가 화면에 보이도록 조정

**패닝 (이동)**:
- `Draw → Move → Pan`
- 또는 마우스 드래그 (일부 모드에서)

**Pajek 6.01 팁**:
- `View → Fit to Window`로 전체 네트워크를 화면에 맞춤

#### 8.4 개별 노드 위치 조정
```
Draw → Move → Move
→ 마우스로 드래그하여 노드 위치 조정
→ 또는 Draw → Move → Move X/Y (축별 이동)
```

**Pajek 6.01 추가 기능**:
- 여러 노드 선택 후 일괄 이동 가능
- `Draw → Move → Align`으로 정렬

**팁**: 
- 레이블이 겹치지 않도록 조정
- 중요한 노드는 중앙에 배치
- 커뮤니티별로 그룹화하여 배치

---

## 🎨 추천 시각화 설정 (단계별)

### 설정 A: 전체 네트워크 보기 (가중치 50 이상)

1. **필터링**: 가중치 50 미만 제거
2. **레이아웃**: Kamada-Kawai (반복 200)
3. **노드**: 크기 12, 파란색, 레이블 표시
4. **엣지**: 가중치 비례 두께 (0.5-3.0), 가중치 기반 색상
5. **결과**: 약 500개 엣지, 전체 구조 파악

### 설정 B: 강한 연결 중심 (가중치 100 이상)

1. **필터링**: 가중치 100 미만 제거
2. **레이아웃**: Kamada-Kawai (반복 300)
3. **노드**: 크기 15, 커뮤니티별 색상, 레이블 표시
4. **엣지**: 가중치 비례 두께 (1.0-4.0), 진한 색상
5. **결과**: 282개 엣지, 핵심 연결 강조

### 설정 C: 매우 강한 연결만 (가중치 200 이상)

1. **필터링**: 가중치 200 미만 제거
2. **레이아웃**: Fruchterman-Reingold (반복 150)
3. **노드**: 크기 18, 커뮤니티별 색상, 레이블 표시
4. **엣지**: 가중치 비례 두께 (2.0-5.0), 진한 색상
5. **결과**: 92개 엣지, 최강 연결만 표시

### 설정 D: 커뮤니티 중심 시각화

1. **커뮤니티 탐지**: Louvain 알고리즘
2. **필터링**: 가중치 100 이상
3. **레이아웃**: 커뮤니티 기반 배치
4. **노드**: 커뮤니티별 색상, 크기 15
5. **엣지**: 커뮤니티 내부는 진하게, 외부는 연하게
6. **결과**: 그룹 구조 명확히 표시

---

## ⚠️ 주의사항 및 문제 해결

### 문제 1: 엣지가 너무 많아 보임
**해결책**:
- 가중치 임계값을 높여 필터링 (50 → 100 → 200)
- 엣지 투명도 조정 (0.3-0.5)
- 엣지 두께 줄이기 (Max: 2.0)

### 문제 2: 노드 레이블이 겹침
**해결책**:
- 레이블 크기 줄이기 (10-12)
- 레이블 위치 조정 (Below → Above)
- 수동으로 노드 위치 조정

### 문제 3: 레이아웃이 마음에 들지 않음
**해결책**:
- 레이아웃 알고리즘 변경 (Kamada-Kawai ↔ Fruchterman-Reingold)
- 반복 횟수 증가 (200 → 300)
- 여러 번 실행하여 최적 결과 선택

### 문제 4: 한글 레이블이 깨짐
**해결책**:
- `File → Options → Default Text Encoding → UTF-8`
- 파일 다시 로드 (Ctrl + N)
- Pajek 6.01 버전에서는 UTF-8 기본 지원
- 여전히 깨지면 파일을 UTF-8 BOM 없이 저장

**Pajek 6.01 한글 지원**:
- UTF-8 인코딩 자동 인식
- 한글 폰트가 설치되어 있어야 정상 표시
- Windows에서 기본 한글 폰트 사용

### 문제 5: 가중치 차이가 잘 안 보임
**해결책**:
- 엣지 두께 범위 확대 (Min: 0.5, Max: 5.0)
- 가중치 기반 색상 그라데이션 사용
- 가중치 구간별 색상 지정

---

## 📊 분석 팁

### 1. 가중치 분포 확인
- 가중치 100 이상: 38.1% (핵심 연결)
- 가중치 200 이상: 12.4% (매우 강한 연결)
- 가중치 500 이상: 0.7% (최강 연결)

### 2. 네트워크 구조 특징
- **완전 그래프에 가까움**: 모든 직군이 거의 모든 직군과 연결
- **가중치 차이가 핵심**: 연결 여부보다 연결 강도가 중요
- **균등한 연결성**: 특정 노드가 과도하게 중심적이지 않음

### 3. 시각화 전략
- **필터링 필수**: 가중치 기반 필터링 없이는 가독성 낮음
- **엣지 스타일 중요**: 노드보다 엣지 스타일이 더 중요
- **커뮤니티 탐지 유용**: 그룹 구조 파악에 도움

---

## 💾 이미지 저장

### 고해상도 저장
```
File → Export → 2D → Bitmap
→ 또는 File → Export → Image
→ 해상도 선택: 300 DPI (논문용) 또는 600 DPI (프레젠테이션용)
→ 형식 선택: PNG (투명 배경) 또는 JPEG
→ 파일명 입력 및 저장
```

**Pajek 6.01 저장 옵션**:
- PNG: 투명 배경 지원, 고품질
- JPEG: 작은 파일 크기, 압축
- BMP: 비압축, 큰 파일 크기

### 벡터 형식 저장
```
File → Export → 2D → Vector
→ 또는 File → Export → EPS/SVG
→ 형식 선택: EPS 또는 SVG
→ 파일명 입력 및 저장
```

**Pajek 6.01 벡터 형식 특징**:
- EPS: 인쇄용, Adobe Illustrator 호환
- SVG: 웹용, 브라우저에서 직접 보기 가능
- 무한 확대 가능, 선명함

### 추가 저장 옵션
**네트워크 파일 저장** (레이아웃 포함):
```
File → Network → Save
→ .net 형식으로 저장 (레이아웃 좌표 포함)
```

**설정 저장**:
```
File → Options → Save Settings
→ 현재 설정을 저장하여 나중에 재사용
```

---

## 🔄 워크플로우 요약 (Pajek 6.01)

1. **파일 로드** 
   - `File → Network → Read` (Ctrl + N)
   - `File → Options → Default Text Encoding → UTF-8` 설정

2. **필터링** 
   - `Net → Transform → Remove → Lines → with Value → Lower than`
   - 가중치 50 또는 100 미만 제거

3. **레이아웃** 
   - `Draw → Energy → Kamada-Kawai → Free`
   - 반복 횟수 200-300 설정

4. **엣지 스타일** 
   - `Draw → Options → Size → of Lines → Proportional to Values`
   - `Draw → Options → Colors → Lines → by Values`

5. **노드 스타일** 
   - `Draw → Options → Size → of Vertices → Fixed (12-15)`
   - `Draw → Options → Labels → Show Labels` (Ctrl + L)

6. **커뮤니티 탐지** (선택)
   - `Net → Vector → Clustering → Louvain`
   - `Draw → Options → Colors → Vertices → by Partition`

7. **최종 조정** 
   - `Draw → Move → Move`로 수동 위치 조정
   - `View → Fit to Window`로 전체 보기

8. **저장** 
   - `File → Export → 2D → Bitmap` (고해상도)
   - 또는 `File → Export → 2D → Vector` (벡터 형식)

## ⌨️ Pajek 6.01 주요 단축키

- `Ctrl + N`: 네트워크 파일 열기
- `Ctrl + D`: 네트워크 그리기
- `Ctrl + L`: 레이블 표시/숨기기
- `Ctrl + S`: 현재 설정 저장
- `Ctrl + Z`: 실행 취소
- `F5`: 다시 그리기

---

## 📈 예상 결과

### 가중치 50 이상 필터링 시
- 엣지 수: 약 500개
- 가독성: ⭐⭐⭐⭐ (좋음)
- 전체 구조 파악: 가능

### 가중치 100 이상 필터링 시
- 엣지 수: 282개
- 가독성: ⭐⭐⭐⭐⭐ (매우 좋음)
- 핵심 연결 강조: 명확

### 가중치 200 이상 필터링 시
- 엣지 수: 92개
- 가독성: ⭐⭐⭐⭐⭐ (완벽)
- 최강 연결만 표시: 매우 명확

---

**최종 추천**: 가중치 100 이상 필터링 + Kamada-Kawai 레이아웃 + 가중치 비례 엣지 스타일이 가장 균형잡힌 시각화입니다.

