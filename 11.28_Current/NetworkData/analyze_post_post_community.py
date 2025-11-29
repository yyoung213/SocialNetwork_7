"""
Post-Post 네트워크 군집 분석 (Community Detection) 스크립트

분석 내용:
1. Louvain 알고리즘을 사용한 커뮤니티 탐지
2. 각 군집을 직군 관점으로 해석
3. 직군별 경계 명확성 검증
4. 군집 시각화
5. 결과 및 인사이트 정리
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import defaultdict, Counter
from pathlib import Path

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
plt.rcParams['axes.unicode_minus'] = False


def parse_pajek_network(file_path):
    """Pajek 형식의 네트워크 파일을 파싱합니다."""
    print(f"[1단계] Pajek 네트워크 파일 파싱: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 헤더 파싱
    header = lines[0].strip()
    parts = header.split()
    n_nodes = int(parts[1])
    
    print(f"  노드 수: {n_nodes}")
    
    # 노드 정보 파싱
    nodes = {}  # {node_id: node_label}
    
    i = 1
    for idx in range(n_nodes):
        if i >= len(lines):
            break
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        parts = line.split('"')
        if len(parts) >= 2:
            node_id = int(parts[0].strip())
            node_label = parts[1].strip()
            nodes[node_id] = node_label
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
            u = int(parts[0])
            v = int(parts[1])
            weight = int(parts[2]) if len(parts) >= 3 else 1
            if u in nodes and v in nodes:
                edges.append((u, v, weight))
        i += 1
    
    print(f"  엣지 수: {len(edges)}")
    
    return nodes, edges


def create_network_from_pajek(nodes, edges):
    """Pajek 데이터로부터 NetworkX 그래프를 생성합니다."""
    print(f"[2단계] NetworkX 그래프 생성")
    
    G = nx.Graph()
    
    # 노드 추가
    for node_id, node_label in nodes.items():
        # job_id에서 직군 정보 추출 (예: "BI 엔지니어_1" -> "BI 엔지니어")
        job_type = node_label.split('_')[0] if '_' in node_label else node_label
        G.add_node(node_id, label=node_label, job_type=job_type)
    
    # 엣지 추가
    for u, v, weight in edges:
        G.add_edge(u, v, weight=weight)
    
    print(f"  그래프 노드 수: {G.number_of_nodes()}")
    print(f"  그래프 엣지 수: {G.number_of_edges()}")
    
    return G


def filter_network_by_weight(G, min_weight=1):
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
    
    print(f"  필터링 후: {G_filtered.number_of_nodes()}개 노드, {G_filtered.number_of_edges()}개 엣지")
    
    return G_filtered


def detect_communities(G, resolution=1.0, randomize=True):
    """
    Louvain 알고리즘을 사용하여 커뮤니티를 탐지합니다.
    Gephi와 동일한 설정으로 구현:
    - Algorithm: Louvain (Blondel et al. 2008)
    - Resolution: 1.0
    - Randomize: On
    - Use edge weights: On
    """
    print(f"[4단계] Louvain 알고리즘으로 커뮤니티 탐지 (Gephi 설정)")
    print(f"  Resolution: {resolution}")
    print(f"  Randomize: {randomize}")
    print(f"  Use edge weights: On")
    
    # NetworkX의 louvain_communities 사용 (Gephi와 동일한 알고리즘)
    seed = None if randomize else 42
    
    communities_list = list(nx.community.louvain_communities(
        G, 
        weight='weight',      # Use edge weights: On
        resolution=resolution,  # Resolution: 1.0
        seed=seed             # Randomize: On (None이면 랜덤)
    ))
    
    # partition 형식으로 변환
    partition = {}
    for comm_id, comm_nodes in enumerate(communities_list):
        for node in comm_nodes:
            partition[node] = comm_id
    
    # 커뮤니티별 노드 그룹화
    communities = defaultdict(list)
    for node, comm_id in partition.items():
        communities[comm_id].append(node)
    
    # 모듈성 계산 (resolution 포함)
    modularity = nx.community.modularity(G, communities_list, weight='weight', resolution=resolution)
    
    # 커뮤니티를 크기순으로 정렬
    communities_sorted = sorted(communities.items(), key=lambda x: len(x[1]), reverse=True)
    
    print(f"  탐지된 커뮤니티 개수: {len(communities)}")
    for i, (comm_id, nodes) in enumerate(communities_sorted[:10], 1):  # 상위 10개만 출력
        print(f"    커뮤니티 {i}: {len(nodes)}개 노드")
    if len(communities) > 10:
        print(f"    ... (총 {len(communities)}개 커뮤니티)")
    
    print(f"  모듈성 (Modularity): {modularity:.4f}")
    
    return partition, communities_sorted, modularity


def analyze_community_job_types(G, communities_sorted):
    """각 커뮤니티의 직군 구성을 분석합니다."""
    print(f"[5단계] 커뮤니티별 직군 구성 분석")
    
    community_analysis = []
    
    for comm_id, nodes in communities_sorted:
        # 커뮤니티 내 공고들의 직군 추출
        job_types = [G.nodes[n].get('job_type', 'Unknown') for n in nodes]
        job_type_counts = Counter(job_types)
        
        # 가장 많은 직군
        most_common_job_type = job_type_counts.most_common(1)[0]
        dominant_job_type = most_common_job_type[0]
        dominant_count = most_common_job_type[1]
        dominance_ratio = dominant_count / len(nodes) if nodes else 0
        
        # 직군 다양성 (Shannon entropy)
        total = len(job_types)
        if total > 0:
            proportions = [count / total for count in job_type_counts.values()]
            entropy = -sum(p * np.log2(p) for p in proportions if p > 0)
            max_entropy = np.log2(len(job_type_counts))
            normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        else:
            normalized_entropy = 0
        
        community_analysis.append({
            'community_id': comm_id,
            'size': len(nodes),
            'dominant_job_type': dominant_job_type,
            'dominance_ratio': dominance_ratio,
            'job_type_distribution': dict(job_type_counts),
            'job_type_diversity': normalized_entropy,  # 0=단일 직군, 1=다양한 직군
            'num_job_types': len(job_type_counts)
        })
        
        print(f"  커뮤니티 {comm_id}: {dominant_job_type} ({len(nodes)}개, 지배도: {dominance_ratio:.2f}, 다양성: {normalized_entropy:.2f})")
    
    return community_analysis


def visualize_communities(G, partition, output_path, communities_sorted):
    """커뮤니티별로 색상을 구분하여 네트워크를 시각화합니다."""
    print(f"[6단계] 커뮤니티 시각화")
    
    # 네트워크가 너무 크면 샘플링
    if G.number_of_nodes() > 1000:
        print(f"  경고: 네트워크가 너무 큽니다 ({G.number_of_nodes()}개 노드). 시각화를 위해 샘플링합니다.")
        # 가장 큰 연결 성분만 사용
        largest_cc = max(nx.connected_components(G), key=len)
        G = G.subgraph(largest_cc).copy()
        partition = {n: partition[n] for n in G.nodes() if n in partition}
        print(f"  샘플링 후: {G.number_of_nodes()}개 노드")
    
    fig, ax = plt.subplots(figsize=(28, 22))
    
    # 커뮤니티별 노드 그룹화
    communities = defaultdict(list)
    for node, comm_id in partition.items():
        if node in G:
            communities[comm_id].append(node)
    
    # 커뮤니티를 크기순으로 정렬
    communities_sorted_filtered = sorted(communities.items(), key=lambda x: len(x[1]), reverse=True)
    
    # 색상 팔레트 생성
    colors = plt.cm.Set3(np.linspace(0, 1, len(communities)))
    color_map = {comm_id: colors[i] for i, (comm_id, _) in enumerate(communities_sorted_filtered)}
    
    # Spring Layout
    print(f"  Spring layout 계산 중... (노드 수: {G.number_of_nodes()})")
    k = 3 / np.sqrt(G.number_of_nodes())
    pos = nx.spring_layout(G, k=k, iterations=300, seed=42)
    
    # 엣지 그리기
    edges = G.edges(data=True)
    edge_weights = [d.get('weight', 1) for u, v, d in edges]
    
    if edge_weights:
        min_weight_val = min(edge_weights)
        max_weight_val = max(edge_weights)
        min_width = 0.1
        max_width = 1.5
        
        def width_func(weight):
            if max_weight_val == min_weight_val:
                return (min_width + max_width) / 2
            normalized = (weight - min_weight_val) / (max_weight_val - min_weight_val)
            return min_width + (max_width - min_width) * normalized
    else:
        def width_func(weight):
            return 0.5
    
    edge_widths = [width_func(w) for w in edge_weights]
    
    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.1, 
                          edge_color='lightgray', ax=ax)
    
    # 커뮤니티별로 노드 그리기
    for comm_id, nodes in communities_sorted_filtered:
        nodes_in_graph = [n for n in nodes if n in G]
        if not nodes_in_graph:
            continue
        color = color_map[comm_id]
        node_sizes = [200 for _ in nodes_in_graph]
        
        nx.draw_networkx_nodes(G, pos, nodelist=nodes_in_graph,
                              node_size=node_sizes,
                              node_color=[color], alpha=0.8,
                              edgecolors='black', linewidths=0.5, ax=ax)
    
    # 범례 생성
    legend_elements = []
    for i, (comm_id, nodes) in enumerate(communities_sorted_filtered[:15], 1):  # 상위 15개만
        nodes_in_graph = [n for n in nodes if n in G]
        if not nodes_in_graph:
            continue
        color = color_map[comm_id]
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                        markerfacecolor=color, markersize=12,
                                        label=f'커뮤니티 {i} ({len(nodes_in_graph)}개)'))
    
    ax.legend(handles=legend_elements, loc='upper left', fontsize=9, 
             framealpha=0.9, title='커뮤니티 구분', title_fontsize=11)
    
    ax.set_title('Post-Post 네트워크 커뮤니티 탐지 결과\n'
                 f'Louvain 알고리즘, {len(communities)}개 커뮤니티 탐지', 
                 fontsize=20, pad=25, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  저장 완료: {output_path}")
    plt.close()


def create_analysis_markdown(G, partition, communities_sorted, modularity, 
                            community_analysis, output_path):
    """군집 분석 결과를 마크다운 파일로 생성합니다."""
    print(f"[7단계] 분석 문서 생성: {output_path}")
    
    # 직군별 경계 명확성 평가
    avg_dominance = np.mean([c['dominance_ratio'] for c in community_analysis])
    avg_diversity = np.mean([c['job_type_diversity'] for c in community_analysis])
    
    markdown_content = f"""# Post-Post 네트워크 군집 분석 (Community Detection)

