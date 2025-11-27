"""
개발관련_raw: Skill-Skill Network Builder
developer_bipartite_skill_edges.csv를 기반으로 스킬 간 co-occurrence 네트워크를 구축합니다.
"""

import pandas as pd
from collections import defaultdict, Counter
from itertools import combinations
import os


def load_skill_edges(csv_file: str = 'developer_bipartite_skill_edges.csv'):
    """CSV 파일에서 기업명별 스킬 리스트를 추출합니다."""
    print(f"데이터 파일 로딩 중: {csv_file}")
    
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    print(f"  로드된 행 수: {len(df)}개")
    
    company_skills = defaultdict(set)
    
    for _, row in df.iterrows():
        company = str(row['기업명']).strip()
        skill = str(row['Skill']).strip()
        
        if company and skill:
            company_skills[company].add(skill)
    
    company_skills_list = {company: sorted(list(skills)) 
                          for company, skills in company_skills.items()}
    
    print(f"  총 구인공고 수: {len(company_skills_list)}개")
    
    all_skills = set()
    for skills in company_skills_list.values():
        all_skills.update(skills)
    print(f"  총 고유 스킬 수: {len(all_skills)}개")
    
    return company_skills_list


def calculate_cooccurrence(company_skills: dict):
    """구인공고별 스킬 쌍의 co-occurrence 빈도를 계산합니다."""
    print("\n스킬 쌍 co-occurrence 계산 중...")
    
    cooccurrence = Counter()
    
    for company, skills in company_skills.items():
        skill_pairs = list(combinations(sorted(skills), 2))
        
        for skill1, skill2 in skill_pairs:
            cooccurrence[(skill1, skill2)] += 1
    
    print(f"  총 스킬 쌍 수: {len(cooccurrence)}개")
    print(f"  최대 co-occurrence: {max(cooccurrence.values()) if cooccurrence else 0}")
    
    return cooccurrence


def build_skill_network(cooccurrence_dict: Counter, min_weight: int = 1):
    """Co-occurrence 딕셔너리를 기반으로 NetworkX 그래프를 생성합니다."""
    import networkx as nx
    
    print(f"\n네트워크 구축 중 (min_weight >= {min_weight})...")
    
    G = nx.Graph()
    
    # 스킬 쌍을 엣지로 추가
    for (skill1, skill2), weight in cooccurrence_dict.items():
        if weight >= min_weight:
            G.add_edge(skill1, skill2, weight=weight)
    
    print(f"  노드 수: {G.number_of_nodes()}개")
    print(f"  엣지 수: {G.number_of_edges()}개 (min_weight >= {min_weight})")
    
    return G


def save_network(G, output_file: str = 'developer_skill_skill_network.net'):
    """NetworkX 그래프를 Pajek .net 형식으로 저장합니다."""
    import networkx as nx
    
    print(f"\n네트워크 저장 중: {output_file}")
    
    # 노드 레이블 매핑
    nodes = sorted(G.nodes())
    node_to_id = {node: idx + 1 for idx, node in enumerate(nodes)}
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Vertices 섹션
        f.write(f'*Vertices {len(nodes)}\n')
        for node in nodes:
            node_id = node_to_id[node]
            f.write(f'{node_id} "{node}"\n')
        
        # Edges 섹션
        f.write('*Edges\n')
        for u, v, data in G.edges(data=True):
            u_id = node_to_id[u]
            v_id = node_to_id[v]
            weight = data.get('weight', 1)
            f.write(f'{u_id} {v_id} {int(weight)}\n')
    
    print(f"  저장 완료: {output_file}")


def main():
    """메인 함수"""
    print("="*60)
    print("개발관련_raw: Skill-Skill Network 구축")
    print("="*60)
    
    # 현재 디렉토리로 이동
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 1. 데이터 로드
    company_skills = load_skill_edges('developer_bipartite_skill_edges.csv')
    
    # 2. Co-occurrence 계산
    cooccurrence = calculate_cooccurrence(company_skills)
    
    # 3. 네트워크 구축
    G = build_skill_network(cooccurrence, min_weight=1)
    
    # 4. 저장
    save_network(G, 'developer_skill_skill_network.net')
    
    print("\n" + "="*60)
    print("작업 완료!")
    print("="*60)


if __name__ == "__main__":
    main()



