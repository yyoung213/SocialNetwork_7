"""
Skills-Skills 네트워크 구축 스크립트
bipartite_skill_wide.csv에서 같은 구인공고에 함께 언급된 스킬들 간의 네트워크를 생성합니다.
"""

import pandas as pd
import ast
import networkx as nx
from collections import Counter
from itertools import combinations
import json
import os
from typing import Dict, List, Tuple, Set


def load_bipartite_data(csv_file: str = 'bipartite_skill_wide.csv') -> pd.DataFrame:
    """
    bipartite_skill_wide.csv 파일을 로드하고 Skills_List를 파싱합니다.
    
    Args:
        csv_file (str): CSV 파일 경로
        
    Returns:
        pd.DataFrame: 파싱된 데이터프레임 (Skills_List가 실제 리스트로 변환됨)
    """
    print(f"데이터 파일 로딩 중: {csv_file}")
    
    # CSV 파일 읽기
    df = pd.read_csv(csv_file)
    print(f"  로드된 행 수: {len(df)}개")
    
    # Skills_List 파싱
    parsed_skills = []
    parse_errors = 0
    
    for idx, row in df.iterrows():
        skills_list_str = row['Skills_List']
        
        try:
            # 문자열을 리스트로 변환
            skills_list = ast.literal_eval(skills_list_str)
            
            # 스킬명 정규화 (공백 제거, 중복 제거)
            normalized_skills = [skill.strip() for skill in skills_list if skill.strip()]
            normalized_skills = list(set(normalized_skills))  # 중복 제거
            
            parsed_skills.append(normalized_skills)
            
        except (ValueError, SyntaxError) as e:
            print(f"  ⚠ Row {idx} 파싱 오류: {skills_list_str[:50]}...")
            parse_errors += 1
            parsed_skills.append([])
    
    # 파싱된 스킬 리스트를 새로운 컬럼으로 추가
    df['Parsed_Skills'] = parsed_skills
    
    if parse_errors > 0:
        print(f"  ⚠ 파싱 오류: {parse_errors}개")
    
    print(f"  ✓ 데이터 로딩 완료")
    return df


def extract_skill_pairs_from_job(skills_list: List[str]) -> List[Tuple[str, str]]:
    """
    하나의 구인공고에서 모든 스킬 쌍을 추출합니다.
    
    Args:
        skills_list (List[str]): 스킬 리스트
        
    Returns:
        List[Tuple[str, str]]: 정렬된 스킬 쌍 리스트 (skill1 < skill2)
    """
    if len(skills_list) < 2:
        return []
    
    # 모든 2개 조합 생성
    pairs = list(combinations(sorted(skills_list), 2))
    return pairs


def build_cooccurrence_matrix(df: pd.DataFrame) -> Dict[Tuple[str, str], int]:
    """
    모든 구인공고를 순회하며 스킬 쌍의 co-occurrence를 계산합니다.
    
    Args:
        df (pd.DataFrame): 파싱된 데이터프레임
        
    Returns:
        Dict[Tuple[str, str], int]: {(skill1, skill2): count} 형태의 딕셔너리
    """
    print("\nCo-occurrence 계산 중...")
    
    cooccurrence_counter = Counter()
    total_jobs = len(df)
    jobs_with_pairs = 0
    
    for idx, row in df.iterrows():
        skills_list = row['Parsed_Skills']
        
        if len(skills_list) < 2:
            continue
        
        # 스킬 쌍 추출
        pairs = extract_skill_pairs_from_job(skills_list)
        
        if pairs:
            jobs_with_pairs += 1
            # Counter에 추가
            for pair in pairs:
                cooccurrence_counter[pair] += 1
        
        # 진행 상황 출력 (100개마다)
        if (idx + 1) % 100 == 0:
            print(f"  진행: {idx + 1}/{total_jobs} ({100*(idx+1)/total_jobs:.1f}%)")
    
    print(f"  ✓ 처리 완료: {total_jobs}개 구인공고 중 {jobs_with_pairs}개에서 스킬 쌍 발견")
    print(f"  ✓ 고유 스킬 쌍 수: {len(cooccurrence_counter)}개")
    
    return dict(cooccurrence_counter)