## 개요
본 문서는 Post-Post One-mode Projection 네트워크에 대한 커뮤니티 탐지 분석 결과를 정리합니다.
- 전체 네트워크 규모: {G.number_of_nodes()}개 노드, {G.number_of_edges()}개 엣지
- 알고리즘: Louvain 알고리즘 (Blondel et al. 2008) - Gephi와 동일한 설정
- **알고리즘 파라미터**:
  - Resolution: 1.0
  - Randomize: On
  - Use edge weights: On
- 모듈성 (Modularity): {modularity:.4f}

---

## 1. 커뮤니티 탐지 알고리즘: Louvain (Gephi 설정)

### 알고리즘 개요
**Louvain 알고리즘**은 모듈성(Modularity) 최적화를 기반으로 한 커뮤니티 탐지 알고리즘입니다.
본 분석은 **Gephi와 동일한 설정**으로 수행되었습니다.

**참고 문헌**: 
- Vincent D Blondel, Jean-Loup Guillaume, Renaud Lambiotte, Etienne Lefebvre, 
  "Fast unfolding of communities in large networks", 
  Journal of Statistical Mechanics: Theory and Experiment 2008 (10), P1000

### 알고리즘 파라미터 (Gephi 설정)
- **Resolution**: 1.0
  - 해상도 파라미터는 커뮤니티 크기를 조절합니다.
  - 값이 클수록 더 작은 커뮤니티를 생성합니다.
  - 1.0은 기본값으로, 네트워크의 자연스러운 커뮤니티 구조를 탐지합니다.
