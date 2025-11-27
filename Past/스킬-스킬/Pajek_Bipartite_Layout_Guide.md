# Pajek에서 Bipartite 네트워크 두 그룹 정렬 가이드

## 개요
Bipartite 네트워크에서 두 타입의 노드(기업과 스킬)를 각각 정렬된 형태로 배치하는 방법을 설명합니다.

---

## 방법 1: 2-Mode Partition을 사용한 자동 정렬 (권장)

### 단계별 절차

#### 1단계: 네트워크 및 Partition 파일 로드
```
1. File → Network → Read
   → bipartite_skill_network.net 선택

2. File → Partition → Read
   → bipartite_skill_network.clu 선택
```

#### 2단계: 2-Mode Partition 생성
```
1. Net → Partition → 2-Mode
   → 이 명령은 네트워크를 두 개의 모드로 자동 분할합니다
   → 첫 번째 모드(기업): partition 값 1
   → 두 번째 모드(스킬): partition 값 2
```

**참고**: 이미 `.clu` 파일이 있다면 이 단계는 생략 가능합니다.

#### 3단계: Bipartite 레이아웃 적용
```
1. Draw → Network → Draw-Partition
   → Partition 파일을 기반으로 네트워크를 그립니다

2. Draw → Layout → Energy → Bipartite
   → 또는 Draw → Layout → Bipartite
   → 두 그룹을 자동으로 분리하여 배치합니다
```

#### 4단계: 레이아웃 조정 (선택사항)
```
1. Draw → Energy → Kamada-Kawai → Bipartite
   → Bipartite 모드로 Energy 레이아웃 적용
   → 두 그룹이 각각 정렬된 형태로 배치됩니다

2. Draw → Energy → Fruchterman-Reingold → Bipartite
   → 더 빠른 계산, 큰 네트워크에 적합
```

---

## 방법 2: 수동 좌표 설정을 통한 정렬

### 단계별 절차

#### 1단계: Partition 파일 확인
```
- Partition 파일(.clu)이 로드되어 있어야 합니다
- 기업 노드: partition 값 1
- 스킬 노드: partition 값 2
```

#### 2단계: 좌표 파일 생성 (Python 스크립트 사용)

Python 스크립트로 좌표 파일을 생성할 수 있습니다:

```python
# create_bipartite_coordinates.py
# 기업 노드를 왼쪽에, 스킬 노드를 오른쪽에 배치

def create_coordinates_file(partition_file, output_file):
    # Partition 파일 읽기
    with open(partition_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    num_vertices = int(lines[0].split()[-1])
    
    # 좌표 생성
    company_nodes = []
    skill_nodes = []
    
    for i in range(1, num_vertices + 1):
        partition_value = int(lines[i].strip())
        if partition_value == 1:  # 기업
            company_nodes.append(i)
        else:  # 스킬
            skill_nodes.append(i)
    
    # 좌표 파일 작성
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"*Vertices {num_vertices}\n")
        
        # 기업 노드: X=0, Y는 균등 분배
        num_companies = len(company_nodes)
        for idx, node_id in enumerate(company_nodes):
            y = (idx + 1) / (num_companies + 1)  # 0~1 사이 값
            f.write(f"0 {y}\n")
        
        # 스킬 노드: X=1, Y는 균등 분배
        num_skills = len(skill_nodes)
        for idx, node_id in enumerate(skill_nodes):
            y = (idx + 1) / (num_skills + 1)  # 0~1 사이 값
            f.write(f"1 {y}\n")
```

#### 3단계: 좌표 파일 로드
```
1. File → Network → Read → bipartite_skill_network.net
2. File → Partition → Read → bipartite_skill_network.clu
3. File → Network → Read Coordinates → bipartite_coordinates.coord
   → 또는 File → Network → Read → bipartite_skill_network.net (좌표 포함)
```

#### 4단계: 네트워크 그리기
```
Draw → Network
→ 또는 Draw → Network → Draw-Partition
```

---

## 방법 3: Energy 레이아웃과 Partition 조합

### 단계별 절차

#### 1단계: 기본 설정
```
1. File → Network → Read → bipartite_skill_network.net
2. File → Partition → Read → bipartite_skill_network.clu
```

#### 2단계: Energy 레이아웃 적용 (Bipartite 모드)
```
1. Draw → Energy → Kamada-Kawai → Bipartite
   → 또는 Draw → Energy → Fruchterman-Reingold → Bipartition
   
2. 옵션 설정:
   - Iterations: 100-500 (네트워크 크기에 따라)
   - Temperature: 기본값 사용
```

