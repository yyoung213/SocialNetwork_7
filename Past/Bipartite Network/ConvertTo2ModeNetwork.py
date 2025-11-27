"""
bipartite_skill_long.csv를 Pajek 2-Mode 네트워크 형식으로 변환하는 스크립트
ex_2mode.net 파일의 형식을 참고하여 변환합니다.

Pajek 2-Mode 네트워크 형식:
*Vertices    N1    N2
1 "노드명" x y z
...
*Edges
노드1 노드2 가중치
...

여기서:
- N1: 첫 번째 모드의 노드 수 (기업)
- N2: 두 번째 모드의 노드 수 (스킬)
- 첫 번째 모드 노드: 1부터 N1까지
- 두 번째 모드 노드: N1+1부터 N1+N2까지
"""

import pandas as pd
import os


def convert_csv_to_2mode_network(csv_file: str = 'bipartite_skill_long.csv',
                                 reference_file: str = 'ex_2mode.net',
                                 output_file: str = 'bipartite_skill_2mode.net'):
    """
    CSV 파일을 Pajek 2-Mode 네트워크 형식으로 변환합니다.
    
    Args:
        csv_file (str): 입력 CSV 파일 경로
        reference_file (str): 참고할 예제 .net 파일 경로
        output_file (str): 출력 .net 파일 경로
    """
    print("=" * 60)
    print("CSV → Pajek 2-Mode Network 변환")
    print("=" * 60)
    
    # 참고 파일 형식 확인
    print(f"\n참고 파일 형식 확인: {reference_file}")
    with open(reference_file, 'r', encoding='utf-8') as f:
        ref_lines = f.readlines()
        if ref_lines:
            vertices_line = ref_lines[0]
            print(f"  참고 형식: {vertices_line.strip()}")
            # *Vertices    N1    N2 형식 확인
    
    # CSV 파일 읽기
    print(f"\nCSV 파일 읽기: {csv_file}")
    df = pd.read_csv(csv_file)
    
    print(f"  총 행 수: {len(df):,}개")
    
    # 고유한 기업과 스킬 추출
    unique_companies = sorted(df['기업명'].unique())
    unique_skills = sorted(df['Skill'].unique())
    
    n1 = len(unique_companies)  # 첫 번째 모드 (기업)
    n2 = len(unique_skills)     # 두 번째 모드 (스킬)
    total_nodes = n1 + n2
    
    print(f"  기업 수 (모드 1): {n1:,}개")
    print(f"  스킬 수 (모드 2): {n2:,}개")
    print(f"  총 노드 수: {total_nodes:,}개")
    
    # 노드 ID 매핑 생성
    # 기업: 1부터 n1까지
    company_to_id = {company: idx + 1 for idx, company in enumerate(unique_companies)}
    # 스킬: n1+1부터 n1+n2까지
    skill_to_id = {skill: idx + 1 + n1 for idx, skill in enumerate(unique_skills)}
    
    # 엣지 수 계산
    edge_count = len(df)
    print(f"  엣지 수: {edge_count:,}개")
    
    # 2-Mode 네트워크 파일 작성
    print(f"\n2-Mode 네트워크 파일 생성 중: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Vertices 헤더: *Vertices    N1    N2
        f.write(f"*Vertices    {n1}    {n2}\n")
        
        # 기업 노드 추가 (모드 1)
        # 형식: 노드번호 "레이블" x y z
        # 좌표는 기본값으로 설정 (0.5, 0.5, 0.5) 또는 나중에 레이아웃으로 조정
        for company in unique_companies:
            company_id = company_to_id[company]
            label_escaped = str(company).replace('"', '\\"')
            # 기본 좌표 (나중에 레이아웃으로 조정 가능)
            f.write(f'{company_id:6d} "{label_escaped}" 0.0000 0.0000 0.5000\n')
        
        # 스킬 노드 추가 (모드 2)
        for skill in unique_skills:
            skill_id = skill_to_id[skill]
            label_escaped = str(skill).replace('"', '\\"')
            # 기본 좌표
            f.write(f'{skill_id:6d} "{label_escaped}" 1.0000 0.0000 0.5000\n')
        
        # Edges 섹션
        f.write(f"*Edges\n")
        
        # 엣지 추가
        for _, row in df.iterrows():
            company = row['기업명']
            skill = row['Skill']
            
            company_id = company_to_id[company]
            skill_id = skill_to_id[skill]
            
            # 가중치 1로 저장
            f.write(f"{company_id:6d} {skill_id:6d}       1\n")
    
    print(f"  ✓ 2-Mode 네트워크 파일 생성 완료")
    
    # 검증
    print(f"\n검증 중...")
    with open(output_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"  파일 총 줄 수: {len(lines):,}줄")
    print(f"  Vertices 헤더: {lines[0].strip()}")
    
    # 샘플 출력
    print(f"\n  샘플 노드 정의 (처음 3개 기업):")
    for i in range(1, 4):
        if i < len(lines):
            print(f"    {lines[i].strip()}")
    
    print(f"\n  샘플 노드 정의 (기업→스킬 경계):")
    if n1 < len(lines):
        print(f"    {lines[n1].strip()}")  # 마지막 기업
    if n1 + 1 < len(lines):
        print(f"    {lines[n1 + 1].strip()}")  # 첫 번째 스킬
    
    # Edges 섹션 확인
    edges_start = None
    for i, line in enumerate(lines):
        if line.startswith('*Edges'):
            edges_start = i
            break
    
    if edges_start:
        print(f"\n  Edges 섹션 시작: {edges_start + 1}번째 줄")
        if edges_start + 1 < len(lines):
            print(f"    샘플 엣지: {lines[edges_start + 1].strip()}")
    
    print("\n" + "=" * 60)
    print("변환 완료!")
    print("=" * 60)
    print(f"\n생성된 파일: {output_file}")
    print(f"\nPajek 사용 방법:")
    print(f"  1. File → Network → Read → {output_file}")
    print(f"  2. Pajek이 자동으로 2-Mode 네트워크로 인식합니다")
    print(f"  3. Draw → Network → Draw-Partition")
    print(f"  4. Draw → Energy → Kamada-Kawai → Bipartite")
    print(f"  5. 한글 깨짐 시: File → Preferences → Default Text Encoding → UTF-8")
    
    return output_file


if __name__ == "__main__":
    # 현재 스크립트가 있는 디렉토리에서 실행
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    convert_csv_to_2mode_network()