- **Randomize**: On
  - 노드 처리 순서를 랜덤화하여 다양한 초기 조건에서 최적화를 수행합니다.
  - 이는 더 나은 모듈성을 찾을 수 있게 해줍니다.
- **Use edge weights**: On
  - 엣지 가중치를 고려하여 커뮤니티를 탐지합니다.
  - 가중치가 높은 연결을 더 중요하게 고려합니다.

---

## 2. 탐지된 커뮤니티 요약

- **총 커뮤니티 개수**: {len(communities_sorted)}개
- **평균 커뮤니티 크기**: {np.mean([len(nodes) for _, nodes in communities_sorted]):.1f}개 노드
- **최대 커뮤니티 크기**: {max([len(nodes) for _, nodes in communities_sorted])}개 노드
- **최소 커뮤니티 크기**: {min([len(nodes) for _, nodes in communities_sorted])}개 노드

### 상위 20개 커뮤니티

| 순위 | 커뮤니티 ID | 크기 | 주요 직군 | 지배도 | 직군 다양성 | 직군 수 |
|------|------------|------|----------|--------|------------|---------|
"""
    
    for i, analysis in enumerate(community_analysis[:20], 1):
        comm_id = analysis['community_id']
        size = analysis['size']
        dominant = analysis['dominant_job_type']
        dominance = analysis['dominance_ratio']
        diversity = analysis['job_type_diversity']
        num_types = analysis['num_job_types']
        
        markdown_content += f"| {i} | {comm_id} | {size} | {dominant} | {dominance:.2f} | {diversity:.2f} | {num_types} |\n"
    
    markdown_content += f"""
