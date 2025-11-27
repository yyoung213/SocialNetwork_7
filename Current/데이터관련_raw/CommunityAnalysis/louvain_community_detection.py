"""
Louvain 알고리즘을 활용한 군집 분석 (데이터관련)
- 기본 군집 탐지
- Modularity 점수 계산
- Modularity 개선을 위한 필터링 전략 적용
"""

import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from networkx.algorithms import community
import os
import warnings
warnings.filterwarnings('ignore')


def read_skill_network(file_path: str):
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


def detect_communities_louvain(G):
    """
    Louvain 알고리즘을 사용하여 커뮤니티 탐지
    """
    print("\nLouvain 알고리즘 적용 중...")
    
    # NetworkX의 louvain_communities 사용
    communities_list = list(community.louvain_communities(G, weight='weight', seed=42))
    
    # partition 딕셔너리 생성 (node -> community_id)
    partition = {}
    for comm_id, comm_nodes in enumerate(communities_list):
        for node in comm_nodes:
            partition[node] = comm_id
    
    # 커뮤니티 ID별로 노드 그룹화
    communities = {}
    for comm_id, comm_nodes in enumerate(communities_list):
        communities[comm_id] = comm_nodes
    
    # Modularity 계산
    modularity = community.modularity(G, communities_list, weight='weight')
    
    print(f"  발견된 커뮤니티 수: {len(communities)}개")
    print(f"  Modularity: {modularity:.4f}")
    
    return partition, communities, modularity


def analyze_communities(G, partition, communities, node_id_to_label):
    """
    커뮤니티 분석 및 통계 생성
    """
    print("\n커뮤니티 분석 중...")
    
    # 각 커뮤니티의 통계
    community_stats = []
    
    for comm_id, nodes in communities.items():
        subgraph = G.subgraph(nodes)
        
        # 커뮤니티 내 주요 스킬 (degree 기준)
        degrees = dict(subgraph.degree())
        top_skills = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]
        top_skill_names = [node_id_to_label.get(node_id, f"Node {node_id}") 
                          for node_id, _ in top_skills]
        
        # 커뮤니티 내부 연결 밀도
        internal_edges = subgraph.number_of_edges()
        possible_edges = len(nodes) * (len(nodes) - 1) / 2
        density = internal_edges / possible_edges if possible_edges > 0 else 0
        
        # 커뮤니티 간 연결 수
        external_edges = 0
        for node in nodes:
            for neighbor in G.neighbors(node):
                if neighbor not in nodes:
                    external_edges += 1
        external_edges = external_edges // 2  # 무방향 그래프
        
        community_stats.append({
            'Community_ID': comm_id,
            'Size': len(nodes),
            'Internal_Edges': internal_edges,
            'External_Edges': external_edges,
            'Density': density,
            'Top_Skills': ', '.join(top_skill_names[:5])
        })
    
    df = pd.DataFrame(community_stats)
    df = df.sort_values('Size', ascending=False)
    
    return df


def filter_network_strategy1(G, node_id_to_label, percentile=95):
    """
    전략 1: 높은 degree 스킬 제거 (허브 노드 제거)
    정당성: 허브 노드는 모든 군집과 연결되어 있어 군집 구분을 어렵게 함
    """
    print(f"\n전략 1: 상위 {100-percentile}% 높은 degree 스킬 제거")
    
    degrees = dict(G.degree())
    degree_values = list(degrees.values())
    threshold = np.percentile(degree_values, percentile)
    
    # 제거할 노드 찾기
    nodes_to_remove = [node for node, deg in degrees.items() 
                       if deg >= threshold]
    
    print(f"  제거할 노드 수: {len(nodes_to_remove)}개 (threshold: {threshold:.0f})")
    print(f"  제거될 주요 스킬: {', '.join([node_id_to_label.get(n, f'Node {n}') for n in nodes_to_remove[:10]])}")
    
    # 노드 제거
    G_filtered = G.copy()
    G_filtered.remove_nodes_from(nodes_to_remove)
    
    print(f"  필터링 후 노드 수: {G_filtered.number_of_nodes()}개")
    print(f"  필터링 후 엣지 수: {G_filtered.number_of_edges()}개")
    
    return G_filtered, f"상위{100-percentile}%_허브제거"