def create_skill_network(cooccurrence_dict: Dict[Tuple[str, str], int], 
                        min_weight: int = 1) -> nx.Graph:
    """
    NetworkX 그래프를 생성합니다.
    
    Args:
        cooccurrence_dict (Dict[Tuple[str, str], int]): 스킬 쌍과 가중치 딕셔너리
        min_weight (int): 최소 가중치 임계값 (이 값 이상인 엣지만 포함)
        
    Returns:
        nx.Graph: NetworkX 그래프 객체
    """
    print(f"\n네트워크 그래프 생성 중 (min_weight >= {min_weight})...")
    
    G = nx.Graph()
    
    # 모든 고유 스킬을 노드로 추가
    all_skills = set()
    for (skill1, skill2) in cooccurrence_dict.keys():
        all_skills.add(skill1)
        all_skills.add(skill2)
    
    for skill in all_skills:
        G.add_node(skill)
    
    print(f"  노드 수: {len(G.nodes())}개")
    
    # 엣지 추가 (가중치 포함)
    edge_count = 0
    filtered_edge_count = 0
    
    for (skill1, skill2), weight in cooccurrence_dict.items():
        edge_count += 1
        
        if weight >= min_weight:
            G.add_edge(skill1, skill2, weight=weight)
            filtered_edge_count += 1
    
    print(f"  전체 엣지 수: {edge_count}개")
    print(f"  필터링 후 엣지 수: {filtered_edge_count}개 (min_weight >= {min_weight})")
    
    return G


def calculate_network_statistics(G: nx.Graph) -> Dict:
    """
    네트워크 통계를 계산합니다.
    
    Args:
        G (nx.Graph): NetworkX 그래프 객체
        
    Returns:
        Dict: 네트워크 통계 정보
    """
    print("\n네트워크 통계 계산 중...")
    
    stats = {}
    
    # 기본 통계
    stats['num_nodes'] = G.number_of_nodes()
    stats['num_edges'] = G.number_of_edges()
    
    # Degree 통계
    degrees = dict(G.degree())
    degree_values = list(degrees.values())
    
    stats['avg_degree'] = sum(degree_values) / len(degree_values) if degree_values else 0
    stats['max_degree'] = max(degree_values) if degree_values else 0
    stats['min_degree'] = min(degree_values) if degree_values else 0
    
    # 연결성
    connected_components = list(nx.connected_components(G))
    stats['num_components'] = len(connected_components)
    stats['largest_component_size'] = len(max(connected_components, key=len)) if connected_components else 0
    
    # 밀도
    stats['density'] = nx.density(G)
    
    # 클러스터링 계수
    stats['avg_clustering'] = nx.average_clustering(G)
    
    # 가중치 통계 (엣지가 있는 경우)
    if G.number_of_edges() > 0:
        weights = [d['weight'] for u, v, d in G.edges(data=True)]
        stats['avg_edge_weight'] = sum(weights) / len(weights)
        stats['max_edge_weight'] = max(weights)
        stats['min_edge_weight'] = min(weights)
    else:
        stats['avg_edge_weight'] = 0
        stats['max_edge_weight'] = 0
        stats['min_edge_weight'] = 0
    
    # 고립된 노드 수
    isolated_nodes = list(nx.isolates(G))
    stats['num_isolated_nodes'] = len(isolated_nodes)
    
    # 상위 degree 노드 (상위 10개)
    sorted_degrees = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
    stats['top_10_degree_nodes'] = sorted_degrees[:10]
    
    print(f"  ✓ 통계 계산 완료")
    
    return stats


