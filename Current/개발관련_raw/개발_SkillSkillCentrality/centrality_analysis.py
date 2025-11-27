"""
스킬-스킬 네트워크 중심성 분석 (개발관련)
- Degree / Weighted Degree
- Betweenness Centrality
- Eigenvector Centrality / PageRank
- Top 10 핵심 스킬 추출 및 비교
"""

import networkx as nx
import pandas as pd
import numpy as np
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


def calculate_degree_centrality(G):
    """
    Degree Centrality 계산
    """
    print("\nDegree Centrality 계산 중...")
    degree_centrality = nx.degree_centrality(G)
    return degree_centrality


def calculate_weighted_degree(G):
    """
    Weighted Degree (Strength) 계산
    각 노드의 연결된 엣지 가중치의 합
    """
    print("Weighted Degree 계산 중...")
    weighted_degree = {}
    for node in G.nodes():
        strength = sum([G[node][neighbor].get('weight', 1.0) 
                        for neighbor in G.neighbors(node)])
        weighted_degree[node] = strength
    return weighted_degree


def calculate_betweenness_centrality(G):
    """
    Betweenness Centrality 계산
    """
    print("Betweenness Centrality 계산 중... (시간이 걸릴 수 있습니다)")
    betweenness = nx.betweenness_centrality(G, weight='weight')
    return betweenness


def calculate_eigenvector_centrality(G):
    """
    Eigenvector Centrality 계산
    """
    print("Eigenvector Centrality 계산 중...")
    try:
        eigenvector = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
    except:
        # 수렴 실패 시 기본값 사용
        print("  ⚠ Eigenvector Centrality 수렴 실패, 기본값 사용")
        eigenvector = {node: 0.0 for node in G.nodes()}
    return eigenvector


def calculate_pagerank(G):
    """
    PageRank 계산
    """
    print("PageRank 계산 중...")
    pagerank = nx.pagerank(G, weight='weight')
    return pagerank


def calculate_all_centralities(G):
    """
    모든 중심성 지표 계산
    """
    print("\n" + "="*60)
    print("중심성 지표 계산 시작")
    print("="*60)
    
    # 각 중심성 지표 계산
    degree_cent = calculate_degree_centrality(G)
    weighted_deg = calculate_weighted_degree(G)
    betweenness = calculate_betweenness_centrality(G)
    eigenvector = calculate_eigenvector_centrality(G)
    pagerank = calculate_pagerank(G)
    
    # 기본 degree도 계산
    degrees = dict(G.degree())
    
    return {
        'degree': degrees,
        'degree_centrality': degree_cent,
        'weighted_degree': weighted_deg,
        'betweenness': betweenness,
        'eigenvector': eigenvector,
        'pagerank': pagerank
    }


def create_centrality_dataframe(G, centralities, node_id_to_label):
    """
    모든 중심성 지표를 DataFrame으로 정리
    """
    print("\n중심성 데이터프레임 생성 중...")
    
    data = []
    for node_id in G.nodes():
        label = node_id_to_label.get(node_id, f"Node {node_id}")
        data.append({
            'Node_ID': node_id,
            'Skill': label,
            'Degree': centralities['degree'].get(node_id, 0),
            'Degree_Centrality': centralities['degree_centrality'].get(node_id, 0),
            'Weighted_Degree': centralities['weighted_degree'].get(node_id, 0),
            'Betweenness_Centrality': centralities['betweenness'].get(node_id, 0),
            'Eigenvector_Centrality': centralities['eigenvector'].get(node_id, 0),
            'PageRank': centralities['pagerank'].get(node_id, 0)
        })
    
    df = pd.DataFrame(data)
    df = df.sort_values('Degree', ascending=False)
    
    return df


def get_top_skills(df, metric: str, n: int = 10):
    """
    특정 지표 기준 Top N 스킬 추출
    """
    top_df = df.nlargest(n, metric)[['Skill', metric]]
    return top_df


