"""
bipartite_skill_long.csv를 Pajek bipartite 네트워크 .net 형식으로 변환하는 스크립트

Pajek bipartite 네트워크 형식:
- *Vertices N: 모든 노드 (기업 + 스킬)
- *Edges: 기업-스킬 간의 연결
- Partition 파일: 노드 타입 구분 (선택사항, 시각화에 유용)
"""

import pandas as pd
import os
from collections import Counter


def load_bipartite_data(csv_file: str = '../bipartite_skill_long.csv') -> pd.DataFrame:
    """
    bipartite_skill_long.csv 파일을 로드합니다.
    
    Args:
        csv_file (str): CSV 파일 경로
        
    Returns:
        pd.DataFrame: 로드된 데이터프레임
    """
    print(f"데이터 파일 로딩 중: {csv_file}")
    
    df = pd.read_csv(csv_file)
    
    print(f"  총 행 수: {len(df):,}개")
    print(f"  고유 기업 수: {df['기업명'].nunique():,}개")
    print(f"  고유 스킬 수: {df['Skill'].nunique():,}개")
    
    return df


def create_pajek_bipartite_network(df: pd.DataFrame, output_file: str = 'bipartite_skill_network.net'):
    """
    Pajek bipartite 네트워크 .net 파일을 생성합니다.
    
    Pajek 형식:
    *Vertices N
    1 "기업명1"
    2 "기업명2"
    ...
    M "스킬1"
    M+1 "스킬2"
    ...
    *Edges
    1 M 1
    2 M+1 1
    ...
    
    Args:
        df (pd.DataFrame): bipartite 데이터프레임
        output_file (str): 출력 .net 파일 경로
    """
    print(f"\nPajek bipartite 네트워크 생성 중...")
    
    # 고유한 기업과 스킬 추출
    unique_companies = sorted(df['기업명'].unique())
    unique_skills = sorted(df['Skill'].unique())
    
    total_nodes = len(unique_companies) + len(unique_skills)
    
    print(f"  기업 노드: {len(unique_companies):,}개")
    print(f"  스킬 노드: {len(unique_skills):,}개")
    print(f"  총 노드 수: {total_nodes:,}개")
    
    # 노드 ID 매핑 생성
    # 기업: 1부터 시작
    company_to_id = {company: idx + 1 for idx, company in enumerate(unique_companies)}
    # 스킬: 기업 다음부터 시작
    skill_to_id = {skill: idx + 1 + len(unique_companies) for idx, skill in enumerate(unique_skills)}
    
    # 엣지 수 계산
    edge_count = len(df)
    print(f"  엣지 수: {edge_count:,}개")
    
    # .net 파일 작성
    print(f"\n.net 파일 작성 중: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Vertices 섹션
        f.write(f"*Vertices {total_nodes}\n")
        
        # 기업 노드 추가
        for company in unique_companies:
            company_id = company_to_id[company]
            # 따옴표 이스케이프 처리
            label_escaped = str(company).replace('"', '\\"')
            f.write(f'{company_id} "{label_escaped}"\n')
        
        # 스킬 노드 추가
        for skill in unique_skills:
            skill_id = skill_to_id[skill]
            # 따옴표 이스케이프 처리
            label_escaped = str(skill).replace('"', '\\"')
            f.write(f'{skill_id} "{label_escaped}"\n')
        
        # Edges 섹션
        f.write(f"*Edges\n")
        
        # 엣지 추가 (가중치는 1로 설정, 필요시 중복 제거 가능)
        for _, row in df.iterrows():
            company = row['기업명']
            skill = row['Skill']
            
            company_id = company_to_id[company]
            skill_id = skill_to_id[skill]
            
            # 가중치 1로 저장 (필요시 중복 카운트 가능)
            f.write(f"{company_id} {skill_id} 1\n")
    
    print(f"  ✓ .net 파일 생성 완료: {output_file}")
    
    return output_file, company_to_id, skill_to_id, len(unique_companies)


def create_partition_file(company_count: int, total_nodes: int, 
                          output_file: str = 'bipartite_skill_network.clu'):
    """
    Pajek partition 파일을 생성합니다.
    노드 타입을 구분하기 위한 파일 (기업=1, 스킬=2)
    
    Args:
        company_count (int): 기업 노드 수
        total_nodes (int): 전체 노드 수
        output_file (str): 출력 .clu 파일 경로
    """
    print(f"\nPartition 파일 생성 중: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"*Vertices {total_nodes}\n")
        
        # 기업 노드: 1
        for i in range(1, company_count + 1):
            f.write("1\n")
        
        # 스킬 노드: 2
        for i in range(company_count + 1, total_nodes + 1):
            f.write("2\n")
    
    print(f"  ✓ Partition 파일 생성 완료: {output_file}")
    print(f"    - 기업 노드 (1): {company_count:,}개")
    print(f"    - 스킬 노드 (2): {total_nodes - company_count:,}개")


def create_vector_file(degrees: dict, node_to_id: dict, 
                      output_file: str = 'bipartite_skill_network.vec'):
    """
    Pajek vector 파일을 생성합니다 (노드별 degree 정보).
    
    Args:
        degrees (dict): 노드별 degree 딕셔너리
        node_to_id (dict): 노드명 -> ID 매핑
        output_file (str): 출력 .vec 파일 경로
    """
    print(f"\nVector 파일 생성 중: {output_file}")
    
    # 전체 노드 ID 범위 확인
    max_id = max(node_to_id.values())
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"*Vertices {max_id}\n")
        
        # 모든 노드 ID에 대해 degree 값 저장
        for node_id in range(1, max_id + 1):
            # ID에서 노드명 찾기
            node_name = None
            for name, nid in node_to_id.items():
                if nid == node_id:
                    node_name = name
                    break
            
            degree = degrees.get(node_name, 0)
            f.write(f"{degree}\n")
    
    print(f"  ✓ Vector 파일 생성 완료: {output_file}")


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("Bipartite Skill Network → Pajek .net 변환")
    print("=" * 60)
    
    # 1. 데이터 로딩
    df = load_bipartite_data()
    
    # 2. Pajek .net 파일 생성
    output_file, company_to_id, skill_to_id, company_count = create_pajek_bipartite_network(df)
    
    # 3. Partition 파일 생성 (노드 타입 구분)
    total_nodes = len(company_to_id) + len(skill_to_id)
    create_partition_file(company_count, total_nodes)
    
    # 4. Vector 파일 생성 (degree 정보, 선택사항)
    # 각 노드의 degree 계산
    company_degrees = Counter(df['기업명'])
    skill_degrees = Counter(df['Skill'])
    
    all_degrees = {}
    all_degrees.update(company_degrees)
    all_degrees.update(skill_degrees)
    
    # 모든 노드 ID 매핑
    all_node_to_id = {**company_to_id, **skill_to_id}
    
    create_vector_file(all_degrees, all_node_to_id)
    
    # 5. 요약 정보 출력
    print("\n" + "=" * 60)
    print("변환 완료!")
    print("=" * 60)
    print(f"생성된 파일:")
    print(f"  1. {output_file} - 네트워크 파일 (Pajek에서 열기)")
    print(f"  2. bipartite_skill_network.clu - Partition 파일 (노드 타입 구분)")
    print(f"  3. bipartite_skill_network.vec - Vector 파일 (degree 정보)")
    print(f"\nPajek 사용 방법:")
    print(f"  1. File → Network → Read → {output_file}")
    print(f"  2. File → Partition → Read → bipartite_skill_network.clu")
    print(f"  3. Draw → Network (시각화)")
    print(f"  4. 한글 깨짐 시: File → Preferences → Default Text Encoding → UTF-8")


if __name__ == "__main__":
    main()

