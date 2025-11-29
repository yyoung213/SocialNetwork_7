"""
Pajek Bipartite 파일을 기반으로 Post-Post One-mode Projection 네트워크 생성

입력: posting_skill_bipartite_2mode.net (Pajek bipartite 형식)
출력: post_post_network.net (Pajek one-mode 형식)
"""

import networkx as nx
import os
from collections import defaultdict, Counter

def parse_pajek_bipartite(file_path):
    """Pajek 형식의 bipartite 네트워크 파일을 파싱합니다."""
    print(f"[1단계] Pajek Bipartite 파일 파싱: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 헤더 파싱
    header = lines[0].strip()
    parts = header.split()
    total_nodes = int(parts[1])
    n_jobs = int(parts[2])  # Mode 1 (공고) 노드 수
    
    print(f"  총 노드 수: {total_nodes}")
    print(f"  공고 노드 수 (Mode 1): {n_jobs}")
    print(f"  스킬 노드 수 (Mode 2): {total_nodes - n_jobs}")
    
    # 노드 정보 파싱
    job_nodes = {}  # {node_id: job_label}
    skill_nodes = {}  # {node_id: skill_name}
    
    i = 1
    # 공고 노드 (Mode 1)
    for idx in range(n_jobs):
        if i >= len(lines):
            break
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        parts = line.split('"')
        if len(parts) >= 2:
            node_id = int(parts[0].strip())
            job_label = parts[1].strip()
            job_nodes[node_id] = job_label
        i += 1
    
    # 스킬 노드 (Mode 2)
    for idx in range(total_nodes - n_jobs):
        if i >= len(lines):
            break
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        parts = line.split('"')
        if len(parts) >= 2:
            node_id = int(parts[0].strip())
            skill_name = parts[1].strip()
            skill_nodes[node_id] = skill_name
        i += 1
    
    # 엣지 파싱
    edges = []
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('*Edges') or line.startswith('*Arcs'):
            i += 1
            break
        i += 1
    
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        parts = line.split()
        if len(parts) >= 2:
            job_id = int(parts[0])
            skill_id = int(parts[1])
            if job_id in job_nodes and skill_id in skill_nodes:
                edges.append((job_id, skill_id))
        i += 1
    
    print(f"  엣지 수: {len(edges)}")
    
    return job_nodes, skill_nodes, edges, n_jobs, total_nodes


def create_bipartite_graph(job_nodes, skill_nodes, edges):
    """Bipartite 네트워크 그래프를 생성합니다."""
    print(f"[2단계] Bipartite 그래프 생성")
    
    G = nx.Graph()
    
    # 노드 추가
    for node_id, job_label in job_nodes.items():
        G.add_node(node_id, node_type='job', label=job_label)
    
    for node_id, skill_name in skill_nodes.items():
        G.add_node(node_id, node_type='skill', label=skill_name)
    
    # 엣지 추가
    G.add_edges_from(edges)
    
    print(f"  그래프 노드 수: {G.number_of_nodes()}")
    print(f"  그래프 엣지 수: {G.number_of_edges()}")
    
    return G


def create_post_post_network(bipartite_G, job_nodes):
    """Bipartite 네트워크에서 Post-Post One-mode Projection을 생성합니다."""
    print(f"[3단계] Post-Post One-mode Projection 생성")
    
    # 공고 노드 ID 리스트
    job_node_ids = list(job_nodes.keys())
    
    # Weighted projection 생성
    post_post_G = nx.bipartite.weighted_projected_graph(bipartite_G, job_node_ids)
    
    print(f"  공고-공고 네트워크 노드 수: {post_post_G.number_of_nodes()}")
    print(f"  공고-공고 네트워크 엣지 수: {post_post_G.number_of_edges()}")
    
    # 가중치 통계
    weights = [d['weight'] for u, v, d in post_post_G.edges(data=True)]
    if weights:
        print(f"  가중치 통계:")
        print(f"    최소: {min(weights)}")
        print(f"    최대: {max(weights)}")
        print(f"    평균: {sum(weights) / len(weights):.2f}")
    
    return post_post_G, job_nodes


def save_pajek_network(G, job_nodes, output_file):
    """Post-Post 네트워크를 Pajek 형식으로 저장합니다."""
    print(f"[4단계] Pajek .net 파일 생성: {output_file}")
    
    # 노드 ID 매핑 (공고 ID -> 1부터 시작하는 숫자 ID)
    sorted_job_ids = sorted(G.nodes())
    job_to_id = {job_id: idx + 1 for idx, job_id in enumerate(sorted_job_ids)}
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Vertices 섹션
        f.write(f"*Vertices {G.number_of_nodes()}\n")
        for job_id in sorted_job_ids:
            node_id = job_to_id[job_id]
            job_label = job_nodes.get(job_id, str(job_id))
            # Pajek 형식: id "label"
            label_escaped = str(job_label).replace('"', '\\"')
            f.write(f'{node_id} "{label_escaped}"\n')
        
        # Edges 섹션 (무방향 그래프)
        f.write("*Edges\n")
        for u, v in sorted(G.edges()):
            u_id = job_to_id[u]
            v_id = job_to_id[v]
            weight = G.edges[u, v].get('weight', 1)
            f.write(f"{u_id} {v_id} {weight}\n")
    
    print(f"  파일 생성 완료: {output_file}")
    print(f"  노드 수: {G.number_of_nodes()}개")
    print(f"  엣지 수: {G.number_of_edges()}개")


def main():
    """메인 함수"""
    print("=" * 70)
    print("Post-Post One-mode Projection 네트워크 생성 (Pajek 형식)")
    print("=" * 70)
    
    # 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'posting_skill_bipartite_2mode.net')
    output_file = os.path.join(script_dir, 'post_post_network.net')
    
    # 1단계: Pajek Bipartite 파일 파싱
    job_nodes, skill_nodes, edges, n_jobs, total_nodes = parse_pajek_bipartite(input_file)
    
    # 2단계: Bipartite 그래프 생성
    bipartite_G = create_bipartite_graph(job_nodes, skill_nodes, edges)
    
    # 3단계: Post-Post One-mode Projection 생성
    post_post_G, job_node_dict = create_post_post_network(bipartite_G, job_nodes)
    
    # 4단계: Pajek 형식으로 저장
    save_pajek_network(post_post_G, job_nodes, output_file)
    
    print("\n" + "=" * 70)
    print("작업 완료!")
    print(f"출력 파일: {output_file}")
    print("=" * 70)


if __name__ == '__main__':
    main()