def filter_network_strategy2(G, min_degree=2):
    """
    전략 2: 낮은 degree 스킬 제거 (고립 노드 제거)
    정당성: 고립 노드나 연결이 적은 노드는 군집 구조에 기여하지 않음
    """
    print(f"\n전략 2: Degree < {min_degree}인 스킬 제거")
    
    degrees = dict(G.degree())
    nodes_to_remove = [node for node, deg in degrees.items() if deg < min_degree]
    
    print(f"  제거할 노드 수: {len(nodes_to_remove)}개")
    
    # 노드 제거
    G_filtered = G.copy()
    G_filtered.remove_nodes_from(nodes_to_remove)
    
    print(f"  필터링 후 노드 수: {G_filtered.number_of_nodes()}개")
    print(f"  필터링 후 엣지 수: {G_filtered.number_of_edges()}개")
    
    return G_filtered, f"최소degree{min_degree}"


def filter_network_strategy3(G, weight_percentile=10):
    """
    전략 3: 가중치가 낮은 엣지 제거
    정당성: 약한 연결은 노이즈로 작용하여 군집 구조를 흐릴 수 있음
    """
    print(f"\n전략 3: 하위 {weight_percentile}% 낮은 가중치 엣지 제거")
    
    weights = [G[u][v].get('weight', 1.0) for u, v in G.edges()]
    threshold = np.percentile(weights, weight_percentile)
    
    # 제거할 엣지 찾기
    edges_to_remove = [(u, v) for u, v in G.edges() 
                       if G[u][v].get('weight', 1.0) <= threshold]
    
    print(f"  제거할 엣지 수: {len(edges_to_remove)}개 (threshold: {threshold:.2f})")
    
    # 엣지 제거
    G_filtered = G.copy()
    G_filtered.remove_edges_from(edges_to_remove)
    
    # 고립 노드 제거
    isolated = list(nx.isolates(G_filtered))
    G_filtered.remove_nodes_from(isolated)
    
    print(f"  필터링 후 노드 수: {G_filtered.number_of_nodes()}개")
    print(f"  필터링 후 엣지 수: {G_filtered.number_of_edges()}개")
    print(f"  제거된 고립 노드: {len(isolated)}개")
    
    return G_filtered, f"하위{weight_percentile}%_엣지제거"


def filter_network_strategy4(G, node_id_to_label, hub_percentile=95, min_degree=2):
    """
    전략 4: 허브 노드 제거 + 고립 노드 제거 (복합 전략)
    정당성: 허브와 고립 노드를 동시에 제거하여 군집 구조를 더 명확하게 함
    """
    print(f"\n전략 4: 허브 노드 제거 + 고립 노드 제거 (복합)")
    
    # 1단계: 허브 노드 제거
    degrees = dict(G.degree())
    degree_values = list(degrees.values())
    hub_threshold = np.percentile(degree_values, hub_percentile)
    hubs_to_remove = [node for node, deg in degrees.items() if deg >= hub_threshold]
    
    G_filtered = G.copy()
    G_filtered.remove_nodes_from(hubs_to_remove)
    
    # 2단계: 고립 노드 제거
    degrees_filtered = dict(G_filtered.degree())
    isolated_to_remove = [node for node, deg in degrees_filtered.items() if deg < min_degree]
    G_filtered.remove_nodes_from(isolated_to_remove)
    
    print(f"  제거된 허브 노드: {len(hubs_to_remove)}개")
    print(f"  제거된 고립 노드: {len(isolated_to_remove)}개")
    print(f"  필터링 후 노드 수: {G_filtered.number_of_nodes()}개")
    print(f"  필터링 후 엣지 수: {G_filtered.number_of_edges()}개")
    
    return G_filtered, f"허브제거+고립제거"


