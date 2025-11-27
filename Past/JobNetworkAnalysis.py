import pandas as pd
import os
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from collections import defaultdict
from typing import Dict, Set

def load_job_keywords(job_dict_dir: str = '직무별_키워드_사전') -> Dict[str, Set[str]]:
    """각 직군별 키워드 사전 로드"""
    job_keywords = {}
    
    # 직무별 키워드 사전 폴더의 모든 파일 찾기
    xlsx_files = [f for f in os.listdir(job_dict_dir) if f.endswith('.xlsx')]
    
    print(f"총 {len(xlsx_files)}개 직군 키워드 사전 파일 발견\n")
    
    for xlsx_file in xlsx_files:
        file_path = os.path.join(job_dict_dir, xlsx_file)
        # 파일명에서 직군명 추출 (예: "데이터 분석가_키워드_사전.xlsx" -> "데이터 분석가")
        job_name = xlsx_file.replace('_키워드_사전.xlsx', '')
        
        try:
            # 엑셀 파일 로드
            df = pd.read_excel(file_path)
            
            # 키워드 추출
            keywords = set()
            for _, row in df.iterrows():
                keyword = row['Keyword']
                if pd.notna(keyword):
                    keywords.add(str(keyword).strip())
            
            job_keywords[job_name] = keywords
            print(f"  {job_name}: {len(keywords)}개 키워드")
            
        except Exception as e:
            print(f"  ⚠ {job_name} 로드 실패: {e}")
            continue
    
    return job_keywords

def create_job_network(job_keywords: Dict[str, Set[str]], min_shared_keywords: int = 1) -> nx.Graph:
    """직군 네트워크 생성 (공통 키워드 기반)"""
    G = nx.Graph()
    
    # 노드 추가 (직군)
    for job_name, keywords in job_keywords.items():
        G.add_node(job_name, keywords=keywords, keyword_count=len(keywords))
    
    # 엣지 추가 (공통 키워드를 가진 직군들)
    jobs = list(job_keywords.keys())
    
    print(f"\n네트워크 엣지 생성 중...")
    edge_count = 0
    
    for i in range(len(jobs)):
        for j in range(i + 1, len(jobs)):
            job1 = jobs[i]
            job2 = jobs[j]
            
            # 공통 키워드 찾기
            shared_keywords = job_keywords[job1] & job_keywords[job2]
            
            # 최소 공통 키워드 개수 이상이면 엣지 추가
            if len(shared_keywords) >= min_shared_keywords:
                G.add_edge(job1, job2, 
                          weight=len(shared_keywords),
                          shared_keywords=list(shared_keywords))
                edge_count += 1
    
    print(f"  생성된 엣지 수: {edge_count}개")
    return G