def save_network(G: nx.Graph, output_prefix: str = 'skill_network'):
    """
    네트워크를 여러 형식으로 저장합니다.
    
    Args:
        G (nx.Graph): NetworkX 그래프 객체
        output_prefix (str): 출력 파일명 접두사
    """
    print(f"\n네트워크 파일 저장 중...")
    
    # GraphML 형식
    graphml_file = f"{output_prefix}.graphml"
    nx.write_graphml(G, graphml_file)
    print(f"  ✓ GraphML: {graphml_file}")
    
    # Edge List CSV 형식
    edges_data = []
    for u, v, d in G.edges(data=True):
        weight = d.get('weight', 1)
        edges_data.append({'Skill1': u, 'Skill2': v, 'Weight': weight})
    
    edges_df = pd.DataFrame(edges_data)
    edges_csv_file = f"{output_prefix}_edges.csv"
    edges_df.to_csv(edges_csv_file, index=False, encoding='utf-8-sig')
    print(f"  ✓ Edge List CSV: {edges_csv_file}")
    
    # GEXF 형식 (Gephi 호환)
    try:
        gexf_file = f"{output_prefix}.gexf"
        nx.write_gexf(G, gexf_file)
        print(f"  ✓ GEXF: {gexf_file}")
    except Exception as e:
        print(f"  ⚠ GEXF 저장 실패: {e}")
    
    # Node List CSV (노드별 degree 정보)
    nodes_data = []
    degrees = dict(G.degree())
    for node in G.nodes():
        nodes_data.append({
            'Skill': node,
            'Degree': degrees[node]
        })
    
    nodes_df = pd.DataFrame(nodes_data)
    nodes_df = nodes_df.sort_values('Degree', ascending=False)
    nodes_csv_file = f"{output_prefix}_nodes.csv"
    nodes_df.to_csv(nodes_csv_file, index=False, encoding='utf-8-sig')
    print(f"  ✓ Node List CSV: {nodes_csv_file}")
    
    # Pajek .net 형식 (UTF-8 인코딩)
    try:
        pajek_file = f"{output_prefix}.net"
        with open(pajek_file, 'w', encoding='utf-8') as f:
            # 노드 ID 매핑 (문자열 -> 숫자, 1부터 시작)
            sorted_nodes = sorted(G.nodes())
            node_to_id = {node: idx + 1 for idx, node in enumerate(sorted_nodes)}
            
            # Vertices 섹션
            f.write(f"*Vertices {G.number_of_nodes()}\n")
            for node in sorted_nodes:
                node_id = node_to_id[node]
                # Pajek 형식: id "label" (따옴표 안의 따옴표는 이스케이프)
                label_escaped = node.replace('"', '\\"')
                f.write(f'{node_id} "{label_escaped}"\n')
            
            # Edges 섹션 (무방향 그래프이므로 *Edges 사용)
            f.write(f"*Edges\n")
            for u, v in sorted(G.edges()):
                u_id = node_to_id[u]
                v_id = node_to_id[v]
                weight = G.edges[u, v].get('weight', 1)
                f.write(f"{u_id} {v_id} {weight}\n")
        
        print(f"  ✓ Pajek .net: {pajek_file}")
    except Exception as e:
        print(f"  ⚠ Pajek .net 저장 실패: {e}")


