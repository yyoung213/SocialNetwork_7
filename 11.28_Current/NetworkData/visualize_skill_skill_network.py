"""
Skill-Skill One-mode Projection Network 시각화 스크립트

요구사항:
1. 가중치 필터링: weight >= 5
2. 노드 크기: Degree에 비례 (Top 3만 크게, 나머지는 작게)
3. 레이아웃: Spring Layout
4. 엣지 두께: Weight 기반, 색상 연하게
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import os

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
plt.rcParams['axes.unicode_minus'] = False


def create_bipartite_graph_from_csv(edges_csv_path):
    """CSV 파일을 직접 사용하여 Bipartite 네트워크 그래프를 생성합니다."""
    print(f"[1단계] Bipartite 그래프 생성: {edges_csv_path}")
    
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
    
    print(f"  그래프 노드 수: {G.number_of_nodes()}")
    print(f"  그래프 엣지 수: {G.number_of_edges()}")
    print(f"  공고 노드 수: {len(unique_jobs)}")
    print(f"  스킬 노드 수: {len(unique_skills)}")
    
    return G, unique_jobs, unique_skills


def create_skill_skill_network(bipartite_G, job_nodes):
    """Bipartite 네트워크에서 Skill-Skill One-mode Projection을 생성합니다."""
    print(f"[2단계] Skill-Skill One-mode Projection 생성")
    
    # 스킬 노드만 추출
    skill_nodes = [n for n in bipartite_G.nodes() if bipartite_G.nodes[n]['node_type'] == 'skill']
    
    # Weighted projection 생성
    skill_skill_G = nx.bipartite.weighted_projected_graph(bipartite_G, skill_nodes)
    
    print(f"  스킬-스킬 네트워크 노드 수: {skill_skill_G.number_of_nodes()}")
    print(f"  스킬-스킬 네트워크 엣지 수: {skill_skill_G.number_of_edges()}")
    
    # 가중치 통계
    weights = [d['weight'] for u, v, d in skill_skill_G.edges(data=True)]
    if weights:
        print(f"  가중치 통계:")
        print(f"    최소: {min(weights)}")
        print(f"    최대: {max(weights)}")
        print(f"    평균: {np.mean(weights):.2f}")
        print(f"    중앙값: {np.median(weights):.2f}")
    
    return skill_skill_G


def filter_network_by_weight(G, min_weight=5):
    """가중치가 min_weight 이상인 엣지만 남깁니다."""
    print(f"[3단계] 가중치 필터링 (weight >= {min_weight})")
    
    G_filtered = G.copy()
    
    # 가중치가 낮은 엣지 제거
    edges_to_remove = []
    for u, v, d in G_filtered.edges(data=True):
        if d.get('weight', 0) < min_weight:
            edges_to_remove.append((u, v))
    
    G_filtered.remove_edges_from(edges_to_remove)
    
    # 연결되지 않은 노드 제거
    isolated_nodes = list(nx.isolates(G_filtered))
    G_filtered.remove_nodes_from(isolated_nodes)
    
    print(f"  필터링 전: {G.number_of_nodes()}개 노드, {G.number_of_edges()}개 엣지")
    print(f"  필터링 후: {G_filtered.number_of_nodes()}개 노드, {G_filtered.number_of_edges()}개 엣지")
    print(f"  제거된 엣지: {len(edges_to_remove)}개")
    print(f"  제거된 고립 노드: {len(isolated_nodes)}개")
    
    return G_filtered


def visualize_skill_skill_network(G, output_path):
    """Skill-Skill 네트워크를 시각화합니다."""
    print(f"[4단계] Skill-Skill 네트워크 시각화")
    
    fig, ax = plt.subplots(figsize=(24, 20))
    
    # Degree 계산
    degrees = dict(G.degree())
    
    # TOP 3 노드 식별
    sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
    top3_nodes = [n for n, _ in sorted_nodes[:3]]
    top3_degrees = {n: degrees[n] for n in top3_nodes}
    
    print(f"  TOP 3 스킬 (Degree 기준):")
    for i, (node_id, degree) in enumerate(sorted_nodes[:3], 1):
        skill_name = G.nodes[node_id].get('label', node_id)
        print(f"    {i}. {skill_name}: {degree}")
    
    # 노드 크기 계산 - TOP 3는 크게, 나머지는 작게
    top3_min_size = 2000
    top3_max_size = 3000
    other_size = 150  # 나머지 노드는 작은 고정 크기
    
    def size_func(node_id, degree):
        if node_id in top3_nodes:
            # TOP 3는 degree에 비례하여 크기 조정
            rank = top3_nodes.index(node_id) + 1
            if rank == 1:
                return top3_max_size
            elif rank == 2:
                return top3_min_size + (top3_max_size - top3_min_size) * 0.7
            else:  # rank == 3
                return top3_min_size + (top3_max_size - top3_min_size) * 0.4
        else:
            return other_size
    
    node_sizes = [size_func(n, degrees.get(n, 0)) for n in G.nodes()]
    
    # 엣지 가중치 추출
    edges = G.edges(data=True)
    edge_weights = [d.get('weight', 1) for u, v, d in edges]
    
    # 엣지 두께 정규화 (Weight 기반)
    if edge_weights:
        min_weight_val = min(edge_weights)
        max_weight_val = max(edge_weights)
        min_width = 0.5
        max_width = 6.0
        
        def width_func(weight):
            if max_weight_val == min_weight_val:
                return (min_width + max_width) / 2
            normalized = (weight - min_weight_val) / (max_weight_val - min_weight_val)
            return min_width + (max_width - min_width) * normalized
    else:
        def width_func(weight):
            return 1.0
    
    edge_widths = [width_func(w) for w in edge_weights]
    
    # Spring Layout
    print(f"  Spring layout 계산 중... (노드 수: {G.number_of_nodes()})")
    k = 2 / np.sqrt(G.number_of_nodes())  # 노드 간 거리 조정
    pos = nx.spring_layout(G, k=k, iterations=200, seed=42)
    
    # 엣지 그리기 (먼저 그려서 노드 아래에, 연한 색상)
    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.2, 
                          edge_color='lightgray', ax=ax)
    
    # 노드를 TOP 3와 나머지로 분리하여 그리기
    other_nodes = [n for n in G.nodes() if n not in top3_nodes]
    
    # 나머지 노드 먼저 그리기 (작게, 회색 계열)
    other_sizes = [size_func(n, degrees.get(n, 0)) for n in other_nodes]
    nx.draw_networkx_nodes(G, pos, nodelist=other_nodes,
                          node_size=other_sizes, 
                          node_color='lightblue', alpha=0.6,
                          edgecolors='gray', linewidths=1, ax=ax)
    
    # TOP 3 노드 그리기 (크게, 강조 색상)
    top3_colors = ['#FF6B6B', '#4ECDC4', '#FFE66D']  # 빨강, 청록, 노랑
    top3_sizes = [size_func(n, degrees.get(n, 0)) for n in top3_nodes]
    
    for i, (node_id, size) in enumerate(zip(top3_nodes, top3_sizes)):
        color = top3_colors[i]
        nx.draw_networkx_nodes(G, pos, nodelist=[node_id],
                              node_color=color, node_size=size,
                              alpha=0.9, ax=ax, edgecolors='black', linewidths=3)
    
    # TOP 3 노드 레이블을 오른쪽 아래 모서리에 배치
    label_text = "TOP 3 스킬:\n"
    for i, node_id in enumerate(top3_nodes, 1):
        skill_name = G.nodes[node_id].get('label', node_id)
        degree = degrees[node_id]
        label_text += f"#{i} {skill_name} (Degree: {degree})\n"
    
    # 오른쪽 아래 모서리에 레이블 배치
    ax.text(0.98, 0.02, label_text, transform=ax.transAxes,
           fontsize=12, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.8', facecolor='white', 
                    edgecolor='black', linewidth=2, alpha=0.95),
           verticalalignment='bottom', horizontalalignment='right')
    
    ax.set_title('Skill-Skill 네트워크 (One-mode Projection)\n'
                 '실무에서 함께 쓰이는 스킬 패키지가 군집으로 나타남', 
                 fontsize=20, pad=25, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  저장 완료: {output_path}")
    plt.close()


def main():
    """메인 함수"""
    print("=" * 70)
    print("Skill-Skill One-mode Projection Network 시각화")
    print("=" * 70)
    
    # 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    edges_csv = os.path.join(script_dir, 'posting_skill_bipartite_edges.csv')
    output_dir = os.path.join(parent_dir, 'skill_skill_networkVisual')
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # 1단계: Bipartite 그래프 생성
    bipartite_G, unique_jobs, unique_skills = create_bipartite_graph_from_csv(edges_csv)
    
    # 2단계: Skill-Skill One-mode Projection 생성
    skill_skill_G = create_skill_skill_network(bipartite_G, unique_jobs)
    
    # 3단계: 가중치 필터링 (weight >= 5)
    G_filtered = filter_network_by_weight(skill_skill_G, min_weight=5)
    
    if G_filtered.number_of_nodes() == 0:
        print(f"  오류: 필터링 후 노드가 없습니다.")
        return
    
    # 4단계: 시각화
    output_path = os.path.join(output_dir, 'skill_skill_network.png')
    visualize_skill_skill_network(G_filtered, output_path)
    
    print("\n" + "=" * 70)
    print("작업 완료!")
    print(f"결과물 저장 위치: {output_dir}")
    print("=" * 70)


if __name__ == '__main__':
    main()
