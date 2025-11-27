"""
Skill-Skill Network 심층 분석
- Max-Component 특징
- PDF와 CCDF 시각화
- Degree Distribution 계산
- Power Law 분석 (허브 존재 파악)
- 노드 속성 기반 시각화
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import os
import warnings
warnings.filterwarnings('ignore')


def read_skill_network(file_path: str = 'skill_skill_network.net'):
    """
    Pajek .net 파일을 읽어 NetworkX 그래프로 변환합니다.
    """
    print(f"네트워크 파일 로딩 중: {file_path}")
    
    G = nx.Graph()
    node_id_to_label = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Vertices 섹션 읽기
    vertices_started = False
    edges_started = False
    node_id = 1
    
    for line in lines:
        line_stripped = line.strip()
        
        if line_stripped.startswith('*Vertices'):
            vertices_started = True
            continue
        
        if line_stripped.startswith('*Edges') or line_stripped.startswith('*Arcs'):
            vertices_started = False
            edges_started = True
            continue
        
        # Vertices 읽기
        if vertices_started and line_stripped and not line_stripped.startswith('*'):
            if '"' in line_stripped:
                parts = line_stripped.split('"', 2)
                if len(parts) >= 2:
                    label = parts[1].strip()
                    node_id_to_label[node_id] = label
                    G.add_node(node_id, label=label)
                    node_id += 1
        
        # Edges 읽기
        if edges_started and line_stripped and not line_stripped.startswith('*'):
            parts = line_stripped.split()
            if len(parts) >= 2:
                try:
                    source_id = int(parts[0])
                    target_id = int(parts[1])
                    weight = float(parts[2]) if len(parts) >= 3 else 1.0
                    
                    if source_id in node_id_to_label and target_id in node_id_to_label:
                        G.add_edge(source_id, target_id, weight=weight)
                except (ValueError, IndexError):
                    continue
    
    print(f"  노드 수: {G.number_of_nodes()}개")
    print(f"  엣지 수: {G.number_of_edges()}개")
    
    return G, node_id_to_label


def analyze_max_component(G, node_id_to_label):
    """
    Max-Component (최대 연결 성분) 특징 분석
    """
    print("\n" + "="*60)
    print("1. Max-Component 특징 분석")
    print("="*60)
    
    # 연결 성분 찾기
    components = list(nx.connected_components(G))
    components_sorted = sorted(components, key=len, reverse=True)
    
    max_component = components_sorted[0]
    max_component_graph = G.subgraph(max_component)
    
    print(f"\n연결 성분 통계:")
    print(f"  총 연결 성분 수: {len(components)}개")
    print(f"  최대 연결 성분 크기: {len(max_component)}개 노드 ({len(max_component)/G.number_of_nodes()*100:.1f}%)")
    print(f"  최대 연결 성분 엣지 수: {max_component_graph.number_of_edges()}개")
    
    # Max-Component의 기본 통계
    degrees = dict(max_component_graph.degree())
    degree_values = list(degrees.values())
    
    print(f"\nMax-Component 통계:")
    print(f"  평균 Degree: {np.mean(degree_values):.2f}")
    print(f"  최대 Degree: {max(degree_values)}")
    print(f"  최소 Degree: {min(degree_values)}")
    print(f"  밀도: {nx.density(max_component_graph):.4f}")
    print(f"  평균 클러스터링 계수: {nx.average_clustering(max_component_graph):.4f}")
    
    # Max-Component의 상위 노드
    sorted_degrees = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
    print(f"\nMax-Component 상위 10개 노드:")
    for i, (node_id, deg) in enumerate(sorted_degrees[:10], 1):
        label = node_id_to_label.get(node_id, f"Node {node_id}")
        print(f"  {i:2d}. {label:30s} (degree: {deg:3d})")
    
    return max_component_graph, components


def plot_degree_distributions(G, output_dir='.'):
    """
    2. PDF와 CCDF 시각화
    3. Degree Distribution 계산 및 CDF 분석
    """
    print("\n" + "="*60)
    print("2-3. Degree Distribution 분석 (PDF, CCDF, CDF)")
    print("="*60)
    
    # 한글 폰트 설정
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    # Degree 계산
    degrees = dict(G.degree())
    degree_values = list(degrees.values())
    
    # Degree 분포 (빈도)
    degree_counter = Counter(degree_values)
    degree_counts = sorted(degree_counter.items())
    degrees_sorted = [d for d, _ in degree_counts]
    counts = [c for _, c in degree_counts]
    
    # PDF (Probability Density Function)
    total_nodes = len(degree_values)
    pdf = [c / total_nodes for c in counts]
    
    # CDF (Cumulative Distribution Function)
    cdf = np.cumsum(pdf)
    
    # CCDF (Complementary CDF = 1 - CDF)
    ccdf = 1 - cdf
    
    # 로그 스케일 데이터 준비 (0 제외)
    degrees_log = [d for d in degrees_sorted if d > 0]
    pdf_log = [p for d, p in zip(degrees_sorted, pdf) if d > 0]
    cdf_log = [c for d, c in zip(degrees_sorted, cdf) if d > 0]
    ccdf_log = [c for d, c in zip(degrees_sorted, ccdf) if d > 0]
    
    # 시각화
    fig = plt.figure(figsize=(20, 12))
    
    # 1. PDF (선형 스케일)
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(degrees_sorted, pdf, 'b-', marker='o', markersize=3, linewidth=1.5)
    ax1.set_xlabel('Degree (k)', fontsize=12)
    ax1.set_ylabel('P(k)', fontsize=12)
    ax1.set_title('PDF: Degree Distribution (Linear Scale)', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 2. PDF (로그 스케일)
    ax2 = plt.subplot(2, 3, 2)
    ax2.loglog(degrees_log, pdf_log, 'b-', marker='o', markersize=3, linewidth=1.5)
    ax2.set_xlabel('Degree (k)', fontsize=12)
    ax2.set_ylabel('P(k)', fontsize=12)
    ax2.set_title('PDF: Degree Distribution (Log-Log Scale)', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 3. CCDF (선형 스케일)
    ax3 = plt.subplot(2, 3, 3)
    ax3.plot(degrees_sorted, ccdf, 'r-', marker='s', markersize=3, linewidth=1.5)
    ax3.set_xlabel('Degree (k)', fontsize=12)
    ax3.set_ylabel('P(K ≥ k)', fontsize=12)
    ax3.set_title('CCDF: Complementary CDF (Linear Scale)', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 4. CCDF (로그 스케일) - Power Law 확인용
    ax4 = plt.subplot(2, 3, 4)
    ax4.loglog(degrees_log, ccdf_log, 'r-', marker='s', markersize=3, linewidth=1.5)
    ax4.set_xlabel('Degree (k)', fontsize=12)
    ax4.set_ylabel('P(K ≥ k)', fontsize=12)
    ax4.set_title('CCDF: Complementary CDF (Log-Log Scale)\nPower Law 확인', 
                  fontsize=13, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # Power Law 피팅 (선형 부분)
    power_law_exponent = None
    if len(degrees_log) > 10:
        try:
            # 높은 degree 부분만 사용 (tail 부분)
            tail_start = len(degrees_log) // 3  # 하위 1/3 제외
            degrees_tail = degrees_log[tail_start:]
            ccdf_tail = ccdf_log[tail_start:]
            
            # 0이나 음수 제거
            valid_idx = [i for i, (d, c) in enumerate(zip(degrees_tail, ccdf_tail)) 
                        if d > 0 and c > 0]
            if len(valid_idx) > 5:
                degrees_tail = [degrees_tail[i] for i in valid_idx]
                ccdf_tail = [ccdf_tail[i] for i in valid_idx]
                
                # 로그 공간에서 선형 회귀
                log_degrees = np.log(degrees_tail)
                log_ccdf = np.log(ccdf_tail)
                
                # 선형 피팅
                coeffs = np.polyfit(log_degrees, log_ccdf, 1)
                power_law_exponent = -coeffs[0]  # 음의 기울기
                
                # 피팅된 선 그리기
                fit_degrees = np.logspace(np.log10(degrees_tail[0]), np.log10(degrees_tail[-1]), 100)
                fit_ccdf = np.exp(coeffs[1]) * (fit_degrees ** coeffs[0])
                ax4.plot(fit_degrees, fit_ccdf, 'g--', linewidth=2, 
                        label=f'Power Law Fit: γ ≈ {power_law_exponent:.2f}')
                ax4.legend()
                
                print(f"\nPower Law 분석:")
                print(f"  추정 지수 (γ): {power_law_exponent:.2f}")
                print(f"  Power Law 형태: P(K ≥ k) ~ k^(-γ)")
                if power_law_exponent > 1:
                    print(f"  → 허브 노드 존재 (높은 degree 노드가 예상보다 많음)")
                elif power_law_exponent > 0:
                    print(f"  → 약한 Power Law (허브 노드가 일부 존재)")
                else:
                    print(f"  → Power Law 특성이 약함")
        except Exception as e:
            print(f"\nPower Law 피팅 실패: {e}")
            print(f"  → CCDF 그래프에서 수동으로 Power Tail 확인 필요")
    
    # 5. CDF (선형 스케일)
    ax5 = plt.subplot(2, 3, 5)
    ax5.plot(degrees_sorted, cdf, 'g-', marker='^', markersize=3, linewidth=1.5)
    ax5.set_xlabel('Degree (k)', fontsize=12)
    ax5.set_ylabel('P(K ≤ k)', fontsize=12)
    ax5.set_title('CDF: Cumulative Distribution Function', fontsize=13, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # 6. CDF (로그 스케일) - Power Tail 확인
    ax6 = plt.subplot(2, 3, 6)
    ax6.semilogx(degrees_log, cdf_log, 'g-', marker='^', markersize=3, linewidth=1.5)
    ax6.set_xlabel('Degree (k) [Log Scale]', fontsize=12)
    ax6.set_ylabel('P(K ≤ k)', fontsize=12)
    ax6.set_title('CDF: Cumulative Distribution (Log X-axis)\nPower Tail 확인', 
                  fontsize=13, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    
    # Power Tail 영역 강조
    if len(degrees_log) > 10:
        tail_threshold = degrees_log[len(degrees_log) * 2 // 3]  # 상위 1/3
        tail_idx = next((i for i, d in enumerate(degrees_log) if d >= tail_threshold), len(degrees_log))
        if tail_idx < len(degrees_log):
            ax6.axvspan(degrees_log[tail_idx], degrees_log[-1], alpha=0.2, color='red', 
                       label='Power Tail 영역')
            ax6.legend()
    
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'degree_distribution_analysis.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"\n  [OK] 저장 완료: {output_file}")
    
    # 통계 출력
    print(f"\nDegree Distribution 통계:")
    print(f"  평균 Degree: {np.mean(degree_values):.2f}")
    print(f"  중앙값 Degree: {np.median(degree_values):.2f}")
    print(f"  최대 Degree: {max(degree_values)}")
    print(f"  최소 Degree: {min(degree_values)}")
    print(f"  표준편차: {np.std(degree_values):.2f}")
    
    return degree_values, power_law_exponent if 'power_law_exponent' in locals() else None


def visualize_with_node_attributes(G, node_id_to_label, degree_values, output_dir='.'):
    """
    4. 노드 속성 정보를 활용한 네트워크 시각화
    (Zachary's Karate Club Network 스타일)
    """
    print("\n" + "="*60)
    print("4. 노드 속성 기반 네트워크 시각화")
    print("="*60)
    
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    # 노드 속성 계산
    degrees = dict(G.degree())
    
    # 중심성 지표 계산
    print("  중심성 지표 계산 중...")
    betweenness = nx.betweenness_centrality(G)
    closeness = nx.closeness_centrality(G)
    eigenvector = nx.eigenvector_centrality(G, max_iter=1000)
    
    # 클러스터링 계수
    clustering = nx.clustering(G)
    
    # 노드 속성을 그래프에 추가
    for node in G.nodes():
        G.nodes[node]['degree'] = degrees[node]
        G.nodes[node]['betweenness'] = betweenness[node]
        G.nodes[node]['closeness'] = closeness[node]
        G.nodes[node]['eigenvector'] = eigenvector[node]
        G.nodes[node]['clustering'] = clustering[node]
    
    # 시각화: 여러 속성 기반
    fig = plt.figure(figsize=(24, 18))
    
    # 레이아웃 계산 (한 번만)
    print("  레이아웃 계산 중... (시간이 걸릴 수 있습니다)")
    pos = nx.spring_layout(G, k=3, iterations=300, seed=42)
    
    # 1. Degree 기반 색상 및 크기
    ax1 = plt.subplot(2, 3, 1)
    node_colors1 = [degrees[n] for n in G.nodes()]
    node_sizes1 = [max(50, degrees[n] * 3) for n in G.nodes()]
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors1, node_size=node_sizes1,
                          cmap='YlOrRd', alpha=0.8, ax=ax1, edgecolors='black', linewidths=0.5)
    nx.draw_networkx_edges(G, pos, alpha=0.1, width=0.3, ax=ax1, edge_color='gray')
    
    # 상위 노드 레이블
    top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]
    labels1 = {n: node_id_to_label.get(n, f"Node {n}") for n, _ in top_nodes}
    nx.draw_networkx_labels(G, pos, labels1, font_size=7, ax=ax1, font_weight='bold')
    
    ax1.set_title('Degree 기반 시각화\n(색상/크기 ∝ Degree)', fontsize=12, fontweight='bold')
    ax1.axis('off')
    
    # 2. Betweenness Centrality 기반
    ax2 = plt.subplot(2, 3, 2)
    node_colors2 = [betweenness[n] for n in G.nodes()]
    node_sizes2 = [max(50, betweenness[n] * 5000) for n in G.nodes()]
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors2, node_size=node_sizes2,
                          cmap='viridis', alpha=0.8, ax=ax2, edgecolors='black', linewidths=0.5)
    nx.draw_networkx_edges(G, pos, alpha=0.1, width=0.3, ax=ax2, edge_color='gray')
    
    top_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:10]
    labels2 = {n: node_id_to_label.get(n, f"Node {n}") for n, _ in top_betweenness}
    nx.draw_networkx_labels(G, pos, labels2, font_size=7, ax=ax2, font_weight='bold')
    
    ax2.set_title('Betweenness Centrality 기반\n(브로커 역할 강조)', fontsize=12, fontweight='bold')
    ax2.axis('off')
    
    # 3. Clustering Coefficient 기반
    ax3 = plt.subplot(2, 3, 3)
    node_colors3 = [clustering[n] for n in G.nodes()]
    node_sizes3 = [max(50, degrees[n] * 2) for n in G.nodes()]
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors3, node_size=node_sizes3,
                          cmap='coolwarm', alpha=0.8, ax=ax3, edgecolors='black', linewidths=0.5)
    nx.draw_networkx_edges(G, pos, alpha=0.1, width=0.3, ax=ax3, edge_color='gray')
    
    ax3.set_title('Clustering Coefficient 기반\n(지역적 밀집도)', fontsize=12, fontweight='bold')
    ax3.axis('off')
    
    # 4. Eigenvector Centrality 기반
    ax4 = plt.subplot(2, 3, 4)
    node_colors4 = [eigenvector[n] for n in G.nodes()]
    node_sizes4 = [max(50, eigenvector[n] * 2000) for n in G.nodes()]
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors4, node_size=node_sizes4,
                          cmap='plasma', alpha=0.8, ax=ax4, edgecolors='black', linewidths=0.5)
    nx.draw_networkx_edges(G, pos, alpha=0.1, width=0.3, ax=ax4, edge_color='gray')
    
    top_eigenvector = sorted(eigenvector.items(), key=lambda x: x[1], reverse=True)[:10]
    labels4 = {n: node_id_to_label.get(n, f"Node {n}") for n, _ in top_eigenvector}
    nx.draw_networkx_labels(G, pos, labels4, font_size=7, ax=ax4, font_weight='bold')
    
    ax4.set_title('Eigenvector Centrality 기반\n(영향력 있는 노드와 연결)', fontsize=12, fontweight='bold')
    ax4.axis('off')
    
    # 5. Degree vs Clustering 산점도
    ax5 = plt.subplot(2, 3, 5)
    deg_values = [degrees[n] for n in G.nodes()]
    clust_values = [clustering[n] for n in G.nodes()]
    
    ax5.scatter(deg_values, clust_values, alpha=0.6, s=50, c=deg_values, cmap='YlOrRd')
    ax5.set_xlabel('Degree', fontsize=11)
    ax5.set_ylabel('Clustering Coefficient', fontsize=11)
    ax5.set_title('Degree vs Clustering Coefficient', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # 6. 허브 노드 강조 시각화
    ax6 = plt.subplot(2, 3, 6)
    
    # 허브 노드 정의: 상위 5% degree
    degree_threshold = np.percentile(degree_values, 95)
    hub_nodes = [n for n in G.nodes() if degrees[n] >= degree_threshold]
    
    node_colors6 = ['red' if n in hub_nodes else 'lightblue' for n in G.nodes()]
    node_sizes6 = [max(100, degrees[n] * 5) if n in hub_nodes else max(30, degrees[n] * 2) 
                   for n in G.nodes()]
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors6, node_size=node_sizes6,
                          alpha=0.8, ax=ax6, edgecolors='black', linewidths=0.5)
    nx.draw_networkx_edges(G, pos, alpha=0.1, width=0.3, ax=ax6, edge_color='gray')
    
    # 허브 노드 레이블
    hub_labels = {n: node_id_to_label.get(n, f"Node {n}") for n in hub_nodes[:15]}
    nx.draw_networkx_labels(G, pos, hub_labels, font_size=7, ax=ax6, 
                           font_weight='bold', font_color='darkred')
    
    ax6.set_title(f'허브 노드 강조\n(상위 5% Degree, {len(hub_nodes)}개)', 
                  fontsize=12, fontweight='bold')
    ax6.axis('off')
    
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'network_node_attributes_visualization.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"  [OK] 저장 완료: {output_file}")
    
    # 허브 노드 정보 출력
    print(f"\n허브 노드 (상위 5%, Degree ≥ {degree_threshold:.0f}):")
    hub_degrees = [(n, degrees[n]) for n in hub_nodes]
    hub_degrees_sorted = sorted(hub_degrees, key=lambda x: x[1], reverse=True)
    for i, (node_id, deg) in enumerate(hub_degrees_sorted[:10], 1):
        label = node_id_to_label.get(node_id, f"Node {node_id}")
        print(f"  {i:2d}. {label:30s} (degree: {deg:3d})")


def main():
    """메인 함수"""
    print("="*60)
    print("Skill-Skill Network 심층 분석")
    print("="*60)
    
    # 현재 디렉토리로 이동
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 네트워크 파일 경로
    net_file = 'skill_skill_network.net'
    if not os.path.exists(net_file):
        print(f"오류: '{net_file}' 파일을 찾을 수 없습니다.")
        return
    
    # 네트워크 로딩
    G, node_id_to_label = read_skill_network(net_file)
    
    # 1. Max-Component 분석
    try:
        max_comp_graph, components = analyze_max_component(G, node_id_to_label)
    except Exception as e:
        print(f"  ⚠ Max-Component 분석 중 오류: {e}")
        import traceback
        traceback.print_exc()
        max_comp_graph = G
        components = [set(G.nodes())]
    
    # 2-3. Degree Distribution 분석
    try:
        degree_values, power_law_exp = plot_degree_distributions(G)
    except Exception as e:
        print(f"  ⚠ Degree Distribution 분석 중 오류: {e}")
        import traceback
        traceback.print_exc()
        degree_values = list(dict(G.degree()).values())
        power_law_exp = None
    
    # 4. 노드 속성 기반 시각화
    try:
        visualize_with_node_attributes(G, node_id_to_label, degree_values)
    except Exception as e:
        print(f"  ⚠ 노드 속성 시각화 중 오류: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("분석 완료!")
    print("="*60)
    print("\n생성된 파일:")
    print("  - degree_distribution_analysis.png")
    print("  - network_node_attributes_visualization.png")


if __name__ == "__main__":
    main()