def visualize_network(G: nx.Graph, output_file: str = 'job_network.png', 
                     figsize: tuple = (28, 20), node_size_scale: int = 500, min_shared_keywords: int = 5):
    """네트워크 시각화 (가독성 개선)"""
    # 한글 폰트 설정
    plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
    plt.rcParams['axes.unicode_minus'] = False
    
    # 최소 공통 키워드 수 이상인 엣지만 포함하는 서브그래프 생성 (가독성 향상)
    G_filtered = G.copy()
    edges_to_remove = [(u, v) for u, v, d in G.edges(data=True) if d.get('weight', 0) < min_shared_keywords]
    G_filtered.remove_edges_from(edges_to_remove)
    
    # 연결되지 않은 노드도 표시 (제거하지 않음)
    isolated_nodes = list(nx.isolates(G_filtered))
    if isolated_nodes:
        print(f"  연결되지 않은 노드: {len(isolated_nodes)}개 (표시됨)")
    
    print(f"  필터링 후: {G_filtered.number_of_nodes()}개 노드, {G_filtered.number_of_edges()}개 엣지")
    
    # 레이아웃 계산 (더 넓게 배치, 여러 알고리즘 시도)
    print("\n네트워크 레이아웃 계산 중...")
    # 노드 수에 따라 레이아웃 알고리즘 선택
    if G_filtered.number_of_nodes() > 20:
        # 많은 노드: force-directed layout with larger k
        pos = nx.spring_layout(G_filtered, k=8, iterations=300, seed=42)
    else:
        pos = nx.spring_layout(G_filtered, k=5, iterations=200, seed=42)
    
    # 노드 크기 (키워드 개수에 비례, 최소/최대 크기 제한)
    node_sizes = []
    keyword_counts = [G_filtered.nodes[node].get('keyword_count', 1) for node in G_filtered.nodes()]
    min_count, max_count = min(keyword_counts), max(keyword_counts)
    
    for node in G_filtered.nodes():
        count = G_filtered.nodes[node].get('keyword_count', 1)
        # 정규화하여 300~2000 사이로 조정
        if max_count > min_count:
            normalized = (count - min_count) / (max_count - min_count)
            size = 300 + normalized * 1700
        else:
            size = 1000
        node_sizes.append(size)
    
    # 엣지 두께 및 색상 (공통 키워드 개수에 비례)
    edge_widths = []
    edge_colors = []
    weights = [G_filtered.edges[edge].get('weight', 1) for edge in G_filtered.edges()]
    if weights:
        min_weight, max_weight = min(weights), max(weights)
    
    for edge in G_filtered.edges():
        weight = G_filtered.edges[edge].get('weight', 1)
        # 두께: 1.0 ~ 4.0 (더 두껍게)
        if max_weight > min_weight:
            normalized = (weight - min_weight) / (max_weight - min_weight)
            width = 1.0 + normalized * 3.0
        else:
            width = 2.0
        edge_widths.append(width)
        
        # 색상: 공통 키워드가 많을수록 진한 파란색 (투명도 조정)
        if max_weight > min_weight:
            alpha = 0.4 + (weight - min_weight) / (max_weight - min_weight) * 0.5
        else:
            alpha = 0.6
        # 파란색 계열 그라데이션
        edge_colors.append((0.2, 0.4, 0.8, min(alpha, 0.9)))
    
    # 그래프 그리기
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    
    # 엣지 그리기 (먼저 그려서 노드 뒤에 배치, 더 얇고 투명하게)
    nx.draw_networkx_edges(G_filtered, pos, width=edge_widths, 
                          edge_color=edge_colors, ax=ax, style='solid')
    
    # 노드 그리기 (키워드 개수에 따라 색상 그라데이션)
    node_colors = []
    for node in G_filtered.nodes():
        count = G_filtered.nodes[node].get('keyword_count', 1)
        if max_count > min_count:
            normalized = (count - min_count) / (max_count - min_count)
            # 파란색 계열 그라데이션
            node_colors.append((0.3, 0.5, 0.8 + normalized * 0.2))
        else:
            node_colors.append((0.3, 0.5, 0.9))
    
    nx.draw_networkx_nodes(G_filtered, pos, node_size=node_sizes, node_color=node_colors, 
                          alpha=0.9, edgecolors='black', linewidths=2, ax=ax)
    
    # 레이블 그리기 (노드 위에, 더 읽기 쉽게)
    labels = {node: node for node in G_filtered.nodes()}
    # 레이블 크기 조정 (노드 수에 따라, 더 크게)
    font_size = max(10, min(14, 300 / G_filtered.number_of_nodes()))
    nx.draw_networkx_labels(G_filtered, pos, labels, font_size=font_size, 
                           font_family='Malgun Gothic', font_weight='bold',
                           bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                                   edgecolor='darkblue', alpha=0.9, linewidth=1), ax=ax)
    
    # 제목
    plt.title(f'직군 네트워크 (노드: {G_filtered.number_of_nodes()}개, 엣지: {G_filtered.number_of_edges()}개, 최소 공통 키워드: {min_shared_keywords}개 이상)', 
             fontsize=20, pad=25, fontfamily='Malgun Gothic', fontweight='bold')
    
    # 범례 추가
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=(0.3, 0.5, 0.8), label='노드 크기: 키워드 개수에 비례'),
        Patch(facecolor=(0.2, 0.4, 0.8, 0.5), label='엣지 두께: 공통 키워드 개수에 비례')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=12, framealpha=0.9)
    
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ 네트워크 그래프가 '{output_file}'에 저장되었습니다.")
    plt.close()

def analyze_network(G: nx.Graph):
    """네트워크 분석 및 통계 출력"""
    print("\n" + "="*60)
    print("네트워크 분석 결과")
    print("="*60)
    print(f"노드 수 (직군 수): {G.number_of_nodes()}")
    print(f"엣지 수 (연결 수): {G.number_of_edges()}")
    
    if G.number_of_nodes() > 0:
        avg_degree = 2 * G.number_of_edges() / G.number_of_nodes()
        print(f"평균 연결 수: {avg_degree:.2f}")
    
    # 연결 요소 분석
    components = list(nx.connected_components(G))
    print(f"\n연결 요소 수: {len(components)}")
    if len(components) > 0:
        largest_component = max(components, key=len)
        print(f"가장 큰 연결 요소 크기: {len(largest_component)}개 직군")
    
    # 중심성 분석
    if G.number_of_nodes() > 0:
        degree_centrality = nx.degree_centrality(G)
        top_central = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        print("\n중심성 상위 10개 직군:")
        for job, centrality in top_central:
            keyword_count = G.nodes[job].get('keyword_count', 0)
            degree = G.degree(job)
            print(f"  {job}: 중심성 {centrality:.3f}, 연결 수 {degree}, 키워드 수 {keyword_count}")
    
    # 공통 키워드가 많은 엣지
    edges_with_weights = [(u, v, G.edges[u, v].get('weight', 0)) 
                          for u, v in G.edges()]
    top_edges = sorted(edges_with_weights, key=lambda x: x[2], reverse=True)[:10]
    print("\n공통 키워드가 많은 상위 10개 연결:")
    for u, v, weight in top_edges:
        shared = G.edges[u, v].get('shared_keywords', [])
        print(f"  {u} <-> {v}: {weight}개 공통 키워드")
        if len(shared) <= 10:
            print(f"    공통 키워드: {', '.join(shared[:10])}")
        else:
            print(f"    공통 키워드: {', '.join(shared[:10])} ... (총 {len(shared)}개)")

