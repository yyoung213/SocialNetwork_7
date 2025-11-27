"""
개발관련_raw: Skill-Skill Network Visualization
degree에 따라 노드 크기를 설정하고 가독성 좋게 시각화합니다.
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os


def read_pajek_net(file_path: str):
    """Pajek .net 파일을 읽어 NetworkX 그래프로 변환합니다."""
    print(f"네트워크 파일 로딩 중: {file_path}")
    
    G = nx.Graph()
    node_id_to_label = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('*Vertices'):
            i += 1
            continue
        
        if line.startswith('*Edges') or line.startswith('*Arcs'):
            i += 1
            break
        
        if line and not line.startswith('*'):
            parts = line.split('"', 2)
            if len(parts) >= 2:
                try:
                    node_id = int(parts[0].strip())
                    label = parts[1].strip()
                    node_id_to_label[node_id] = label
                    G.add_node(node_id, label=label)
                except (ValueError, IndexError):
                    pass
        i += 1
    
    while i < len(lines):
        line = lines[i].strip()
        if line and not line.startswith('*'):
            parts = line.split()
            if len(parts) >= 2:
                try:
                    source_id = int(parts[0])
                    target_id = int(parts[1])
                    weight = float(parts[2]) if len(parts) >= 3 else 1.0
                    G.add_edge(source_id, target_id, weight=weight)
                except (ValueError, IndexError):
                    pass
        i += 1
    
    print(f"  노드 수: {G.number_of_nodes()}개")
    print(f"  엣지 수: {G.number_of_edges()}개")
    
    return G, node_id_to_label


def visualize_skill_network(G, node_id_to_label, output_file: str = 'developer_skill_skill_network_visualization.png',
                           figsize: tuple = (40, 30), min_degree: int = 1):
    """Skill-Skill 네트워크를 시각화합니다."""
    print(f"\n네트워크 시각화 생성 중...")
    
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    # Degree 계산
    degrees = dict(G.degree())
    
    # 최소 degree 이상인 노드만 필터링
    G_filtered = G.subgraph([n for n in G.nodes() if degrees[n] >= min_degree])
    degrees_filtered = {n: degrees[n] for n in G_filtered.nodes()}
    
    print(f"  필터링 후 노드 수: {G_filtered.number_of_nodes()}개 (min_degree >= {min_degree})")
    
    # 레이아웃 계산
    print("  레이아웃 계산 중... (시간이 걸릴 수 있습니다)")
    pos = nx.spring_layout(G_filtered, k=3, iterations=300, seed=42)
    
    # 노드 크기 (degree에 비례)
    node_sizes = [max(50, degrees_filtered[n] * 5) for n in G_filtered.nodes()]
    
    # 노드 색상 (degree에 비례)
    node_colors = [degrees_filtered[n] for n in G_filtered.nodes()]
    
    # 시각화
    fig, ax = plt.subplots(figsize=figsize)
    
    # 엣지 그리기
    edges = G_filtered.edges(data=True)
    edge_weights = [d.get('weight', 1) for u, v, d in edges]
    if edge_weights:
        max_weight = max(edge_weights)
        edge_widths = [w / max_weight * 2 for w in edge_weights]
    else:
        edge_widths = [0.5] * len(edges)
    
    nx.draw_networkx_edges(G_filtered, pos, width=edge_widths, 
                          alpha=0.1, edge_color='gray', ax=ax)
    
    # 노드 그리기
    nx.draw_networkx_nodes(G_filtered, pos, node_size=node_sizes,
                          node_color=node_colors, cmap='YlOrRd',
                          alpha=0.8, ax=ax, edgecolors='black', linewidths=0.5)
    
    # 레이블 (상위 노드만)
    top_nodes = sorted(degrees_filtered.items(), key=lambda x: x[1], reverse=True)[:30]
    labels = {}
    for node_id, _ in top_nodes:
        label = node_id_to_label.get(node_id, f"Node {node_id}")
        labels[node_id] = label
    
    nx.draw_networkx_labels(G_filtered, pos, labels, font_size=8, 
                           ax=ax, font_weight='bold', font_family='Malgun Gothic')
    
    ax.set_title(f'개발관련_raw: Skill-Skill Network\n(노드 크기 ∝ Degree, 상위 30개 레이블 표시)', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"  저장 완료: {output_file}")
    
    # 통계 출력
    print(f"\n상위 10개 노드 (by degree):")
    for i, (node_id, deg) in enumerate(top_nodes[:10], 1):
        label = node_id_to_label.get(node_id, f"Node {node_id}")
        print(f"  {i:2d}. {label:30s} (degree: {deg:3d})")


def main():
    """메인 함수"""
    print("="*60)
    print("개발관련_raw: Skill-Skill Network 시각화")
    print("="*60)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    net_file = 'developer_skill_skill_network.net'
    if not os.path.exists(net_file):
        print(f"오류: '{net_file}' 파일을 찾을 수 없습니다.")
        return
    
    G, node_id_to_label = read_pajek_net(net_file)
    visualize_skill_network(G, node_id_to_label)


if __name__ == "__main__":
    main()