---

## 3. 직군별 경계 명확성 분석

### 전체 평가 지표
- **평균 지배도 (Average Dominance Ratio)**: {avg_dominance:.3f}
  - 각 커뮤니티에서 가장 많은 직군이 차지하는 비율의 평균
  - 값이 1에 가까울수록 커뮤니티가 단일 직군으로 구성됨을 의미
- **평균 직군 다양성 (Average Job Type Diversity)**: {avg_diversity:.3f}
  - 각 커뮤니티 내 직군의 다양성을 나타내는 지표 (Shannon Entropy 기반)
  - 값이 0에 가까울수록 단일 직군, 1에 가까울수록 다양한 직군이 혼재

### 해석
"""
    
    if avg_dominance > 0.7:
        markdown_content += f"- **직군 경계가 비교적 명확함**: 평균 지배도가 {avg_dominance:.3f}로 높아, 대부분의 커뮤니티가 특정 직군으로 지배되고 있습니다.\n"
    elif avg_dominance > 0.5:
        markdown_content += f"- **직군 경계가 중간 수준**: 평균 지배도가 {avg_dominance:.3f}로, 일부 커뮤니티는 단일 직군으로 구성되지만 일부는 혼재되어 있습니다.\n"
    else:
        markdown_content += f"- **직군 경계가 모호함**: 평균 지배도가 {avg_dominance:.3f}로 낮아, 대부분의 커뮤니티가 여러 직군이 혼재되어 있습니다.\n"
    
    if avg_diversity < 0.3:
        markdown_content += f"- **직군 다양성이 낮음**: 평균 다양성이 {avg_diversity:.3f}로 낮아, 각 커뮤니티가 주로 단일 직군으로 구성되어 있습니다.\n"
    elif avg_diversity < 0.6:
        markdown_content += f"- **직군 다양성이 중간 수준**: 평균 다양성이 {avg_diversity:.3f}로, 일부 커뮤니티는 단일 직군, 일부는 여러 직군이 혼재되어 있습니다.\n"
    else:
        markdown_content += f"- **직군 다양성이 높음**: 평균 다양성이 {avg_diversity:.3f}로 높아, 대부분의 커뮤니티가 여러 직군이 혼재되어 있습니다.\n"
    
    markdown_content += f"""
---

## 4. 상위 커뮤니티 상세 분석

"""
    
    for i, analysis in enumerate(community_analysis[:10], 1):
        comm_id = analysis['community_id']
        size = analysis['size']
        dominant = analysis['dominant_job_type']
        dominance = analysis['dominance_ratio']
        diversity = analysis['job_type_diversity']
        job_type_dist = analysis['job_type_distribution']
        
        markdown_content += f"""### 커뮤니티 {i} (ID: {comm_id})

- **크기**: {size}개 공고
- **주요 직군**: {dominant} ({dominance:.1%})
- **직군 다양성**: {diversity:.3f}
- **직군 구성**:
"""
        for job_type, count in sorted(job_type_dist.items(), key=lambda x: x[1], reverse=True)[:5]:
            ratio = count / size
            markdown_content += f"  - {job_type}: {count}개 ({ratio:.1%})\n"
        
        markdown_content += "\n"
    
    markdown_content += f"""
