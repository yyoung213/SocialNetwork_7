"""
Skill-Skill Network Visualization
degree에 따라 노드 크기를 설정하고 가독성 좋게 시각화합니다.
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os


def read_pajek_net(file_path: str):
    """
    Pajek .net 파일을 읽어 NetworkX 그래프로 변환합니다.
    
    Args:
        file_path (str): .net 파일 경로
        
    Returns:
        nx.Graph: NetworkX 그래프 객체
    """
    print(f"네트워크 파일 로딩 중: {file_path}")
    
    try:
        # NetworkX의 read_pajek 사용 (UTF-8 인코딩)
        G = nx.read_pajek(file_path, encoding='utf-8')
        print(f"  노드 수: {G.number_of_nodes()}개")
        print(f"  엣지 수: {G.number_of_edges()}개")
        return G
    except Exception as e:
        print(f"  오류 발생: {e}")
        print("  수동 파싱 시도 중...")
        return read_pajek_manual(file_path)


def read_pajek_manual(file_path: str):
    """
    Pajek .net 파일을 수동으로 파싱합니다.
    """
    G = nx.Graph()
    node_id_to_label = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    # Vertices 섹션 읽기
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('*Vertices'):
            num_vertices = int(line.split()[1])
            i += 1
            for j in range(num_vertices):
                if i >= len(lines):
                    break
                parts = lines[i].strip().split(' ', 1)
                node_id = int(parts[0])
                # 따옴표 제거
                label = parts[1].strip('"').replace('\\"', '"')
                node_id_to_label[node_id] = label
                G.add_node(label)
                i += 1
        elif line.startswith('*Edges') or line.startswith('*Arcs'):
            i += 1
            # Edges 섹션 읽기
            while i < len(lines):
                edge_line = lines[i].strip()
                if not edge_line or edge_line.startswith('*'):
                    break
                parts = edge_line.split()
                if len(parts) >= 2:
                    source_id = int(parts[0])
                    target_id = int(parts[1])
                    weight = float(parts[2]) if len(parts) >= 3 else 1.0
                    
                    source = node_id_to_label.get(source_id)
                    target = node_id_to_label.get(target_id)
                    
                    if source and target:
                        G.add_edge(source, target, weight=weight)
                i += 1
            break
        else:
            i += 1
    
    print(f"  노드 수: {G.number_of_nodes()}개")
    print(f"  엣지 수: {G.number_of_edges()}개")
    return G


def visualize_skill_network(G: nx.Graph, output_file: str = 'skill_skill_network_visualization.png',
                           figsize: tuple = (40, 30), min_degree: int = 1):
    """
    스킬 네트워크를 시각화합니다.
    
    Args:
        G (nx.Graph): NetworkX 그래프
        output_file (str): 출력 이미지 파일 경로
        figsize (tuple): 그림 크기
        min_degree (int): 최소 degree 필터 (이 값보다 작은 노드는 제외)
    """
    print("\n네트워크 시각화 준비 중...")
    
    # 한글 폰트 설정
    plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
    # plt.rcParams['font.family'] = 'AppleGothic'  # macOS
    # plt.rcParams['font.family'] = 'NanumGothic'  # Linux
    plt.rcParams['axes.unicode_minus'] = False
    
    # 최소 degree 필터링 (선택적)
    if min_degree > 1:
        nodes_to_remove = [node for node in G.nodes() if G.degree(node) < min_degree]
        G_filtered = G.copy()
        G_filtered.remove_nodes_from(nodes_to_remove)
        print(f"  필터링: {len(nodes_to_remove)}개 노드 제거 (degree < {min_degree})")
        print(f"  필터링 후: {G_filtered.number_of_nodes()}개 노드, {G_filtered.number_of_edges()}개 엣지")
    else:
        G_filtered = G
    
    # Degree 계산
    degrees = dict(G_filtered.degree())
    degree_values = list(degrees.values())
    
    print(f"\nDegree 통계:")
    print(f"  평균 degree: {np.mean(degree_values):.2f}")
    print(f"  최소 degree: {min(degree_values)}")
    print(f"  최대 degree: {max(degree_values)}")
    
    # 노드 크기 설정 (degree에 비례)
    node_sizes = []
    min_degree_val = min(degree_values)
    max_degree_val = max(degree_values)
    
    # 노드 크기 범위: 50 ~ 3000
    size_min, size_max = 50, 3000
    
    for node in G_filtered.nodes():
        degree = degrees[node]
        if max_degree_val > min_degree_val:
            # 정규화
            normalized = (degree - min_degree_val) / (max_degree_val - min_degree_val)
            size = size_min + normalized * (size_max - size_min)
        else:
            size = (size_min + size_max) / 2
        node_sizes.append(size)
    
    # 레이아웃 계산 (노드 간격 조정)
    print("\n레이아웃 계산 중... (시간이 걸릴 수 있습니다)")
    
    # 노드 수에 따라 k 값 조정 (k가 클수록 노드 간격이 넓어짐)
    num_nodes = G_filtered.number_of_nodes()
    if num_nodes > 200:
        k = 15  # 큰 네트워크: 더 넓은 간격
        iterations = 500
    elif num_nodes > 100:
        k = 10
        iterations = 400
    else:
        k = 5
        iterations = 300
    
    print(f"  레이아웃 파라미터: k={k}, iterations={iterations}")
    
    # Spring layout (force-directed)
    pos = nx.spring_layout(G_filtered, k=k, iterations=iterations, seed=42)
    
    # 엣지 가중치에 따른 두께 및 색상
    edge_weights = [data.get('weight', 1) for u, v, data in G_filtered.edges(data=True)]
    if edge_weights:
        min_weight = min(edge_weights)
        max_weight = max(edge_weights)
        
        edge_widths = []
        edge_alphas = []
        
        for u, v, data in G_filtered.edges(data=True):
            weight = data.get('weight', 1)
            # 엣지 두께: 0.5 ~ 3.0
            if max_weight > min_weight:
                normalized = (weight - min_weight) / (max_weight - min_weight)
                width = 0.5 + normalized * 2.5
            else:
                width = 1.5
            edge_widths.append(width)
            
            # 엣지 투명도: 가중치가 높을수록 더 진하게
            if max_weight > min_weight:
                alpha = 0.1 + (weight - min_weight) / (max_weight - min_weight) * 0.4
            else:
                alpha = 0.3
            edge_alphas.append(min(alpha, 0.5))  # 최대 0.5로 제한
    else:
        edge_widths = [0.5] * G_filtered.number_of_edges()
        edge_alphas = [0.2] * G_filtered.number_of_edges()
    
    # 노드 색상 (degree에 따른 그라데이션)
    node_colors = []
    for node in G_filtered.nodes():
        degree = degrees[node]
        if max_degree_val > min_degree_val:
            normalized = (degree - min_degree_val) / (max_degree_val - min_degree_val)
            # 파란색 계열 그라데이션 (연한 파란색 -> 진한 파란색)
            r = 0.2 + normalized * 0.3
            g = 0.4 + normalized * 0.4
            b = 0.8 + normalized * 0.2
            node_colors.append((r, g, b))
        else:
            node_colors.append((0.4, 0.6, 1.0))
    
    # 그래프 그리기
    print("\n그래프 그리기 중...")
    fig, ax = plt.subplots(figsize=figsize, facecolor='white', dpi=100)
    
    # 엣지 그리기 (먼저 그려서 노드 뒤에 배치)
    nx.draw_networkx_edges(G_filtered, pos, 
                          width=edge_widths,
                          alpha=edge_alphas,
                          edge_color='gray',
                          ax=ax,
                          style='solid')
    
    # 노드 그리기
    nx.draw_networkx_nodes(G_filtered, pos,
                           node_size=node_sizes,
                           node_color=node_colors,
                           alpha=0.8,
                           ax=ax,
                           linewidths=0.5,
                           edgecolors='black')
    
    # 레이블 표시 (degree가 높은 노드만 표시하여 가독성 향상)
    # 상위 10% 노드만 레이블 표시
    sorted_nodes_by_degree = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
    top_n = max(20, int(len(sorted_nodes_by_degree) * 0.1))  # 최소 20개
    nodes_to_label = {node for node, _ in sorted_nodes_by_degree[:top_n]}
    
    labels = {node: node if node in nodes_to_label else '' 
              for node in G_filtered.nodes()}
    
    nx.draw_networkx_labels(G_filtered, pos,
                           labels=labels,
                           font_size=8,
                           font_family='Malgun Gothic',
                           ax=ax,
                           font_weight='bold')
    
    # 제목 및 통계 정보
    title = f"Skill-Skill Network\n"
    title += f"Nodes: {G_filtered.number_of_nodes()}, Edges: {G_filtered.number_of_edges()}\n"
    title += f"Node size ∝ Degree, Layout: Spring (k={k})"
    
    ax.set_title(title, fontsize=16, pad=20)
    ax.axis('off')
    
    # 저장
    print(f"\n이미지 저장 중: {output_file}")
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"  ✓ 저장 완료: {output_file}")
    
    # 상위 degree 노드 출력
    print(f"\n상위 10개 노드 (by degree):")
    for i, (node, degree) in enumerate(sorted_nodes_by_degree[:10], 1):
        print(f"  {i:2d}. {node:30s} (degree: {degree:3d})")
    
    plt.close()


def main():
    """메인 함수"""
    print("="*60)
    print("Skill-Skill Network Visualization")
    print("="*60)
    
    # 현재 스크립트가 있는 디렉토리로 이동
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 네트워크 파일 경로
    net_file = 'skill_skill_network.net'
    if not os.path.exists(net_file):
        print(f"오류: '{net_file}' 파일을 찾을 수 없습니다.")
        return
    
    # 네트워크 로딩
    G = read_pajek_net(net_file)
    
    # 시각화
    output_file = 'skill_skill_network_visualization.png'
    visualize_skill_network(G, output_file, figsize=(40, 30), min_degree=1)
    
    print("\n" + "="*60)
    print("완료!")
    print("="*60)


if __name__ == "__main__":
    main()