def save_statistics(stats: Dict, output_file: str = 'skill_network_stats.txt'):
    """
    네트워크 통계를 텍스트 파일로 저장합니다.
    
    Args:
        stats (Dict): 네트워크 통계 정보
        output_file (str): 출력 파일명
    """
    print(f"\n통계 정보 저장 중: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("Skills-Skills 네트워크 통계\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("기본 통계\n")
        f.write("-" * 60 + "\n")
        f.write(f"노드 수: {stats['num_nodes']:,}개\n")
        f.write(f"엣지 수: {stats['num_edges']:,}개\n")
        f.write(f"밀도: {stats['density']:.6f}\n\n")
        
        f.write("Degree 통계\n")
        f.write("-" * 60 + "\n")
        f.write(f"평균 Degree: {stats['avg_degree']:.2f}\n")
        f.write(f"최대 Degree: {stats['max_degree']}\n")
        f.write(f"최소 Degree: {stats['min_degree']}\n\n")
        
        f.write("연결성\n")
        f.write("-" * 60 + "\n")
        f.write(f"연결 성분 수: {stats['num_components']}개\n")
        f.write(f"최대 연결 성분 크기: {stats['largest_component_size']}개 노드\n")
        f.write(f"고립된 노드 수: {stats['num_isolated_nodes']}개\n\n")
        
        f.write("클러스터링\n")
        f.write("-" * 60 + "\n")
        f.write(f"평균 클러스터링 계수: {stats['avg_clustering']:.4f}\n\n")
        
        if stats['num_edges'] > 0:
            f.write("엣지 가중치 통계\n")
            f.write("-" * 60 + "\n")
            f.write(f"평균 가중치: {stats['avg_edge_weight']:.2f}\n")
            f.write(f"최대 가중치: {stats['max_edge_weight']}\n")
            f.write(f"최소 가중치: {stats['min_edge_weight']}\n\n")
        
        f.write("상위 10개 Degree 노드\n")
        f.write("-" * 60 + "\n")
        for i, (node, degree) in enumerate(stats['top_10_degree_nodes'], 1):
            f.write(f"{i:2d}. {node:30s} (Degree: {degree})\n")
    
    # JSON 형식으로도 저장
    json_file = output_file.replace('.txt', '.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        # JSON serialization을 위해 튜플을 리스트로 변환
        json_stats = stats.copy()
        json_stats['top_10_degree_nodes'] = [[node, degree] for node, degree in stats['top_10_degree_nodes']]
        json.dump(json_stats, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ 텍스트 파일: {output_file}")
    print(f"  ✓ JSON 파일: {json_file}")


def main(csv_file: str = 'bipartite_skill_wide.csv', min_weight: int = 1):
    """
    메인 실행 함수
    
    Args:
        csv_file (str): 입력 CSV 파일 경로
        min_weight (int): 최소 엣지 가중치 임계값
    """
    print("=" * 60)
    print("Skills-Skills 네트워크 구축")
    print("=" * 60)
    
    # 1. 데이터 로딩 및 파싱
    df = load_bipartite_data(csv_file)
    
    # 2. Co-occurrence 계산
    cooccurrence_dict = build_cooccurrence_matrix(df)
    
    # 3. 네트워크 그래프 생성
    G = create_skill_network(cooccurrence_dict, min_weight=min_weight)
    
    # 4. 네트워크 통계 계산
    stats = calculate_network_statistics(G)
    
    # 5. 결과 저장
    save_network(G, output_prefix='skill_network')
    save_statistics(stats, output_file='skill_network_stats.txt')
    
    # 6. 결과 요약 출력
    print("\n" + "=" * 60)
    print("네트워크 구축 완료!")
    print("=" * 60)
    print(f"노드 수: {stats['num_nodes']:,}개")
    print(f"엣지 수: {stats['num_edges']:,}개")
    print(f"평균 Degree: {stats['avg_degree']:.2f}")
    print(f"밀도: {stats['density']:.6f}")
    print(f"연결 성분 수: {stats['num_components']}개")
    print(f"평균 클러스터링 계수: {stats['avg_clustering']:.4f}")
    
    return G, stats


if __name__ == "__main__":
    # 기본 실행 (min_weight >= 1, 모든 엣지 포함)
    G, stats = main(min_weight=1)
    
    # 추가로 min_weight >= 2인 네트워크도 생성 (선택사항)
    print("\n" + "=" * 60)
    print("추가 네트워크 생성: min_weight >= 2")
    print("=" * 60)
    G_filtered, stats_filtered = main(min_weight=2)
    
    # 필터링된 네트워크 저장
    save_network(G_filtered, output_prefix='skill_network_filtered')
    save_statistics(stats_filtered, output_file='skill_network_filtered_stats.txt')