def compare_top_skills(df):
    """
    각 지표별 Top 10 비교
    """
    print("\n" + "="*60)
    print("Top 10 핵심 스킬 비교")
    print("="*60)
    
    # 각 지표별 Top 10
    top_degree = get_top_skills(df, 'Degree', 10)
    top_weighted = get_top_skills(df, 'Weighted_Degree', 10)
    top_betweenness = get_top_skills(df, 'Betweenness_Centrality', 10)
    top_eigenvector = get_top_skills(df, 'Eigenvector_Centrality', 10)
    top_pagerank = get_top_skills(df, 'PageRank', 10)
    
    return {
        'degree': top_degree,
        'weighted_degree': top_weighted,
        'betweenness': top_betweenness,
        'eigenvector': top_eigenvector,
        'pagerank': top_pagerank
    }


def save_results(df, top_skills, output_dir: str):
    """
    결과를 파일로 저장
    """
    print("\n" + "="*60)
    print("결과 저장 중...")
    print("="*60)
    
    # 전체 중심성 데이터 저장
    csv_path = os.path.join(output_dir, 'all_centrality_metrics.csv')
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"✓ 전체 중심성 지표: {csv_path}")
    
    # 각 지표별 Top 10 저장
    for metric_name, top_df in top_skills.items():
        csv_path = os.path.join(output_dir, f'top10_{metric_name}.csv')
        top_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"✓ Top 10 ({metric_name}): {csv_path}")
    
    # 종합 리포트 생성
    report_path = os.path.join(output_dir, 'centrality_analysis_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("개발관련 스킬-스킬 네트워크 중심성 분석 리포트\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"전체 스킬 수: {len(df)}개\n")
        f.write(f"네트워크 엣지 수: {df['Degree'].sum() // 2}개\n\n")
        
        f.write("-"*60 + "\n")
        f.write("1. Degree 기준 Top 10 핵심 스킬\n")
        f.write("-"*60 + "\n")
        for idx, row in top_skills['degree'].iterrows():
            f.write(f"{idx+1:2d}. {row['Skill']:30s} (Degree: {row['Degree']:.0f})\n")
        
        f.write("\n" + "-"*60 + "\n")
        f.write("2. Weighted Degree 기준 Top 10 핵심 스킬\n")
        f.write("-"*60 + "\n")
        for idx, row in top_skills['weighted_degree'].iterrows():
            f.write(f"{idx+1:2d}. {row['Skill']:30s} (Weighted Degree: {row['Weighted_Degree']:.2f})\n")
        
        f.write("\n" + "-"*60 + "\n")
        f.write("3. Betweenness Centrality 기준 Top 10 브릿지 스킬\n")
        f.write("-"*60 + "\n")
        for idx, row in top_skills['betweenness'].iterrows():
            f.write(f"{idx+1:2d}. {row['Skill']:30s} (Betweenness: {row['Betweenness_Centrality']:.6f})\n")
        
        f.write("\n" + "-"*60 + "\n")
        f.write("4. Eigenvector Centrality 기준 Top 10 핵심 스킬\n")
        f.write("-"*60 + "\n")
        for idx, row in top_skills['eigenvector'].iterrows():
            f.write(f"{idx+1:2d}. {row['Skill']:30s} (Eigenvector: {row['Eigenvector_Centrality']:.6f})\n")
        
        f.write("\n" + "-"*60 + "\n")
        f.write("5. PageRank 기준 Top 10 핵심 스킬\n")
        f.write("-"*60 + "\n")
        for idx, row in top_skills['pagerank'].iterrows():
            f.write(f"{idx+1:2d}. {row['Skill']:30s} (PageRank: {row['PageRank']:.6f})\n")
    
    print(f"✓ 종합 리포트: {report_path}")


def generate_conclusions(df, top_skills):
    """
    분석 결과를 바탕으로 결론 도출
    """
    print("\n" + "="*60)
    print("결론 도출")
    print("="*60)
    
    # 공통으로 나타나는 스킬 찾기
    degree_top10 = set(top_skills['degree']['Skill'].values)
    eigenvector_top10 = set(top_skills['eigenvector']['Skill'].values)
    pagerank_top10 = set(top_skills['pagerank']['Skill'].values)
    betweenness_top10 = set(top_skills['betweenness']['Skill'].values)
    
    # 모든 지표에서 공통으로 나타나는 스킬
    common_all = degree_top10 & eigenvector_top10 & pagerank_top10 & betweenness_top10
    
    # Degree와 Eigenvector/PageRank에서 공통
    common_degree_eigen = degree_top10 & eigenvector_top10
    common_degree_pagerank = degree_top10 & pagerank_top10
    
    # 브릿지 스킬 (Betweenness 높지만 다른 지표는 낮은 경우)
    bridge_skills = betweenness_top10 - degree_top10
    
    conclusions = []
    
    conclusions.append("\n【핵심 발견사항】\n")
    conclusions.append(f"1. 모든 지표에서 공통으로 나타나는 슈퍼 허브 스킬: {len(common_all)}개")
    if common_all:
        conclusions.append(f"   → {', '.join(sorted(common_all))}")
    
    conclusions.append(f"\n2. Degree와 Eigenvector/PageRank에서 공통으로 나타나는 스킬: {len(common_degree_eigen)}개")
    if common_degree_eigen:
        conclusions.append(f"   → {', '.join(sorted(common_degree_eigen))}")
    
    conclusions.append(f"\n3. 브릿지 역할을 하는 스킬 (Betweenness 높지만 Degree 낮음): {len(bridge_skills)}개")
    if bridge_skills:
        conclusions.append(f"   → {', '.join(sorted(bridge_skills))}")
    
    # 통계 요약
    conclusions.append("\n【통계 요약】\n")
    conclusions.append(f"- 평균 Degree: {df['Degree'].mean():.2f}")
    conclusions.append(f"- 최대 Degree: {df['Degree'].max():.0f}")
    conclusions.append(f"- 평균 Weighted Degree: {df['Weighted_Degree'].mean():.2f}")
    conclusions.append(f"- 최대 Weighted Degree: {df['Weighted_Degree'].max():.2f}")
    conclusions.append(f"- 평균 Betweenness: {df['Betweenness_Centrality'].mean():.6f}")
    conclusions.append(f"- 최대 Betweenness: {df['Betweenness_Centrality'].max():.6f}")
    
    # 해석
    conclusions.append("\n【해석】\n")
    conclusions.append("1. Degree가 높은 스킬 = 많은 다른 스킬과 함께 요구되는 범용 스킬")
    conclusions.append("2. Weighted Degree가 높은 스킬 = 강하게 연결된 스킬 (자주 함께 등장)")
    conclusions.append("3. Betweenness가 높은 스킬 = 다른 스킬 군집을 연결하는 브릿지 역할")
    conclusions.append("4. Eigenvector/PageRank가 높은 스킬 = 중요 스킬들과 연결된 권위 있는 스킬")
    
    conclusion_text = "\n".join(conclusions)
    print(conclusion_text)
    
    return conclusion_text


def main():
    """메인 함수"""
    print("="*60)
    print("개발관련 스킬-스킬 네트워크 중심성 분석")
    print("="*60)
    
    # 현재 스크립트 위치 기준으로 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    # 입력 파일 경로
    input_file = os.path.join(parent_dir, 'developer_skill_skill_network.net')
    
    # 출력 디렉토리
    output_dir = script_dir
    
    if not os.path.exists(input_file):
        print(f"오류: '{input_file}' 파일을 찾을 수 없습니다.")
        return
    
    # 네트워크 로딩
    G, node_id_to_label = read_skill_network(input_file)
    
    # 중심성 지표 계산
    centralities = calculate_all_centralities(G)
    
    # DataFrame 생성
    df = create_centrality_dataframe(G, centralities, node_id_to_label)
    
    # Top 10 추출
    top_skills = compare_top_skills(df)
    
    # 결과 저장
    save_results(df, top_skills, output_dir)
    
    # 결론 도출
    conclusion_text = generate_conclusions(df, top_skills)
    
    # 결론 저장
    conclusion_path = os.path.join(output_dir, 'conclusions.txt')
    with open(conclusion_path, 'w', encoding='utf-8') as f:
        f.write(conclusion_text)
    print(f"\n✓ 결론 저장: {conclusion_path}")
    
    print("\n" + "="*60)
    print("분석 완료!")
    print("="*60)


if __name__ == "__main__":
    main()

