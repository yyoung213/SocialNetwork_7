# Git 저장소 클론 및 브랜치 작업 가이드

## 1. 저장소 클론하기 (Clone Repository)

### 기본 명령어
```bash
git clone <저장소_URL>
```

### 설명
- **git clone**: 원격 저장소의 전체 코드와 히스토리를 로컬 환경에 복사하는 명령어입니다.
- 저장소 URL은 GitHub, GitLab 등에서 제공하는 HTTPS 또는 SSH 주소를 사용합니다.
- 예: `git clone https://github.com/username/repository.git`
- 이 명령어를 실행하면:
  - 현재 디렉토리에 저장소 이름과 동일한 폴더가 생성됩니다
  - 모든 파일과 Git 히스토리가 다운로드됩니다
  - 자동으로 원격 저장소가 'origin'이라는 이름으로 설정됩니다
  - 기본 브랜치(보통 main 또는 master)로 체크아웃됩니다

### 실행 후 작업
클론 후에는 해당 폴더로 이동해야 합니다:
```bash
cd <저장소_폴더명>
```

---

## 2. 브랜치 생성하기 (Create Branch)

### 방법 1: 새 브랜치 생성 후 전환
```bash
git checkout -b JiwonBranch
```

### 방법 2: 새 브랜치만 생성 (현재 브랜치 유지)
```bash
git branch JiwonBranch
```

### 설명
- **git checkout -b**: 새 브랜치를 생성하고 동시에 그 브랜치로 전환하는 명령어입니다.
  - `-b` 옵션: 새 브랜치 생성
  - `JiwonBranch`: 생성할 브랜치 이름
- 브랜치는 독립적인 작업 공간으로, 다른 브랜치의 작업에 영향을 주지 않습니다.
- 브랜치를 생성하면 현재 브랜치의 상태를 그대로 복사합니다.

### 현재 브랜치 확인
```bash
git branch
```
- `*` 표시가 있는 브랜치가 현재 작업 중인 브랜치입니다.

---

## 3. 작업 흐름 (Workflow)

### 3.1. 메인 브랜치의 최신 변경사항 가져오기

#### 명령어
```bash
git pull origin main
```

#### 설명
- **git pull**: 원격 저장소의 변경사항을 가져와서 현재 브랜치에 병합하는 명령어입니다.
- **origin**: 원격 저장소의 기본 이름 (clone 시 자동 설정됨)
- **main**: 가져올 원격 브랜치 이름
- 이 명령어는 다음 두 작업을 동시에 수행합니다:
  1. `git fetch origin main`: 원격 저장소의 변경사항을 로컬로 가져옴
  2. `git merge origin/main`: 가져온 변경사항을 현재 브랜치에 병합

#### 주의사항
- 현재 브랜치가 `JiwonBranch`인 상태에서 실행하면:
  - 메인 브랜치의 변경사항이 JiwonBranch에 병합됩니다
  - 충돌(conflict)이 발생할 수 있으니 주의가 필요합니다

#### 대안: 메인 브랜치로 전환 후 업데이트
```bash
# 메인 브랜치로 전환
git checkout main

# 메인 브랜치를 최신 상태로 업데이트
git pull origin main

# 다시 작업 브랜치로 돌아가기
git checkout JiwonBranch

# 메인 브랜치의 변경사항을 작업 브랜치에 병합
git merge main
```

---

### 3.2. 작업 브랜치에 변경사항 푸시하기

#### 명령어
```bash
git push origin JiwonBranch
```

#### 설명
- **git push**: 로컬 브랜치의 변경사항을 원격 저장소에 업로드하는 명령어입니다.
- **origin**: 원격 저장소 이름
- **JiwonBranch**: 푸시할 로컬 브랜치 이름
- 이 명령어를 실행하면:
  - 로컬의 JiwonBranch 브랜치가 원격 저장소에도 동일한 이름으로 생성/업데이트됩니다
  - 다른 사람들이 이 브랜치를 볼 수 있게 됩니다
  - Pull Request를 생성할 수 있게 됩니다

#### 첫 푸시 시 (브랜치가 원격에 없을 때)
```bash
git push -u origin JiwonBranch
```
- `-u` 옵션: upstream(상위 브랜치) 설정
- 이후부터는 `git push`만으로도 푸시 가능합니다

---

## 4. 전체 작업 흐름 예시

### 초기 설정 (한 번만 수행)
```bash
# 1. 저장소 클론
git clone https://github.com/username/repository.git

# 2. 저장소 폴더로 이동
cd repository

# 3. 작업 브랜치 생성 및 전환
git checkout -b JiwonBranch
```

### 일상적인 작업 흐름
```bash
# 1. 작업 전: 메인 브랜치의 최신 변경사항 가져오기
git pull origin main

# 2. 파일 수정 및 작업 수행
# ... (코드 작성, 파일 수정 등)

# 3. 변경사항 스테이징 (추가)
git add .

# 4. 커밋 생성
git commit -m "작업 내용 설명"

# 5. 원격 저장소에 푸시
git push origin JiwonBranch
```

---

## 5. 주요 Git 명령어 요약

| 명령어 | 설명 |
|--------|------|
| `git clone <URL>` | 원격 저장소를 로컬에 복사 |
| `git branch` | 브랜치 목록 확인 |
| `git checkout -b <브랜치명>` | 새 브랜치 생성 및 전환 |
| `git checkout <브랜치명>` | 브랜치 전환 |
| `git pull origin main` | 원격 main 브랜치의 변경사항 가져오기 |
| `git push origin <브랜치명>` | 로컬 브랜치를 원격에 푸시 |
| `git status` | 현재 상태 확인 |
| `git add .` | 모든 변경사항 스테이징 |
| `git commit -m "메시지"` | 커밋 생성 |
| `git log` | 커밋 히스토리 확인 |

---

## 6. 주의사항 및 팁

### 주의사항
1. **충돌(Conflict)**: `git pull origin main` 실행 시 충돌이 발생할 수 있습니다. 충돌 파일을 수동으로 해결한 후 커밋해야 합니다.
2. **브랜치 확인**: 작업 전에 `git branch`로 현재 브랜치를 확인하는 습관을 기르세요.
3. **커밋 메시지**: 의미 있는 커밋 메시지를 작성하세요.

### 권장 작업 순서
1. 작업 시작 전: `git pull origin main` (최신 변경사항 확인)
2. 작업 수행
3. `git add .` (변경사항 추가)
4. `git commit -m "작업 내용"` (커밋)
5. `git push origin JiwonBranch` (푸시)

---

## 7. 문제 해결

### 문제: "Your branch is behind 'origin/main'"
**해결**: `git pull origin main`을 실행하여 최신 변경사항을 가져옵니다.

### 문제: "Please commit your changes"
**해결**: 변경사항을 커밋하거나 `git stash`로 임시 저장 후 작업을 이어가세요.

### 문제: "Permission denied"
**해결**: GitHub 인증 설정이 필요합니다. Personal Access Token 또는 SSH 키를 설정하세요.

