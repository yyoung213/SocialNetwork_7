# Gephi에서 Bipartite Network를 지리 좌표로 시각화하기

## 개요
Bipartite 네트워크를 지리 좌표(위도/경도)를 사용하여 지도 위에 배치하는 방법입니다.

## 생성된 파일

1. **`job_skill_bipartite_2mode_geo.net`**: 지리 좌표가 설정된 Pajek 네트워크 파일
   - Post 노드: 서울 근처 (위도 37.5665°, 경도 126.9780°)
   - Skill 노드: 부산 근처 (위도 35.1796°, 경도 129.0756°)

2. **`job_skill_geo_coordinates.csv`**: Gephi Import용 CSV 파일
   - 컬럼: Id, Label, Latitude, Longitude, node_type

---

## 방법 1: .net 파일 직접 사용 (권장)

### 단계별 절차

#### 1단계: Gephi에서 네트워크 파일 열기
```
File → Open → job_skill_bipartite_2mode_geo.net
```

#### 2단계: Geo Layout 플러그인 설치 (필요 시)
```
Tools → Plugins → Available Plugins
→ "Geo Layout" 검색 및 설치
→ Gephi 재시작
```

#### 3단계: Geo Layout 적용
```
Layout → Geo Layout
```

**설정 옵션:**
- **Latitude Column**: `Y` (또는 위도가 저장된 컬럼)
- **Longitude Column**: `X` (또는 경도가 저장된 컬럼)
- **Projection**: `Mercator` (기본값) 또는 다른 투영법 선택

#### 4단계: 레이아웃 실행
```
Run 버튼 클릭
```

#### 5단계: 지도 배경 추가 (선택사항)
```
Window → Map of Countries
→ 지도 배경이 표시됩니다
```

---

## 방법 2: CSV Import 사용

### 단계별 절차

#### 1단계: 네트워크 파일 먼저 로드
```
File → Open → job_skill_bipartite_2mode.net (원본 파일)
```

#### 2단계: 지리 좌표 CSV Import
```
Data Laboratory → Import Spreadsheet
→ job_skill_geo_coordinates.csv 선택
→ Import as: Edges Table → Nodes Table로 변경
→ Next
→ Id 컬럼을 "Id"로 매핑
→ Latitude, Longitude 컬럼 확인
→ Finish
```

#### 3단계: Geo Layout 적용
```
Layout → Geo Layout
→ Latitude Column: "Latitude"
→ Longitude Column: "Longitude"
→ Run
```

---

## 좌표 설정 커스터마이징

스크립트를 수정하여 다른 지역으로 설정할 수 있습니다:

```python
# set_geo_coordinates.py 수정
set_geo_coordinates(
    input_file, 
    output_file,
    post_lat_center=37.5665,   # Post 노드 중심 위도
    post_lon_center=126.9780,  # Post 노드 중심 경도
    skill_lat_center=35.1796,  # Skill 노드 중심 위도
    skill_lon_center=129.0756, # Skill 노드 중심 경도
    spread=0.3  # 좌표 분산 범위 (±도 단위)
)
```

### 예시: 다른 지역 설정

**서울(Post) - 제주(Skill)**
```python
post_lat_center=37.5665, post_lon_center=126.9780,  # 서울
skill_lat_center=33.4996, skill_lon_center=126.5312,  # 제주
```

**서울(Post) - 대구(Skill)**
```python
post_lat_center=37.5665, post_lon_center=126.9780,  # 서울
skill_lat_center=35.8714, skill_lon_center=128.6014,  # 대구
```

---

## 주의사항

1. **좌표 순서**: Pajek .net 파일에서 좌표는 `X Y Z` 형식이며, 지리 좌표의 경우:
   - X = 경도 (Longitude)
   - Y = 위도 (Latitude)

2. **좌표 범위**:
   - 위도: -90° ~ +90° (남극 ~ 북극)
   - 경도: -180° ~ +180° (서경 ~ 동경)

3. **한국 좌표 범위**:
   - 위도: 약 33° ~ 38.5°
   - 경도: 약 124° ~ 132°

4. **분산(spread) 설정**: 너무 크면 노드들이 지도 밖으로 나갈 수 있습니다.

---

## 시각화 팁

1. **Partition으로 색상 구분**:
   ```
   Partition → node_type 선택
   → Post와 Skill을 다른 색상으로 표시
   ```

2. **노드 크기 조정**:
   ```
   Appearance → Nodes → Size
   → Degree 또는 다른 메트릭으로 크기 설정
   ```

3. **엣지 스타일**:
   ```
   Appearance → Edges → Color
   → 단색 또는 그라데이션 설정
   ```

4. **레이블 표시**:
   ```
   Preview → Show Labels
   → 노드 이름 표시
   ```

---

## 문제 해결

### 문제: Geo Layout이 작동하지 않음
- **해결**: 플러그인이 설치되어 있는지 확인
- **해결**: 좌표 컬럼 이름이 올바른지 확인 (X=경도, Y=위도)

### 문제: 노드들이 지도 밖에 있음
- **해결**: 좌표 범위 확인 (한국: 위도 33~38.5°, 경도 124~132°)
- **해결**: spread 값을 줄여서 좌표 분산 범위 축소

### 문제: CSV Import 시 좌표가 인식되지 않음
- **해결**: CSV 파일의 컬럼 이름 확인 (Latitude, Longitude)
- **해결**: 숫자 형식 확인 (소수점 포함)

---

## 참고 자료

- Gephi Geo Layout 플러그인: https://gephi.org/plugins/
- Pajek 파일 형식: http://vlado.fmf.uni-lj.si/pub/networks/pajek/
- 지리 좌표계: WGS84 (GPS에서 사용하는 표준 좌표계)