#### 3단계: 레이아웃 조정
```
1. Draw → Move → Move
   → 마우스로 노드를 드래그하여 미세 조정

2. Draw → Move → Move X/Y
   → X 또는 Y 좌표만 조정
```

---

## 방법 4: Pajek 매크로를 사용한 자동 정렬

### 매크로 스크립트 예제

Pajek 매크로 파일(`bipartite_layout.mcr`) 생성:

```
*Network bipartite_skill_network.net
*Partition bipartite_skill_network.clu
*Draw-Partition
*Energy Kamada-Kawai Bipartite
*Draw
```

### 매크로 실행
```
File → Macro → Run → bipartite_layout.mcr
```

---

## 고급 기법: 그룹별 정렬 개선

### 1. 그룹 내 노드 정렬 (Degree 기반)

```
1. Net → Vector → Centrality → Degree
   → 각 노드의 degree 계산

2. Net → Partition → Create → by Values → Vector
   → Degree 값에 따라 그룹 내에서 정렬

3. Draw → Layout → Energy → Bipartite
   → 정렬된 상태로 레이아웃 적용
```

### 2. 그룹 간 거리 조정

```
1. Draw → Options → Layout → Bipartite Distance
   → 두 그룹 간의 거리 설정
   → 기본값: 1.0
   → 증가: 그룹 간 거리 증가
   → 감소: 그룹 간 거리 감소
```

### 3. 수직/수평 정렬 선택

```
1. Draw → Layout → Bipartite → Horizontal
   → 두 그룹을 수평으로 배치 (왼쪽/오른쪽)

2. Draw → Layout → Bipartite → Vertical
   → 두 그룹을 수직으로 배치 (위/아래)
```

---

## 문제 해결

### 문제 1: 노드가 겹쳐 보임
**해결책**:
```
1. Draw → Options → Size → of Vertices
   → 노드 크기 줄이기 (5-10)

2. Draw → Energy → Kamada-Kawai → Bipartite
   → 레이아웃 재계산
```

### 문제 2: 두 그룹이 명확히 분리되지 않음
**해결책**:
```
1. Net → Partition → 2-Mode
   → 2-Mode partition 재생성

2. Draw → Layout → Bipartite → Force Separation
   → 그룹 간 강제 분리
```

### 문제 3: 레이아웃이 느림
**해결책**:
```
1. Draw → Energy → Fruchterman-Reingold → Bipartite
   → 더 빠른 알고리즘 사용

2. Net → Transform → Remove → Isolated Vertices
   → 고립된 노드 제거 (성능 향상)
```

---

## 추천 워크플로우

### 빠른 정렬 (작은 네트워크)
```
1. File → Network → Read → bipartite_skill_network.net
2. File → Partition → Read → bipartite_skill_network.clu
3. Draw → Network → Draw-Partition
4. Draw → Energy → Kamada-Kawai → Bipartite
```

### 정밀한 정렬 (큰 네트워크)
```
1. File → Network → Read → bipartite_skill_network.net
2. File → Partition → Read → bipartite_skill_network.clu
3. Net → Partition → 2-Mode (확인)
4. Draw → Energy → Fruchterman-Reingold → Bipartite
5. Draw → Options → Layout → Bipartite Distance → 1.5
6. Draw → Move → Move (필요시 수동 조정)
```

---

## 추가 팁

### 1. 색상으로 그룹 구분
```
1. File → Partition → Read → bipartite_skill_network.clu
2. Draw → Options → Colors → Vertices → by Partition
   → 기업: 파란색, 스킬: 빨간색 등으로 구분
```

### 2. 레이블 표시
```
1. Draw → Options → Labels → Show Labels
2. Draw → Options → Labels → Size → 8-10
   → 큰 네트워크에서는 작은 크기 권장
```

### 3. 엣지 스타일
```
1. Draw → Options → Colors → Lines → Gray
   → 엣지 색상을 회색으로 설정 (가독성 향상)

2. Draw → Options → Size → of Lines → 0.5
   → 엣지 두께 줄이기
```

---

## 참고사항

- **Pajek 버전**: Pajek 5.x 이상에서 Bipartite 레이아웃 기능이 개선되었습니다
- **네트워크 크기**: 2000개 이상의 노드가 있는 경우 레이아웃 계산에 시간이 걸릴 수 있습니다
- **메모리**: 큰 네트워크의 경우 충분한 메모리가 필요합니다

---

## 예제 파일

현재 디렉토리에 다음 파일들이 있습니다:
- `bipartite_skill_network.net` - 네트워크 파일
- `bipartite_skill_network.clu` - Partition 파일 (기업=1, 스킬=2)
- `bipartite_skill_network.vec` - Vector 파일 (degree 정보)

이 파일들을 사용하여 위의 방법들을 시도해보세요!

