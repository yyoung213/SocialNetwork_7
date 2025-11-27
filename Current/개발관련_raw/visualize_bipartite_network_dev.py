"""
Bipartite Network 시각화 스크립트
developer_bipartite_skill_2mode.net 파일을 기반으로 다양한 시각화 전략을 구현합니다.
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict, Counter
import os


def read_2mode_network(file_path: str):
    """
    Pajek 2-mode 네트워크 파일을 정확히 파싱합니다.
    
    형식: *Vertices total_count first_mode_count
    - total_count: 총 노드 수
    - first_mode_count: 첫 번째 모드(기업)의 노드 수
    - 두 번째 모드(스킬) = total_count - first_mode_count
    
    Returns:
        G: NetworkX 그래프 (노드 ID를 키로 사용)
        companies: 기업 노드 ID 리스트
        skills: 스킬 노드 ID 리스트
        node_id_to_label: 노드 ID -> 레이블 매핑
        n_companies: 기업 수
        n_skills: 스킬 수
    """
    print(f"네트워크 파일 로딩 중: {file_path}")
    
    G = nx.Graph()
    companies = []  # 노드 ID 1 ~ n_companies
    skills = []      # 노드 ID n_companies+1 ~ total
    node_id_to_label = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 첫 줄에서 모드 정보 읽기
    first_line = lines[0].strip()
    parts = first_line.split()
    total_nodes = int(parts[1])
    n_companies = int(parts[2])
    n_skills = total_nodes - n_companies
    
    print(f"  총 노드 수: {total_nodes}개")
    print(f"  기업 수 (Mode 1): {n_companies}개")
    print(f"  스킬 수 (Mode 2): {n_skills}개")
    
    # Vertices 섹션 읽기
    vertices_started = False
    edges_started = False
    node_id = 1
    
    for line in lines:
        line_stripped = line.strip()
        
        # Vertices 섹션 시작
        if line_stripped.startswith('*Vertices'):
            vertices_started = True
            continue
        
        # Edges/Arcs 섹션 시작
        if line_stripped.startswith('*Edges') or line_stripped.startswith('*Arcs'):
            vertices_started = False
            edges_started = True
            continue
        
        # Vertices 읽기
        if vertices_started and line_stripped and not line_stripped.startswith('*'):
            if '"' in line_stripped:
                # 형식: "번호 "레이블" x y z"
                parts = line_stripped.split('"', 2)
                if len(parts) >= 2:
                    label = parts[1].strip()
                    node_id_to_label[node_id] = label
                    G.add_node(node_id, label=label)
                    
                    if node_id <= n_companies:
                        companies.append(node_id)
                    else:
                        skills.append(node_id)
                    
                    node_id += 1
        
        # Edges 읽기
        if edges_started and line_stripped and not line_stripped.startswith('*'):
            parts = line_stripped.split()
            if len(parts) >= 2:
                try:
                    source_id = int(parts[0])
                    target_id = int(parts[1])
                    weight = float(parts[2]) if len(parts) >= 3 else 1.0
                    
                    # 두 노드가 모두 존재하는지 확인
                    if source_id in node_id_to_label and target_id in node_id_to_label:
                        G.add_edge(source_id, target_id, weight=weight)
                except (ValueError, IndexError):
                    continue
    
    print(f"  실제 읽은 기업 노드: {len(companies)}개")
    print(f"  실제 읽은 스킬 노드: {len(skills)}개")
    print(f"  총 엣지: {G.number_of_edges()}개")
    
    return G, companies, skills, node_id_to_label, n_companies, n_skills


def strategy1_basic_bipartite(G, companies, skills, node_id_to_label, 
                              output_file='developer_bipartite_basic.png',
                              max_companies=50, max_skills=50):
    """
    전략 1: 기본 Bipartite 레이아웃 (양쪽 정렬) - 개선 버전
    """
    print("\n[전략 1] 기본 Bipartite 레이아웃 생성 중...")
    
    # 한글 폰트 설정
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    # Degree가 높은 노드 우선 선택
    degrees = dict(G.degree())
    
    # 기업: 많은 스킬을 요구하는 기업
    company_degrees = {n: degrees.get(n, 0) for n in companies if n in G.nodes()}
    top_companies = sorted(company_degrees.items(), key=lambda x: x[1], reverse=True)[:max_companies]
    top_company_ids = [n for n, _ in top_companies]
    
    # 스킬: 많은 기업이 요구하는 스킬
    skill_degrees = {n: degrees.get(n, 0) for n in skills if n in G.nodes()}
    top_skills = sorted(skill_degrees.items(), key=lambda x: x[1], reverse=True)[:max_skills]
    top_skill_ids = [n for n, _ in top_skills]
    
    # 서브그래프 생성
    selected_nodes = set(top_company_ids + top_skill_ids)
    subgraph_nodes = [n for n in G.nodes() if n in selected_nodes]
    G_sub = G.subgraph(subgraph_nodes)
    
    print(f"  선택된 기업: {len(top_company_ids)}개")
    print(f"  선택된 스킬: {len(top_skill_ids)}개")
    print(f"  서브그래프 엣지: {G_sub.number_of_edges()}개")
    
    # Bipartite 레이아웃: 기업은 왼쪽, 스킬은 오른쪽
    pos = {}
    
    # 기업을 왼쪽에 세로로 배치
    for i, company_id in enumerate(top_company_ids):
        if company_id in G_sub.nodes():
            pos[company_id] = (0, i * 0.8)
    
    # 스킬을 오른쪽에 세로로 배치
    for i, skill_id in enumerate(top_skill_ids):
        if skill_id in G_sub.nodes():
            pos[skill_id] = (3, i * 0.8)
    
    # 그래프 그리기
    fig, ax = plt.subplots(figsize=(24, max(len(top_companies), len(top_skills)) * 0.1))
    
    # 엣지 그리기 (먼저 그려서 노드 뒤에 배치)
    edges_to_draw = [(u, v) for u, v in G_sub.edges() if u in pos and v in pos]
    nx.draw_networkx_edges(G_sub, pos, edgelist=edges_to_draw,
                          alpha=0.2, width=0.5, ax=ax, edge_color='gray')
    
    # 노드 그리기
    company_nodes_in_sub = [n for n in top_company_ids if n in G_sub.nodes() and n in pos]
    skill_nodes_in_sub = [n for n in top_skill_ids if n in G_sub.nodes() and n in pos]
    
    # 노드 크기 (degree에 비례)
    company_sizes = [min(300, max(50, degrees.get(n, 1) * 3)) for n in company_nodes_in_sub]
    skill_sizes = [min(500, max(100, degrees.get(n, 1) * 5)) for n in skill_nodes_in_sub]
    
    nx.draw_networkx_nodes(G_sub, pos, nodelist=company_nodes_in_sub,
                          node_color='steelblue', node_size=company_sizes,
                          ax=ax, alpha=0.8, edgecolors='darkblue', linewidths=1)
    
    nx.draw_networkx_nodes(G_sub, pos, nodelist=skill_nodes_in_sub,
                          node_color='coral', node_size=skill_sizes,
                          ax=ax, alpha=0.8, edgecolors='darkred', linewidths=1)
    
    # 레이블 (일부만 표시)
    labels = {}
    for company_id in company_nodes_in_sub[:15]:
        label = node_id_to_label.get(company_id, f"Company {company_id}")
        if len(label) > 20:
            label = label[:17] + "..."
        labels[company_id] = label
    
    for skill_id in skill_nodes_in_sub[:20]:
        label = node_id_to_label.get(skill_id, f"Skill {skill_id}")
        labels[skill_id] = label
    
    nx.draw_networkx_labels(G_sub, pos, labels,
                           font_size=7, ax=ax, font_weight='bold',
                           font_family='Malgun Gothic')
    
    # 제목 및 범례
    ax.set_title(f"Bipartite Network: 기업 (왼쪽) ↔ 스킬 (오른쪽)\n"
                f"상위 {len(top_company_ids)}개 기업, 상위 {len(top_skill_ids)}개 스킬",
                fontsize=16, pad=20)
    
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='steelblue', alpha=0.8, label='기업 (Companies)'),
        Patch(facecolor='coral', alpha=0.8, label='스킬 (Skills)')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"  [OK] 저장 완료: {output_file}")
    
    # 통계 출력
    print(f"\n  상위 5개 기업 (많은 스킬 요구):")
    for i, (company_id, deg) in enumerate(top_companies[:5], 1):
        label = node_id_to_label.get(company_id, f"Company {company_id}")
        print(f"    {i}. {label}: {deg}개 스킬")
    
    print(f"\n  상위 5개 스킬 (많은 기업이 요구):")
    for i, (skill_id, deg) in enumerate(top_skills[:5], 1):
        label = node_id_to_label.get(skill_id, f"Skill {skill_id}")
        print(f"    {i}. {label}: {deg}개 기업")


def strategy2_degree_based(G, companies, skills, node_id_to_label, output_file='developer_bipartite_degree.png'):
    """
    전략 2: Degree 기반 노드 크기 및 위치
    """
    print("\n[전략 2] Degree 기반 시각화 생성 중...")
    
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    # Degree 계산
    degrees = dict(G.degree())
    company_degrees = {n: degrees.get(n, 0) for n in companies}
    skill_degrees = {n: degrees.get(n, 0) for n in skills}
    
    # 상위 노드 선택
    top_companies = sorted(company_degrees.items(), key=lambda x: x[1], reverse=True)[:50]
    top_skills = sorted(skill_degrees.items(), key=lambda x: x[1], reverse=True)[:50]
    
    top_company_nodes = [n for n, _ in top_companies]
    top_skill_nodes = [n for n, _ in top_skills]
    
    # Bipartite 레이아웃
    pos = {}
    for i, (company, deg) in enumerate(top_companies):
        pos[company] = (0, i * 0.05)
    
    for i, (skill, deg) in enumerate(top_skills):
        pos[skill] = (2, i * 0.05)
    
    # 노드 크기 (degree에 비례)
    company_sizes = [company_degrees[n] * 2 for n in top_company_nodes]
    skill_sizes = [skill_degrees[n] * 2 for n in top_skill_nodes]
    
    # 그래프 그리기
    fig, ax = plt.subplots(figsize=(20, 30))
    
    # 엣지
    edges_to_draw = [(u, v) for u, v in G.edges() 
                     if (u in pos and v in pos)]
    nx.draw_networkx_edges(G, pos, edgelist=edges_to_draw, 
                          alpha=0.1, width=0.3, ax=ax, edge_color='gray')
    
    # 노드
    nx.draw_networkx_nodes(G, pos, nodelist=top_company_nodes,
                          node_color='steelblue', node_size=company_sizes, 
                          ax=ax, alpha=0.8)
    nx.draw_networkx_nodes(G, pos, nodelist=top_skill_nodes,
                          node_color='coral', node_size=skill_sizes, 
                          ax=ax, alpha=0.8)
    
    # 레이블 (node_id_to_label 사용)
    labels = {}
    for node_id in top_company_nodes[:15]:
        label = node_id_to_label.get(node_id, f"Company {node_id}")
        if len(label) > 20:
            label = label[:17] + "..."
        labels[node_id] = label
    
    for node_id in top_skill_nodes[:15]:
        label = node_id_to_label.get(node_id, f"Skill {node_id}")
        labels[node_id] = label
    
    nx.draw_networkx_labels(G, pos, labels, font_size=7, ax=ax, font_weight='bold',
                           font_family='Malgun Gothic')
    
    # 제목 및 범례
    ax.set_title("Degree 기반 노드 크기\n(크기가 클수록 많은 연결)", fontsize=14)
    
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='steelblue', alpha=0.8, label='기업 (Companies)'),
        Patch(facecolor='coral', alpha=0.8, label='스킬 (Skills)')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"  [OK] 저장 완료: {output_file}")
    
    # 통계 출력
    print(f"\n  상위 5개 기업 (by degree):")
    for i, (company_id, deg) in enumerate(top_companies[:5], 1):
        label = node_id_to_label.get(company_id, f"Company {company_id}")
        print(f"    {i}. {label}: {deg}개 스킬")
    
    print(f"\n  상위 5개 스킬 (by degree):")
    for i, (skill_id, deg) in enumerate(top_skills[:5], 1):
        label = node_id_to_label.get(skill_id, f"Skill {skill_id}")
        print(f"    {i}. {label}: {deg}개 기업")


def strategy4_cooccurrence_heatmap(G, companies, skills, node_id_to_label, output_file='developer_cooccurrence_heatmap.png'):
    """
    전략 4: 스킬-스킬 Co-occurrence 히트맵
    """
    print("\n[전략 4] Co-occurrence 히트맵 생성 중...")
    
    try:
        import seaborn as sns
    except ImportError:
        print("  ⚠ seaborn이 설치되지 않았습니다. pip install seaborn")
        return
    
    # 각 기업의 스킬 리스트
    company_skills_dict = defaultdict(list)
    for company, skill in G.edges():
        if company in companies and skill in skills:
            company_skills_dict[company].append(skill)
    
    # Top 스킬 선택 (node_id 기반)
    skill_degrees = {n: G.degree(n) for n in skills if n in G.nodes()}
    top_skills = sorted(skill_degrees.items(), key=lambda x: x[1], reverse=True)[:30]
    top_skill_ids = [s_id for s_id, _ in top_skills]
    
    # 스킬 레이블 가져오기
    top_skill_labels = [node_id_to_label.get(s_id, f"Skill {s_id}") for s_id in top_skill_ids]
    
    # Co-occurrence 행렬 생성
    n = len(top_skill_ids)
    cooccurrence = np.zeros((n, n))
    
    for i, skill1_id in enumerate(top_skill_ids):
        for j, skill2_id in enumerate(top_skill_ids):
            if i != j:
                # 두 스킬을 모두 요구하는 기업 수
                count = sum(1 for comp_id in companies 
                          if comp_id in G.nodes() and 
                          skill1_id in G[comp_id] and skill2_id in G[comp_id])
                cooccurrence[i][j] = count
    
    # 히트맵 시각화
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots(figsize=(20, 16))
    
    sns.heatmap(cooccurrence, 
                xticklabels=top_skill_labels,
                yticklabels=top_skill_labels,
                cmap='YlOrRd',
                annot=False,
                fmt='.0f',
                cbar_kws={'label': 'Co-occurrence Count'},
                ax=ax)
    
    ax.set_title('스킬-스킬 Co-occurrence 히트맵\n(함께 요구되는 빈도)', fontsize=16, pad=20)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"  [OK] 저장 완료: {output_file}")
    
    # 상위 co-occurrence 쌍 출력
    print(f"\n  상위 5개 스킬 쌍 (co-occurrence):")
    pairs = []
    for i, skill1_id in enumerate(top_skill_ids):
        for j, skill2_id in enumerate(top_skill_ids):
            if i < j:
                skill1_label = top_skill_labels[i]
                skill2_label = top_skill_labels[j]
                pairs.append((skill1_label, skill2_label, cooccurrence[i][j]))
    
    top_pairs = sorted(pairs, key=lambda x: x[2], reverse=True)[:5]
    for i, (s1, s2, count) in enumerate(top_pairs, 1):
        print(f"    {i}. {s1} - {s2}: {int(count)}개 기업")


def strategy7_projection(G, companies, skills, node_id_to_label, output_file='developer_projection_networks.png'):
    """
    전략 7: Projection 네트워크 (기업-기업, 스킬-스킬)
    """
    print("\n[전략 7] Projection 네트워크 생성 중...")
    
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    # 기업-기업 네트워크 (공통 스킬 기반)
    print("  기업-기업 네트워크 생성 중...")
    G_companies = nx.bipartite.weighted_projected_graph(G, companies[:200])  # 상위 200개만
    
    # 스킬-스킬 네트워크 (같은 기업에서 요구되는 스킬)
    print("  스킬-스킬 네트워크 생성 중...")
    G_skills = nx.bipartite.weighted_projected_graph(G, skills[:200])  # 상위 200개만
    
    # 시각화
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(40, 20))
    
    # 1. 기업-기업 네트워크
    # k 값을 크게 하여 노드 간 거리 증가 (기본값보다 훨씬 크게)
    # 노드 수에 따라 k 값 조정
    num_companies = G_companies.number_of_nodes()
    k1 = max(5, num_companies ** 0.5)  # 노드 수의 제곱근에 비례하여 증가
    
    print(f"  기업 네트워크 레이아웃: k={k1:.2f}, iterations=300")
    pos1 = nx.spring_layout(G_companies, k=k1, iterations=300, seed=42)
    
    # 엣지 가중치에 따른 두께
    edges1 = G_companies.edges(data=True)
    weights1 = [d.get('weight', 1) for u, v, d in edges1]
    if weights1:
        max_weight1 = max(weights1)
        edge_widths1 = [w / max_weight1 * 2 for w in weights1]  # 두께 약간 줄임
    else:
        edge_widths1 = [0.5] * len(edges1)
    
    nx.draw_networkx_edges(G_companies, pos1, width=edge_widths1, 
                          alpha=0.2, ax=ax1, edge_color='gray')  # 투명도 낮춤
    
    # 노드 크기 (degree)
    degrees1 = dict(G_companies.degree())
    node_sizes1 = [degrees1[n] * 30 for n in G_companies.nodes()]  # 크기 약간 줄임
    
    nx.draw_networkx_nodes(G_companies, pos1, node_size=node_sizes1,
                          node_color='steelblue', alpha=0.8, ax=ax1,
                          edgecolors='darkblue', linewidths=0.5)
    
    # 레이블 (상위 10개만, node_id_to_label 사용)
    top_nodes1 = sorted(degrees1.items(), key=lambda x: x[1], reverse=True)[:10]
    labels1 = {}
    for node_id, _ in top_nodes1:
        label = node_id_to_label.get(node_id, f"Company {node_id}")
        if len(label) > 15:
            label = label[:12] + "..."
        labels1[node_id] = label
    nx.draw_networkx_labels(G_companies, pos1, labels1, font_size=8, ax=ax1,
                           font_family='Malgun Gothic', font_weight='bold')
    
    ax1.set_title(f"기업-기업 네트워크\n(공통 스킬 기반, {G_companies.number_of_nodes()}개 노드)", 
                  fontsize=14)
    ax1.axis('off')
    
    # 2. 스킬-스킬 네트워크
    # k 값을 크게 하여 노드 간 거리 증가
    num_skills = G_skills.number_of_nodes()
    k2 = max(5, num_skills ** 0.5)  # 노드 수의 제곱근에 비례하여 증가
    
    print(f"  스킬 네트워크 레이아웃: k={k2:.2f}, iterations=300")
    pos2 = nx.spring_layout(G_skills, k=k2, iterations=300, seed=42)
    
    edges2 = G_skills.edges(data=True)
    weights2 = [d.get('weight', 1) for u, v, d in edges2]
    if weights2:
        max_weight2 = max(weights2)
        edge_widths2 = [w / max_weight2 * 2 for w in weights2]  # 두께 약간 줄임
    else:
        edge_widths2 = [0.5] * len(edges2)
    
    nx.draw_networkx_edges(G_skills, pos2, width=edge_widths2,
                          alpha=0.2, ax=ax2, edge_color='gray')  # 투명도 낮춤
    
    degrees2 = dict(G_skills.degree())
    node_sizes2 = [degrees2[n] * 30 for n in G_skills.nodes()]  # 크기 약간 줄임
    
    nx.draw_networkx_nodes(G_skills, pos2, node_size=node_sizes2,
                          node_color='coral', alpha=0.8, ax=ax2,
                          edgecolors='darkred', linewidths=0.5)
    
    top_nodes2 = sorted(degrees2.items(), key=lambda x: x[1], reverse=True)[:10]
    labels2 = {}
    for node_id, _ in top_nodes2:
        label = node_id_to_label.get(node_id, f"Skill {node_id}")
        labels2[node_id] = label
    nx.draw_networkx_labels(G_skills, pos2, labels2, font_size=8, ax=ax2,
                           font_family='Malgun Gothic', font_weight='bold')
    
    ax2.set_title(f"스킬-스킬 네트워크\n(같은 기업에서 요구, {G_skills.number_of_nodes()}개 노드)",
                  fontsize=14)
    ax2.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  [OK] 저장 완료: {output_file}")


def main():
    """메인 함수"""
    print("="*60)
    print("Bipartite Network 시각화")
    print("="*60)
    
    # 현재 디렉토리로 이동
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 네트워크 파일 경로
    net_file = 'developer_bipartite_skill_2mode.net'
    if not os.path.exists(net_file):
        print(f"오류: '{net_file}' 파일을 찾을 수 없습니다.")
        return
    
    # 네트워크 로딩
    G, companies, skills, node_id_to_label, n_companies, n_skills = read_2mode_network(net_file)
    
    # 각 전략 실행
    try:
        strategy1_basic_bipartite(G, companies, skills, node_id_to_label)
    except Exception as e:
        print(f"  ⚠ 전략 1 실행 중 오류: {e}")
    
    try:
        strategy2_degree_based(G, companies, skills, node_id_to_label)
    except Exception as e:
        print(f"  ⚠ 전략 2 실행 중 오류: {e}")
    
    try:
        strategy4_cooccurrence_heatmap(G, companies, skills, node_id_to_label)
    except Exception as e:
        print(f"  ⚠ 전략 4 실행 중 오류: {e}")
    
    try:
        strategy7_projection(G, companies, skills, node_id_to_label)
    except Exception as e:
        print(f"  ⚠ 전략 7 실행 중 오류: {e}")
    
    print("\n" + "="*60)
    print("완료!")
    print("="*60)


if __name__ == "__main__":
    main()