def main():
    """메인 함수"""
    print("="*60)
    print("직군 네트워크 분석")
    print("="*60)
    
    # 1. 각 직군별 키워드 로드
    print("\n직군별 키워드 사전 로드 중...")
    job_keywords = load_job_keywords('직무별_키워드_사전')
    
    print(f"\n총 {len(job_keywords)}개 직군의 키워드 로드 완료")
    
    # 2. 네트워크 생성
    print("\n네트워크 생성 중...")
    G = create_job_network(job_keywords, min_shared_keywords=1)
    
    # 3. 네트워크 시각화 (가독성 개선)
    print("\n네트워크 시각화 중...")
    # 최소 공통 키워드 70개 이상인 엣지만 표시하여 가독성 향상
    visualize_network(G, output_file='job_network.png', figsize=(32, 24), min_shared_keywords=70)
    
    # 4. 네트워크 분석
    analyze_network(G)
    
    # 5. 네트워크 데이터 저장
    try:
        # GraphML 형식으로 저장 (한글 지원)
        # GraphML은 set 타입을 지원하지 않으므로 변환 필요
        G_graphml = G.copy()
        for node in G_graphml.nodes():
            if 'keywords' in G_graphml.nodes[node]:
                keywords_set = G_graphml.nodes[node]['keywords']
                if isinstance(keywords_set, set):
                    G_graphml.nodes[node]['keywords'] = ', '.join(sorted(keywords_set))
                else:
                    G_graphml.nodes[node]['keywords'] = str(keywords_set)
        for u, v in G_graphml.edges():
            if 'shared_keywords' in G_graphml.edges[u, v]:
                shared = G_graphml.edges[u, v]['shared_keywords']
                if isinstance(shared, set):
                    G_graphml.edges[u, v]['shared_keywords'] = ', '.join(sorted(shared))
                elif isinstance(shared, list):
                    G_graphml.edges[u, v]['shared_keywords'] = ', '.join(shared)
                else:
                    G_graphml.edges[u, v]['shared_keywords'] = str(shared)
        
        nx.write_graphml(G_graphml, 'job_network.graphml')
        print("\n✓ 네트워크 데이터가 'job_network.graphml'에 저장되었습니다.")
    except Exception as e:
        print(f"\n⚠ GraphML 저장 중 오류 발생: {e}")
        try:
            # GML 형식으로 저장 시도
            G_copy = G.copy()
            for node in G_copy.nodes():
                if 'keywords' in G_copy.nodes[node]:
                    keywords_set = G_copy.nodes[node]['keywords']
                    if isinstance(keywords_set, set):
                        G_copy.nodes[node]['keywords'] = ', '.join(sorted(keywords_set))
                    else:
                        G_copy.nodes[node]['keywords'] = str(keywords_set)
            for u, v in G_copy.edges():
                if 'shared_keywords' in G_copy.edges[u, v]:
                    shared = G_copy.edges[u, v]['shared_keywords']
                    if isinstance(shared, set):
                        G_copy.edges[u, v]['shared_keywords'] = ', '.join(sorted(shared))
                    elif isinstance(shared, list):
                        G_copy.edges[u, v]['shared_keywords'] = ', '.join(shared)
                    else:
                        G_copy.edges[u, v]['shared_keywords'] = str(shared)
            nx.write_gml(G_copy, 'job_network.gml')
            print("✓ 네트워크 데이터가 'job_network.gml'에 저장되었습니다.")
        except Exception as e2:
            print(f"⚠ GML 저장도 실패: {e2}")
    
    # Pajek 형식으로 저장 (표준 Pajek 형식 준수)
    try:
        # Pajek 형식은 속성 저장에 제한이 있으므로, 기본 정보만 포함하는 그래프 생성
        G_pajek = nx.Graph()
        
        # 노드 ID 매핑 (문자열 -> 숫자)
        node_to_id = {node: idx + 1 for idx, node in enumerate(sorted(G.nodes()))}
        id_to_node = {idx + 1: node for idx, node in enumerate(sorted(G.nodes()))}
        
        # 노드 추가 (ID와 레이블만)
        for node in sorted(G.nodes()):
            node_id = node_to_id[node]
            G_pajek.add_node(node_id)
            # 노드 레이블은 write_pajek에서 자동 처리됨
        
        # 엣지 추가 (가중치 포함)
        for u, v in G.edges():
            u_id = node_to_id[u]
            v_id = node_to_id[v]
            weight = G.edges[u, v].get('weight', 1)
            G_pajek.add_edge(u_id, v_id, weight=weight)
        
        # Pajek 형식으로 저장 (.net 확장자, UTF-8 인코딩)
        # NetworkX의 write_pajek은 표준 Pajek 형식으로 저장하지만,
        # 노드 레이블을 유지하기 위해 수동으로 작성
        with open('job_network.net', 'w', encoding='utf-8') as f:
            # Vertices 섹션
            f.write(f"*Vertices {G_pajek.number_of_nodes()}\n")
            for node_id in sorted(G_pajek.nodes()):
                node_label = id_to_node[node_id]
                # Pajek 형식: id "label"
                # 따옴표 안의 따옴표는 이스케이프 필요
                label_escaped = node_label.replace('"', '\\"')
                f.write(f'{node_id} "{label_escaped}"\n')
            
            # Edges 섹션 (무방향 그래프이므로 *Edges 사용)
            f.write(f"*Edges\n")
            for u, v in sorted(G_pajek.edges()):
                weight = G_pajek.edges[u, v].get('weight', 1)
                f.write(f"{u} {v} {weight}\n")
        
        print("✓ 네트워크 데이터가 'job_network.net' (Pajek 형식)에 저장되었습니다.")
        print(f"  - 노드 수: {G_pajek.number_of_nodes()}개")
        print(f"  - 엣지 수: {G_pajek.number_of_edges()}개")
    except Exception as e:
        print(f"\n⚠ Pajek 저장 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    # Pajek 형식으로 저장 (가중치 100 이상인 엣지만 포함)
    try:
        # 가중치 100 이상인 엣지만 포함하는 그래프 생성
        G_pajek_100 = nx.Graph()
        
        # 노드 ID 매핑 (문자열 -> 숫자) - 원본 그래프의 모든 노드 포함
        node_to_id = {node: idx + 1 for idx, node in enumerate(sorted(G.nodes()))}
        id_to_node = {idx + 1: node for idx, node in enumerate(sorted(G.nodes()))}
        
        # 모든 노드 추가 (연결되지 않은 노드도 포함)
        for node in sorted(G.nodes()):
            node_id = node_to_id[node]
            G_pajek_100.add_node(node_id)
        
        # 가중치 100 이상인 엣지만 추가
        for u, v in G.edges():
            weight = G.edges[u, v].get('weight', 1)
            if weight >= 100:
                u_id = node_to_id[u]
                v_id = node_to_id[v]
                G_pajek_100.add_edge(u_id, v_id, weight=weight)
        
        # Pajek 형식으로 저장 (.net 확장자, UTF-8 인코딩)
        with open('job_network_100.net', 'w', encoding='utf-8') as f:
            # Vertices 섹션
            f.write(f"*Vertices {G_pajek_100.number_of_nodes()}\n")
            for node_id in sorted(G_pajek_100.nodes()):
                node_label = id_to_node[node_id]
                # Pajek 형식: id "label"
                # 따옴표 안의 따옴표는 이스케이프 필요
                label_escaped = node_label.replace('"', '\\"')
                f.write(f'{node_id} "{label_escaped}"\n')
            
            # Edges 섹션 (무방향 그래프이므로 *Edges 사용)
            f.write(f"*Edges\n")
            for u, v in sorted(G_pajek_100.edges()):
                weight = G_pajek_100.edges[u, v].get('weight', 1)
                f.write(f"{u} {v} {weight}\n")
        
        print("\n✓ 네트워크 데이터가 'job_network_100.net' (Pajek 형식, 가중치 100 이상)에 저장되었습니다.")
        print(f"  - 노드 수: {G_pajek_100.number_of_nodes()}개")
        print(f"  - 엣지 수: {G_pajek_100.number_of_edges()}개 (가중치 100 이상)")
        
        # 연결되지 않은 노드 확인
        isolated_nodes = list(nx.isolates(G_pajek_100))
        if isolated_nodes:
            print(f"  - 연결되지 않은 노드: {len(isolated_nodes)}개")
    except Exception as e:
        print(f"\n⚠ Pajek 100 저장 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    return G

if __name__ == "__main__":
    G = main()

