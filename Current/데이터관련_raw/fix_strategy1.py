"""
전략 1: 기본 Bipartite 레이아웃 (수정 버전)
Pajek 2-mode 네트워크 형식을 정확히 파싱하여 시각화
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os


def read_pajek_2mode(file_path: str):
    """
    Pajek 2-mode 네트워크 파일을 정확히 파싱합니다.
    
    형식: *Vertices total_count first_mode_count
    - total_count: 총 노드 수
    - first_mode_count: 첫 번째 모드(기업)의 노드 수
    - 두 번째 모드(스킬) = total_count - first_mode_count
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


def strategy1_basic_bipartite_improved(G, companies, skills, node_id_to_label, 
                                      output_file='bipartite_basic_improved.png',
                                      max_companies=50, max_skills=50):
    """
    전략 1: 기본 Bipartite 레이아웃 (개선 버전)
    - 양쪽 정렬 레이아웃
    - 가독성 향상
    """
    print("\n[전략 1] 기본 Bipartite 레이아웃 생성 중 (개선 버전)...")
    
    # 한글 폰트 설정
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    # 서브그래프 생성 (상위 노드만 선택하여 가독성 향상)
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
    
    # 노드 크기 (degree에 비례, 최소/최대 제한)
    company_sizes = []
    for n in company_nodes_in_sub:
        deg = degrees.get(n, 1)
        size = min(300, max(50, deg * 3))
        company_sizes.append(size)
    
    skill_sizes = []
    for n in skill_nodes_in_sub:
        deg = degrees.get(n, 1)
        size = min(500, max(100, deg * 5))
        skill_sizes.append(size)
    
    nx.draw_networkx_nodes(G_sub, pos, nodelist=company_nodes_in_sub,
                          node_color='steelblue', node_size=company_sizes,
                          ax=ax, alpha=0.8, edgecolors='darkblue', linewidths=1)
    
    nx.draw_networkx_nodes(G_sub, pos, nodelist=skill_nodes_in_sub,
                          node_color='coral', node_size=skill_sizes,
                          ax=ax, alpha=0.8, edgecolors='darkred', linewidths=1)
    
    # 레이블 (일부만 표시하여 가독성 향상)
    labels = {}
    
    # 상위 15개 기업 레이블
    for company_id in company_nodes_in_sub[:15]:
        label = node_id_to_label.get(company_id, f"Company {company_id}")
        # 레이블 길이 제한
        if len(label) > 20:
            label = label[:17] + "..."
        labels[company_id] = label
    
    # 상위 20개 스킬 레이블
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
    
    # 범례 추가
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='steelblue', alpha=0.8, label='기업 (Companies)'),
        Patch(facecolor='coral', alpha=0.8, label='스킬 (Skills)')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"  ✓ 저장 완료: {output_file}")
    
    # 통계 출력
    print(f"\n  상위 5개 기업 (많은 스킬 요구):")
    for i, (company_id, deg) in enumerate(top_companies[:5], 1):
        label = node_id_to_label.get(company_id, f"Company {company_id}")
        print(f"    {i}. {label}: {deg}개 스킬")
    
    print(f"\n  상위 5개 스킬 (많은 기업이 요구):")
    for i, (skill_id, deg) in enumerate(top_skills[:5], 1):
        label = node_id_to_label.get(skill_id, f"Skill {skill_id}")
        print(f"    {i}. {label}: {deg}개 기업")


def main():
    """메인 함수"""
    print("="*60)
    print("전략 1: 기본 Bipartite 레이아웃 (개선 버전)")
    print("="*60)
    
    # 현재 디렉토리로 이동
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 네트워크 파일 경로
    net_file = 'data_bipartite_skill_2mode.net'
    if not os.path.exists(net_file):
        print(f"오류: '{net_file}' 파일을 찾을 수 없습니다.")
        return
    
    # 네트워크 로딩
    G, companies, skills, node_id_to_label, n_companies, n_skills = read_pajek_2mode(net_file)
    
    # 전략 1 실행
    try:
        strategy1_basic_bipartite_improved(G, companies, skills, node_id_to_label,
                                          max_companies=50, max_skills=50)
        print("\n✓ 전략 1 완료!")
        print("출력 파일: bipartite_basic_improved.png")
    except Exception as e:
        print(f"\n⚠ 전략 1 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()



