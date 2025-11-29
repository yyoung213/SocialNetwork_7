"""
작은 Component에 속한 노드 찾기
"""

import pandas as pd
import networkx as nx
import os

def create_bipartite_graph_from_csv(edges_csv_path):
    """CSV 파일을 직접 사용하여 Bipartite 네트워크 그래프를 생성합니다."""
    df = pd.read_csv(edges_csv_path, encoding='utf-8-sig')
    
    G = nx.Graph()
    
    # 고유한 job_id와 skill 추출
    unique_jobs = df['job_id'].unique()
    unique_skills = df['skill'].unique()
    
    # 노드 추가 (공고 노드)
    for job_id in unique_jobs:
        job_type = df[df['job_id'] == job_id]['job_type'].iloc[0]
        G.add_node(job_id, node_type='job', job_type=job_type, label=job_id)
    
    # 노드 추가 (스킬 노드)
    for skill_name in unique_skills:
        G.add_node(skill_name, node_type='skill', skill_name=skill_name, label=skill_name)
    
    # 엣지 추가
    for _, row in df.iterrows():
        job_id = str(row['job_id'])
        skill_name = str(row['skill'])
        if job_id in G and skill_name in G:
            G.add_edge(job_id, skill_name)
    
    return G, unique_jobs, unique_skills


def create_skill_skill_network(bipartite_G, job_nodes):
    """Bipartite 네트워크에서 Skill-Skill One-mode Projection을 생성합니다."""
    # 스킬 노드만 추출
    skill_nodes = [n for n in bipartite_G.nodes() if bipartite_G.nodes[n]['node_type'] == 'skill']
    
    # Weighted projection 생성
    skill_skill_G = nx.bipartite.weighted_projected_graph(bipartite_G, skill_nodes)
    
    return skill_skill_G


def find_small_components(G):
    """작은 Component들을 찾습니다."""
    # Connected Components 탐지
    components = list(nx.connected_components(G))
    components = [list(comp) for comp in components]
    
    # 크기별로 정렬 (큰 것부터)
    components.sort(key=len, reverse=True)
    
    print(f"총 Component 개수: {len(components)}")
    print(f"\n각 Component 정보:")
    
    for i, comp in enumerate(components, 1):
        subgraph = G.subgraph(comp)
        print(f"\nComponent {i}:")
        print(f"  노드 수: {len(comp)}")
        print(f"  엣지 수: {subgraph.number_of_edges()}")
        
        if len(comp) <= 10:  # 작은 Component는 모든 노드 출력
            print(f"  노드 목록:")
            for node in comp:
                skill_name = G.nodes[node].get('label', node)
                print(f"    - {skill_name}")
        else:
            print(f"  대표 노드 (상위 10개):")
            degrees = dict(subgraph.degree())
            top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]
            for node_id, degree in top_nodes:
                skill_name = G.nodes[node_id].get('label', node_id)
                print(f"    - {skill_name} (Degree: {degree})")
    
    # 작은 Component 찾기 (Giant Component 제외)
    if len(components) > 1:
        print(f"\n{'='*70}")
        print("작은 Component 상세 정보:")
        print(f"{'='*70}")
        
        for i, comp in enumerate(components[1:], 2):  # 첫 번째(Giant) 제외
            subgraph = G.subgraph(comp)
            print(f"\nComponent {i} (작은 Component):")
            print(f"  노드 수: {len(comp)}")
            print(f"  엣지 수: {subgraph.number_of_edges()}")
            print(f"  노드 목록:")
            for node in comp:
                skill_name = G.nodes[node].get('label', node)
                # 엣지 정보도 출력
                edges = list(subgraph.edges(node, data=True))
                if edges:
                    print(f"    - {skill_name}")
                    for u, v, d in edges:
                        other_skill = G.nodes[v].get('label', v) if v != node else G.nodes[u].get('label', u)
                        weight = d.get('weight', 1)
                        print(f"      └─ {other_skill} (weight: {weight})")
                else:
                    print(f"    - {skill_name} (고립된 노드)")


def main():
    """메인 함수"""
    print("=" * 70)
    print("작은 Component 노드 찾기")
    print("=" * 70)
    
    # 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    edges_csv = os.path.join(script_dir, 'posting_skill_bipartite_edges.csv')
    
    # 1단계: Bipartite 그래프 생성
    bipartite_G, unique_jobs, unique_skills = create_bipartite_graph_from_csv(edges_csv)
    
    # 2단계: Skill-Skill One-mode Projection 생성
    skill_skill_G = create_skill_skill_network(bipartite_G, unique_jobs)
    
    # 3단계: 작은 Component 찾기
    find_small_components(skill_skill_G)
    
    print("\n" + "=" * 70)
    print("작업 완료!")
    print("=" * 70)


if __name__ == '__main__':
    main()