def save_community_results(partition, communities, modularity, community_stats, 
                          node_id_to_label, output_dir, strategy_name=""):
    """
    커뮤니티 분석 결과 저장
    """
    print(f"\n결과 저장 중...")
    
    # 커뮤니티 할당 정보 저장
    community_assignments = []
    for node_id, comm_id in partition.items():
        skill_name = node_id_to_label.get(node_id, f"Node {node_id}")
        community_assignments.append({
            'Node_ID': node_id,
            'Skill': skill_name,
            'Community_ID': comm_id
        })
    
    df_assignments = pd.DataFrame(community_assignments)
    df_assignments = df_assignments.sort_values('Community_ID')
    
    # 파일명에 전략명 추가
    suffix = f"_{strategy_name}" if strategy_name else ""
    
    # 커뮤니티 할당 저장
    csv_path = os.path.join(output_dir, f'community_assignments{suffix}.csv')
    df_assignments.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"✓ 커뮤니티 할당: {csv_path}")
    
    # 커뮤니티 통계 저장
    csv_path = os.path.join(output_dir, f'community_statistics{suffix}.csv')
    community_stats.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"✓ 커뮤니티 통계: {csv_path}")
    
    # 상세 리포트 생성
    report_path = os.path.join(output_dir, f'community_analysis_report{suffix}.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("Louvain 알고리즘 기반 군집 분석 리포트 (데이터관련)\n")
        if strategy_name:
            f.write(f"전략: {strategy_name}\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"Modularity 점수: {modularity:.4f}\n")
        f.write(f"커뮤니티 수: {len(communities)}개\n\n")
        
        f.write("-"*60 + "\n")
        f.write("커뮤니티별 상세 정보\n")
        f.write("-"*60 + "\n\n")
        
        for _, row in community_stats.iterrows():
            comm_id = int(row['Community_ID'])
            f.write(f"커뮤니티 {comm_id}:\n")
            f.write(f"  크기: {int(row['Size'])}개 스킬\n")
            f.write(f"  내부 연결: {int(row['Internal_Edges'])}개\n")
            f.write(f"  외부 연결: {int(row['External_Edges'])}개\n")
            f.write(f"  밀도: {row['Density']:.4f}\n")
            f.write(f"  주요 스킬: {row['Top_Skills']}\n\n")
    
    print(f"✓ 분석 리포트: {report_path}")


def compare_strategies(results):
    """
    여러 전략의 결과 비교
    """
    print("\n" + "="*60)
    print("전략별 Modularity 비교")
    print("="*60)
    
    comparison = []
    for strategy_name, modularity, num_communities, num_nodes in results:
        comparison.append({
            'Strategy': strategy_name,
            'Modularity': modularity,
            'Num_Communities': num_communities,
            'Num_Nodes': num_nodes
        })
    
    df_comparison = pd.DataFrame(comparison)
    df_comparison = df_comparison.sort_values('Modularity', ascending=False)
    
    print("\n전략별 결과:")
    for _, row in df_comparison.iterrows():
        print(f"  {row['Strategy']:30s} | Modularity: {row['Modularity']:.4f} | "
              f"커뮤니티: {row['Num_Communities']:3d}개 | 노드: {row['Num_Nodes']:4d}개")
    
    return df_comparison


def main():
    """메인 함수"""
    print("="*60)
    print("Louvain 알고리즘 기반 군집 분석 (데이터관련)")
    print("="*60)
    
    # 현재 스크립트 위치 기준으로 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    # 입력 파일 경로
    input_file = os.path.join(parent_dir, 'skill_skill_network.net')
    
    # 출력 디렉토리
    output_dir = script_dir
    
    if not os.path.exists(input_file):
        print(f"오류: '{input_file}' 파일을 찾을 수 없습니다.")
        return
    
    # 네트워크 로딩
    G, node_id_to_label = read_skill_network(input_file)
    
    # 결과 저장용 리스트
    results = []
    
    # 1. 기본 네트워크 분석
    print("\n" + "="*60)
    print("1. 기본 네트워크 분석")
    print("="*60)
    
    partition, communities, modularity = detect_communities_louvain(G)
    community_stats = analyze_communities(G, partition, communities, node_id_to_label)
    save_community_results(partition, communities, modularity, community_stats, 
                          node_id_to_label, output_dir, "기본")
    
    results.append(("기본", modularity, len(communities), G.number_of_nodes()))
    
    # Modularity가 낮으면 (0.3 미만) 필터링 전략 적용
    if modularity < 0.3:
        print(f"\n⚠ Modularity가 낮습니다 ({modularity:.4f} < 0.3). 필터링 전략을 적용합니다.")
        
        # 전략 1: 허브 노드 제거
        print("\n" + "="*60)
        print("2. 전략 1: 허브 노드 제거")
        print("="*60)
        G_filtered1, strategy_name1 = filter_network_strategy1(G, node_id_to_label, percentile=95)
        if G_filtered1.number_of_nodes() > 10:  # 최소 노드 수 확인
            partition1, communities1, modularity1 = detect_communities_louvain(G_filtered1)
            community_stats1 = analyze_communities(G_filtered1, partition1, communities1, node_id_to_label)
            save_community_results(partition1, communities1, modularity1, community_stats1, 
                                  node_id_to_label, output_dir, strategy_name1)
            results.append((strategy_name1, modularity1, len(communities1), G_filtered1.number_of_nodes()))
        
        # 전략 2: 고립 노드 제거
        print("\n" + "="*60)
        print("3. 전략 2: 고립 노드 제거")
        print("="*60)
        G_filtered2, strategy_name2 = filter_network_strategy2(G, min_degree=2)
        if G_filtered2.number_of_nodes() > 10:
            partition2, communities2, modularity2 = detect_communities_louvain(G_filtered2)
            community_stats2 = analyze_communities(G_filtered2, partition2, communities2, node_id_to_label)
            save_community_results(partition2, communities2, modularity2, community_stats2, 
                                  node_id_to_label, output_dir, strategy_name2)
            results.append((strategy_name2, modularity2, len(communities2), G_filtered2.number_of_nodes()))
        
        # 전략 3: 낮은 가중치 엣지 제거
        print("\n" + "="*60)
        print("4. 전략 3: 낮은 가중치 엣지 제거")
        print("="*60)
        G_filtered3, strategy_name3 = filter_network_strategy3(G, weight_percentile=10)
        if G_filtered3.number_of_nodes() > 10:
            partition3, communities3, modularity3 = detect_communities_louvain(G_filtered3)
            community_stats3 = analyze_communities(G_filtered3, partition3, communities3, node_id_to_label)
            save_community_results(partition3, communities3, modularity3, community_stats3, 
                                  node_id_to_label, output_dir, strategy_name3)
            results.append((strategy_name3, modularity3, len(communities3), G_filtered3.number_of_nodes()))
        
        # 전략 4: 복합 전략
        print("\n" + "="*60)
        print("5. 전략 4: 허브 제거 + 고립 제거 (복합)")
        print("="*60)
        G_filtered4, strategy_name4 = filter_network_strategy4(G, node_id_to_label, hub_percentile=95, min_degree=2)
        if G_filtered4.number_of_nodes() > 10:
            partition4, communities4, modularity4 = detect_communities_louvain(G_filtered4)
            community_stats4 = analyze_communities(G_filtered4, partition4, communities4, node_id_to_label)
            save_community_results(partition4, communities4, modularity4, community_stats4, 
                                  node_id_to_label, output_dir, strategy_name4)
            results.append((strategy_name4, modularity4, len(communities4), G_filtered4.number_of_nodes()))
        
        # 추가 개선 전략: 더 많은 허브 노드 제거
        if modularity1 < 0.25:  # 여전히 낮으면 추가 전략 시도
            print("\n" + "="*60)
            print("6. 추가 전략: 상위 10% 허브 노드 제거")
            print("="*60)
            G_filtered5, strategy_name5 = filter_network_strategy1(G, node_id_to_label, percentile=90)
            if G_filtered5.number_of_nodes() > 10:
                partition5, communities5, modularity5 = detect_communities_louvain(G_filtered5)
                community_stats5 = analyze_communities(G_filtered5, partition5, communities5, node_id_to_label)
                save_community_results(partition5, communities5, modularity5, community_stats5, 
                                      node_id_to_label, output_dir, strategy_name5)
                results.append((strategy_name5, modularity5, len(communities5), G_filtered5.number_of_nodes()))
            
            print("\n" + "="*60)
            print("7. 추가 전략: 상위 15% 허브 노드 제거")
            print("="*60)
            G_filtered6, strategy_name6 = filter_network_strategy1(G, node_id_to_label, percentile=85)
            if G_filtered6.number_of_nodes() > 10:
                partition6, communities6, modularity6 = detect_communities_louvain(G_filtered6)
                community_stats6 = analyze_communities(G_filtered6, partition6, communities6, node_id_to_label)
                save_community_results(partition6, communities6, modularity6, community_stats6, 
                                      node_id_to_label, output_dir, strategy_name6)
                results.append((strategy_name6, modularity6, len(communities6), G_filtered6.number_of_nodes()))
        
        # 전략 비교
        df_comparison = compare_strategies(results)
        comparison_path = os.path.join(output_dir, 'strategy_comparison.csv')
        df_comparison.to_csv(comparison_path, index=False, encoding='utf-8-sig')
        print(f"\n✓ 전략 비교 결과: {comparison_path}")
        
        # 최적 전략 선택
        best_strategy = df_comparison.iloc[0]
        print(f"\n🏆 최적 전략: {best_strategy['Strategy']}")
        print(f"   Modularity: {best_strategy['Modularity']:.4f}")
        print(f"   커뮤니티 수: {best_strategy['Num_Communities']}개")
    else:
        print(f"\n✓ Modularity가 충분히 높습니다 ({modularity:.4f} >= 0.3). 추가 필터링이 필요하지 않습니다.")
    
    print("\n" + "="*60)
    print("분석 완료!")
    print("="*60)


if __name__ == "__main__":
    main()