---

## 5. 인사이트 및 결론

### 주요 발견사항
1. **커뮤니티 구조**: 총 {len(communities_sorted)}개의 커뮤니티가 탐지되었으며, 평균 크기는 {np.mean([len(nodes) for _, nodes in communities_sorted]):.1f}개 공고입니다.

2. **직군 경계**: 
"""
    
    if avg_dominance > 0.7:
        markdown_content += "   - 직군별 경계가 비교적 명확하게 나타나고 있습니다.\n"
        markdown_content += "   - 대부분의 커뮤니티가 특정 직군의 공고들로 구성되어 있어, 직군별데이터_raw의 분류가 실제 네트워크 구조와 일치합니다.\n"
    elif avg_dominance > 0.5:
        markdown_content += "   - 직군별 경계가 부분적으로 나타나고 있습니다.\n"
        markdown_content += "   - 일부 커뮤니티는 단일 직군으로 구성되지만, 일부는 여러 직군이 혼재되어 있습니다.\n"
        markdown_content += "   - 이는 일부 직군들이 유사한 스킬을 요구하거나, 직군 분류가 완전히 명확하지 않을 수 있음을 시사합니다.\n"
    else:
        markdown_content += "   - 직군별 경계가 모호하게 나타나고 있습니다.\n"
        markdown_content += "   - 대부분의 커뮤니티가 여러 직군이 혼재되어 있어, 직군별데이터_raw의 분류와 실제 네트워크 구조 간에 차이가 있습니다.\n"
        markdown_content += "   - 이는 직군들이 유사한 스킬을 요구하거나, 직군 분류 기준을 재검토할 필요가 있음을 시사합니다.\n"
    
    markdown_content += f"""
3. **모듈성**: {modularity:.4f}의 모듈성을 보여주며, 이는 네트워크가 명확한 커뮤니티 구조를 가지고 있음을 의미합니다.

### 시사점
- 공고-공고 네트워크의 군집분석을 통해 직군별 경계의 명확성을 검증할 수 있습니다.
- 직군별데이터_raw의 분류가 실제 네트워크 구조와 일치하는지 확인할 수 있습니다.
- 유사한 스킬을 요구하는 공고들이 실제로 같은 커뮤니티로 묶이는지 확인할 수 있습니다.

---
*본 분석은 NetworkX의 Louvain 알고리즘을 사용하여 수행되었습니다.*
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"  저장 완료: {output_path}")


def main():
    """메인 함수"""
    print("=" * 70)
    print("Post-Post 네트워크 군집 분석 (Community Detection)")
    print("=" * 70)
    
    # 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'post_post_network.net')
    
    # 출력 폴더 생성
    output_dir = os.path.join(os.path.dirname(script_dir), 'post_post_network_CommunityDetect')
    os.makedirs(output_dir, exist_ok=True)
    
    output_viz = os.path.join(output_dir, 'community_detection_visualization.png')
    output_md = os.path.join(output_dir, 'CommunityDetect_Analysis.md')
    
    # 1단계: Pajek 파일 파싱
    nodes, edges = parse_pajek_network(input_file)
    
    # 2단계: NetworkX 그래프 생성
    G = create_network_from_pajek(nodes, edges)
    
    # 3단계: 가중치 필터링 (선택적)
    # G = filter_network_by_weight(G, min_weight=1)
    
    # 4단계: 커뮤니티 탐지
    partition, communities_sorted, modularity = detect_communities(G, resolution=1.0, randomize=True)
    
    # 5단계: 커뮤니티별 직군 분석
    community_analysis = analyze_community_job_types(G, communities_sorted)
    
    # 6단계: 시각화
    visualize_communities(G, partition, output_viz, communities_sorted)
    
    # 7단계: 분석 문서 생성
    create_analysis_markdown(G, partition, communities_sorted, modularity, 
                            community_analysis, output_md)
    
    print("\n" + "=" * 70)
    print("작업 완료!")
    print(f"출력 폴더: {output_dir}")
    print("=" * 70)


if __name__ == '__main__':
    main()

