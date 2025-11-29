"""
공고-스킬 Bipartite Network 시각화 스크립트

1. 기본적인 Bipartite Network 시각화
2. 상세한 Bipartite Network 시각화:
   - 공고 노드 작게, 스킬 노드 크게
   - 스킬 노드 크기는 해당 스킬을 요구하는 공고 수(차수)에 비례
   - 직무별 색상 구분
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
import numpy as np
import os
from collections import defaultdict

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
plt.rcParams['axes.unicode_minus'] = False

def parse_pajek_bipartite(file_path):
    """Pajek 형식의 bipartite 네트워크 파일을 파싱합니다."""
    print(f"[1단계] Pajek 파일 파싱: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 헤더 파싱
    header = lines[0].strip()
    parts = header.split()
    total_nodes = int(parts[1])
    n_jobs = int(parts[2])  # Mode 1 (공고) 노드 수
    
    print(f"  총 노드 수: {total_nodes}")
    print(f"  공고 노드 수 (Mode 1): {n_jobs}")
    print(f"  스킬 노드 수 (Mode 2): {total_nodes - n_jobs}")
    
    # 노드 정보 파싱
    job_nodes = {}  # {node_id: job_type}
    skill_nodes = {}  # {node_id: skill_name}
    
    i = 1
    # 공고 노드 (Mode 1)
    for idx in range(n_jobs):
        if i >= len(lines):
            break
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        parts = line.split('"')
        if len(parts) >= 2:
            node_id = int(parts[0].strip())
            job_type = parts[1].strip()
            job_nodes[node_id] = job_type
        i += 1
    
    # 스킬 노드 (Mode 2)
    for idx in range(total_nodes - n_jobs):
        if i >= len(lines):
            break
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        parts = line.split('"')
        if len(parts) >= 2:
            node_id = int(parts[0].strip())
            skill_name = parts[1].strip()
            skill_nodes[node_id] = skill_name
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
            job_id = int(parts[0])
            skill_id = int(parts[1])
            if job_id in job_nodes and skill_id in skill_nodes:
                edges.append((job_id, skill_id))
        i += 1
    
    print(f"  엣지 수: {len(edges)}")
    
    return job_nodes, skill_nodes, edges, n_jobs, total_nodes


def load_job_type_mapping(edges_csv_path, skill_nodes):
    """CSV 파일에서 job_id와 job_type 매핑을 로드하고, 엣지 정보를 사용하여 노드 매핑을 생성합니다."""
    print(f"[2단계] 직무 정보 로드: {edges_csv_path}")
    
    df = pd.read_csv(edges_csv_path, encoding='utf-8-sig')
    
    # 스킬 이름 -> 노드 ID 역매핑 생성
    skill_name_to_id = {name: node_id for node_id, name in skill_nodes.items()}
    
    # job_id -> job_type 매핑
    job_id_to_type = {}
    for _, row in df.iterrows():
        job_id_str = str(row['job_id'])
        job_type = str(row['job_type'])
        job_id_to_type[job_id_str] = job_type
    
    # 엣지 정보를 사용하여 노드 ID -> job_type 매핑 생성
    # CSV의 job_id는 "직군명_번호" 형식이므로, 이를 사용하여 매핑
    node_id_to_job_type = {}
    job_counter = defaultdict(int)  # 각 직군별 카운터
    
    # CSV의 각 행을 순회하며 노드 매핑 생성
    for _, row in df.iterrows():
        job_id_str = str(row['job_id'])
        job_type = str(row['job_type'])
        skill_name = str(row['skill'])
        
        # 스킬 노드 ID 찾기
        if skill_name in skill_name_to_id:
            skill_node_id = skill_name_to_id[skill_name]
            
            # job_id에서 번호 추출 (예: "BI 엔지니어_1" -> 1)
            try:
                job_num = int(job_id_str.split('_')[-1])
                # 노드 ID는 1부터 시작하므로, 직군별로 순차적으로 매핑
                # 실제로는 CSV의 순서를 사용하여 매핑해야 함
            except:
                pass
    
    # 더 간단한 방법: CSV의 job_id를 순서대로 사용하여 노드 ID와 매핑
    # 각 직군별로 첫 번째 등장하는 job_id를 노드 ID 1부터 매핑
    job_id_list = df['job_id'].unique()
    job_id_sorted = sorted(job_id_list)
    
    # 노드 ID -> job_type 매핑 (직군명을 사용)
    node_id_to_job_type = {}
    current_node_id = 1
    
    for job_id in job_id_sorted:
        job_type = job_id_to_type[job_id]
        # 같은 직군의 연속된 노드들은 같은 job_type을 가짐
        # 실제로는 CSV의 순서를 사용해야 하지만, 여기서는 직군명을 사용
        node_id_to_job_type[current_node_id] = job_type
        current_node_id += 1
    
    print(f"  로드된 공고-직무 매핑 수: {len(job_id_to_type)}")
    print(f"  노드 ID -> 직무 매핑 수: {len(node_id_to_job_type)}")
    
    return job_id_to_type, node_id_to_job_type


def create_bipartite_graph_from_csv(edges_csv_path):
    """CSV 파일을 직접 사용하여 Bipartite 네트워크 그래프를 생성합니다."""
    print(f"[3단계] CSV 파일로부터 Bipartite 그래프 생성")
    
    df = pd.read_csv(edges_csv_path, encoding='utf-8-sig')
    
    G = nx.Graph()
    
    # 고유한 job_id와 skill 추출
    unique_jobs = df['job_id'].unique()
    unique_skills = df['skill'].unique()
    
    # 노드 추가 (공고 노드)
    job_id_to_node = {}
    for idx, job_id in enumerate(unique_jobs, 1):
        job_type = df[df['job_id'] == job_id]['job_type'].iloc[0]
        G.add_node(job_id, node_type='job', job_type=job_type, label=job_id)
        job_id_to_node[job_id] = job_id
    
    # 노드 추가 (스킬 노드)
    skill_name_to_node = {}
    for skill_name in unique_skills:
        G.add_node(skill_name, node_type='skill', skill_name=skill_name, label=skill_name)
        skill_name_to_node[skill_name] = skill_name
    
    # 엣지 추가
    for _, row in df.iterrows():
        job_id = str(row['job_id'])
        skill_name = str(row['skill'])
        if job_id in job_id_to_node and skill_name in skill_name_to_node:
            G.add_edge(job_id, skill_name)
    
    print(f"  그래프 노드 수: {G.number_of_nodes()}")
    print(f"  그래프 엣지 수: {G.number_of_edges()}")
    print(f"  공고 노드 수: {len(unique_jobs)}")
    print(f"  스킬 노드 수: {len(unique_skills)}")
    
    return G, unique_jobs, unique_skills


def get_job_type_colors():
    """직무별 색상 매핑을 반환합니다."""
    job_types = [
        'BI 엔지니어', 'DBA', '데이터 분석가', '데이터 사이언티스트',
        '데이터 엔지니어', '머신러닝 엔지니어', '빅데이터 엔지니어', '프로덕트 매니저'
    ]
    
    # 데이터 관련 직군을 그룹화하여 색상 할당
    # 데이터 직군: 파란색 계열
    # 프로덕트 매니저: 다른 색상
    colors = {
        'BI 엔지니어': '#4A90E2',  # 파란색
        'DBA': '#5B9BD5',  # 밝은 파란색
        '데이터 분석가': '#4472C4',  # 진한 파란색
        '데이터 사이언티스트': '#2E75B6',  # 더 진한 파란색
        '데이터 엔지니어': '#1F4E78',  # 매우 진한 파란색
        '머신러닝 엔지니어': '#0070C0',  # 시안 파란색
        '빅데이터 엔지니어': '#00B0F0',  # 밝은 시안
        '프로덕트 매니저': '#FF6B6B'  # 빨간색 계열
    }
    
    return colors


def visualize_basic_bipartite(G, output_path):
    """기본적인 Bipartite Network 시각화"""
    print(f"[4단계] 기본 Bipartite Network 시각화 생성")
    
    fig, ax = plt.subplots(figsize=(20, 16))
    
    # 노드 분리
    job_nodes_list = [n for n in G.nodes() if G.nodes[n]['node_type'] == 'job']
    skill_nodes_list = [n for n in G.nodes() if G.nodes[n]['node_type'] == 'skill']
    
    # Bipartite 레이아웃
    pos = nx.bipartite_layout(G, job_nodes_list, align='vertical')
    
    # 공고 노드 (작게, 회색)
    nx.draw_networkx_nodes(G, pos, nodelist=job_nodes_list, 
                          node_color='lightgray', node_size=10, 
                          alpha=0.6, ax=ax)
    
    # 스킬 노드 (크게, 파란색)
    nx.draw_networkx_nodes(G, pos, nodelist=skill_nodes_list,
                          node_color='steelblue', node_size=50,
                          alpha=0.7, ax=ax)
    
    # 엣지 그리기 (얇고 반투명)
    nx.draw_networkx_edges(G, pos, alpha=0.1, width=0.5, ax=ax)
    
    # 레이블 (스킬 노드만, 상위 20개만)
    skill_degrees = [(n, G.degree(n)) for n in skill_nodes_list]
    skill_degrees.sort(key=lambda x: x[1], reverse=True)
    top_skills = [n for n, _ in skill_degrees[:20]]
    
    labels = {}
    for node_id in top_skills:
        labels[node_id] = G.nodes[node_id]['label']
    
    nx.draw_networkx_labels(G, pos, labels, font_size=6, ax=ax)
    
    ax.set_title('공고-스킬 Bipartite Network (기본 시각화)', fontsize=16, pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  저장 완료: {output_path}")
    plt.close()


def visualize_detailed_bipartite(G, output_path):
    """상세한 Bipartite Network 시각화"""
    print(f"[5단계] 상세 Bipartite Network 시각화 생성")
    
    fig, ax = plt.subplots(figsize=(24, 18))
    
    # 직무별 색상 매핑
    job_type_colors = get_job_type_colors()
    
    # 노드 분리
    job_nodes_list = [n for n in G.nodes() if G.nodes[n]['node_type'] == 'job']
    skill_nodes_list = [n for n in G.nodes() if G.nodes[n]['node_type'] == 'skill']
    
    # 스킬 노드의 차수 계산 (해당 스킬을 요구하는 공고 수)
    skill_degrees = {node_id: G.degree(node_id) for node_id in skill_nodes_list}
    
    # 스킬 노드 크기 계산 (차수에 비례, 최소/최대 크기 설정)
    min_size = 50
    max_size = 500
    if skill_degrees:
        min_degree = min(skill_degrees.values())
        max_degree = max(skill_degrees.values())
        
        def size_func(degree):
            if max_degree == min_degree:
                return (min_size + max_size) / 2
            return min_size + (max_size - min_size) * (degree - min_degree) / (max_degree - min_degree)
    else:
        def size_func(degree):
            return min_size
    
    # 공고 노드의 직무별 색상 매핑
    job_node_colors = {}
    for node_id in job_nodes_list:
        job_type = G.nodes[node_id].get('job_type', '기타')
        job_node_colors[node_id] = job_type_colors.get(job_type, '#CCCCCC')
    
    # Bipartite 레이아웃
    pos = nx.bipartite_layout(G, job_nodes_list, align='vertical')
    
    # 레이아웃 개선: 스킬 노드를 차수에 따라 재배치
    # 차수가 높은 스킬을 중앙에 배치
    skill_degrees_sorted = sorted(skill_degrees.items(), key=lambda x: x[1], reverse=True)
    
    # 공고 노드를 직무별로 그룹화하여 재배치
    job_type_groups = defaultdict(list)
    for node_id in job_nodes_list:
        job_type = G.nodes[node_id].get('job_type', '기타')
        job_type_groups[job_type].append(node_id)
    
    # 각 직무 그룹 내에서 노드 위치 조정
    y_offset = 0
    for job_type, nodes in sorted(job_type_groups.items()):
        for i, node_id in enumerate(nodes):
            if node_id in pos:
                pos[node_id] = (pos[node_id][0], y_offset + i * 0.01)
        y_offset += len(nodes) * 0.01 + 0.1
    
    # 공고 노드 그리기 (작게, 직무별 색상)
    job_colors_list = [job_node_colors.get(n, '#CCCCCC') for n in job_nodes_list]
    nx.draw_networkx_nodes(G, pos, nodelist=job_nodes_list,
                          node_color=job_colors_list, node_size=15,
                          alpha=0.5, ax=ax, edgecolors='black', linewidths=0.3)
    
    # 스킬 노드 그리기 (크게, 차수에 비례한 크기)
    skill_sizes = [size_func(skill_degrees.get(n, 0)) for n in skill_nodes_list]
    nx.draw_networkx_nodes(G, pos, nodelist=skill_nodes_list,
                          node_color='steelblue', node_size=skill_sizes,
                          alpha=0.8, ax=ax, edgecolors='darkblue', linewidths=1.5)
    
    # 엣지 그리기 (얇고 반투명)
    nx.draw_networkx_edges(G, pos, alpha=0.08, width=0.3, ax=ax, edge_color='gray')
    
    # 상위 스킬 레이블 표시
    top_skills = [n for n, _ in skill_degrees_sorted[:30]]
    labels = {}
    for node_id in top_skills:
        skill_name = G.nodes[node_id]['label']
        degree = skill_degrees[node_id]
        labels[node_id] = f"{skill_name}\n({degree})"
    
    nx.draw_networkx_labels(G, pos, labels, font_size=7, ax=ax, font_weight='bold')
    
    # 범례 생성
    legend_elements = []
    for job_type, color in job_type_colors.items():
        legend_elements.append(mpatches.Patch(color=color, label=job_type))
    
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10, framealpha=0.9)
    
    ax.set_title('공고-스킬 Bipartite Network (상세 시각화)\n스킬 노드 크기 = 요구 공고 수, 색상 = 직무', 
                 fontsize=18, pad=20, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  저장 완료: {output_path}")
    plt.close()


def create_improved_visualization(G, output_path):
    """개선된 Bipartite Network 시각화 - TOP 3 스킬 강조"""
    print(f"[6단계] 개선된 Bipartite Network 시각화 생성 (TOP 3 스킬 강조)")
    
    fig, ax = plt.subplots(figsize=(28, 20))
    
    # 직무별 색상 매핑
    job_type_colors = get_job_type_colors()
    
    # 노드 분리
    job_nodes_list = [n for n in G.nodes() if G.nodes[n]['node_type'] == 'job']
    skill_nodes_list = [n for n in G.nodes() if G.nodes[n]['node_type'] == 'skill']
    
    # 스킬 노드의 차수 계산
    skill_degrees = {n: G.degree(n) for n in skill_nodes_list}
    
    # TOP 3 스킬 식별
    skill_degrees_sorted = sorted(skill_degrees.items(), key=lambda x: x[1], reverse=True)
    top3_skills = [n for n, _ in skill_degrees_sorted[:3]]
    top3_degrees = {n: skill_degrees[n] for n in top3_skills}
    
    print(f"  TOP 3 스킬:")
    for i, (skill_node, degree) in enumerate(skill_degrees_sorted[:3], 1):
        skill_name = G.nodes[skill_node]['label']
        print(f"    {i}. {skill_name}: {degree}개 공고")
    
    # 스킬 노드 크기 계산 - TOP 3와 나머지를 명확히 구분
    # TOP 3: 매우 크게 (1500-2500)
    # 나머지: 작게 (20-80)
    top3_min_size = 1500
    top3_max_size = 2500
    other_min_size = 20
    other_max_size = 80
    
    def size_func(node_id, degree):
        if node_id in top3_skills:
            # TOP 3는 차수에 따라 크기 조정 (1위가 가장 크게)
            rank = top3_skills.index(node_id) + 1
            if rank == 1:
                return top3_max_size
            elif rank == 2:
                return top3_min_size + (top3_max_size - top3_min_size) * 0.7
            else:  # rank == 3
                return top3_min_size + (top3_max_size - top3_min_size) * 0.4
        else:
            # 나머지는 작게, 차수에 따라 약간의 변화만
            other_degrees = [d for n, d in skill_degrees.items() if n not in top3_skills]
            if other_degrees:
                min_other = min(other_degrees)
                max_other = max(other_degrees)
                if max_other == min_other:
                    return (other_min_size + other_max_size) / 2
                normalized = (degree - min_other) / (max_other - min_other)
                return other_min_size + (other_max_size - other_min_size) * normalized
            return other_min_size
    
    # 공고 노드의 직무별 색상 및 그룹화
    job_node_colors = {}
    job_node_groups = defaultdict(list)
    
    for node_id in job_nodes_list:
        job_type = G.nodes[node_id].get('job_type', '기타')
        color = job_type_colors.get(job_type, '#CCCCCC')
        job_node_colors[node_id] = color
        job_node_groups[job_type].append(node_id)
    
    # Bipartite 레이아웃
    pos = nx.bipartite_layout(G, job_nodes_list, align='vertical')
    
    # 레이아웃 개선: 공고 노드를 직무별로 그룹화하여 재배치
    job_type_groups = defaultdict(list)
    for node_id in job_nodes_list:
        job_type = G.nodes[node_id].get('job_type', '기타')
        job_type_groups[job_type].append(node_id)
    
    # 각 직무 그룹 내에서 노드 위치 조정 (더 명확한 그룹화)
    y_positions = {}
    y_offset = 0
    for job_type, nodes in sorted(job_type_groups.items()):
        group_size = len(nodes)
        for i, node_id in enumerate(nodes):
            if node_id in pos:
                # 그룹 내에서 균등하게 배치
                y_pos = y_offset + (i / max(1, group_size - 1)) * min(group_size * 0.15, 2.0)
                pos[node_id] = (pos[node_id][0], y_pos)
        y_offset += min(group_size * 0.15, 2.0) + 0.2
    
    # 엣지 그리기 (먼저 그려서 노드 아래에)
    nx.draw_networkx_edges(G, pos, alpha=0.05, width=0.2, ax=ax, edge_color='gray')
    
    # 공고 노드 그리기 (작게, 직무별 색상, 그룹별로)
    for job_type, nodes in job_node_groups.items():
        color = job_type_colors.get(job_type, '#CCCCCC')
        nx.draw_networkx_nodes(G, pos, nodelist=nodes,
                              node_color=color, node_size=20,
                              alpha=0.6, ax=ax, edgecolors='white', linewidths=0.5,
                              label=job_type)
    
    # 스킬 노드를 TOP 3와 나머지로 분리하여 그리기
    other_skill_nodes = [n for n in skill_nodes_list if n not in top3_skills]
    
    # 나머지 스킬 노드 먼저 그리기 (작게, 회색 계열)
    other_skill_sizes = [size_func(n, skill_degrees.get(n, 0)) for n in other_skill_nodes]
    nx.draw_networkx_nodes(G, pos, nodelist=other_skill_nodes,
                          node_color='#B0B0B0', node_size=other_skill_sizes,
                          alpha=0.4, ax=ax, edgecolors='#808080', linewidths=1)
    
    # TOP 3 스킬 노드 그리기 (매우 크게, 강조 색상)
    top3_colors = ['#FF6B6B', '#4ECDC4', '#FFE66D']  # 빨강, 청록, 노랑
    top3_sizes = [size_func(n, skill_degrees.get(n, 0)) for n in top3_skills]
    
    for i, (node_id, size) in enumerate(zip(top3_skills, top3_sizes)):
        color = top3_colors[i]
        nx.draw_networkx_nodes(G, pos, nodelist=[node_id],
                              node_color=color, node_size=size,
                              alpha=0.9, ax=ax, edgecolors='#000000', linewidths=4)
    
    # TOP 3 스킬 레이블만 표시 (큰 폰트, 명확한 색상)
    labels = {}
    for i, node_id in enumerate(top3_skills):
        skill_name = G.nodes[node_id]['label']
        degree = skill_degrees[node_id]
        rank = i + 1
        labels[node_id] = f"#{rank} {skill_name}\n({degree}개 공고)"
    
    # 레이블을 노드 옆에 배치 (더 명확하게)
    label_pos = {}
    for node_id in top3_skills:
        x, y = pos[node_id]
        # 노드 오른쪽에 레이블 배치
        label_pos[node_id] = (x + 0.15, y)
    
    for node_id, label_text in labels.items():
        x, y = label_pos[node_id]
        ax.text(x, y, label_text, fontsize=16, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                        edgecolor='black', linewidth=2, alpha=0.9),
               verticalalignment='center', horizontalalignment='left')
    
    # 범례 생성 (직무별)
    legend_elements = []
    for job_type, color in sorted(job_type_colors.items()):
        legend_elements.append(mpatches.Patch(color=color, label=job_type))
    
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11, 
             framealpha=0.95, title='직무 구분', title_fontsize=12)
    
    # TOP 3 스킬 정보 박스 추가
    top3_info = "TOP 3 스킬 (요구 공고 수 기준):\n"
    for i, (node_id, degree) in enumerate(skill_degrees_sorted[:3], 1):
        skill_name = G.nodes[node_id]['label']
        top3_info += f"{i}. {skill_name}: {degree}개 공고\n"
    
    ax.text(0.02, 0.15, top3_info, transform=ax.transAxes,
           fontsize=12, verticalalignment='top', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='lightyellow', 
                    edgecolor='black', linewidth=2, alpha=0.9))
    
    # 통계 정보 추가
    stats_text = f"총 공고 수: {len(job_nodes_list):,}개\n"
    stats_text += f"총 스킬 수: {len(skill_nodes_list):,}개\n"
    stats_text += f"총 연결 수: {G.number_of_edges():,}개"
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
           fontsize=11, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax.set_title('공고-스킬 Bipartite Network (개선된 시각화)\n'
                 'TOP 3 스킬 강조: 크기와 레이블로 명확히 표시, 나머지 스킬은 작게 표시', 
                 fontsize=20, pad=25, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  저장 완료: {output_path}")
    plt.close()


def main():
    """메인 함수"""
    print("=" * 70)
    print("공고-스킬 Bipartite Network 시각화")
    print("=" * 70)
    
    # 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    network_file = os.path.join(script_dir, 'posting_skill_bipartite_2mode.net')
    edges_csv = os.path.join(script_dir, 'posting_skill_bipartite_edges.csv')
    output_dir = os.path.join(parent_dir, 'post_skill_BipartiteVisul')
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # CSV 파일을 직접 사용하여 그래프 생성 (더 정확함)
    G, unique_jobs, unique_skills = create_bipartite_graph_from_csv(edges_csv)
    
    # 4단계: 기본 시각화
    basic_output = os.path.join(output_dir, 'bipartite_basic.png')
    visualize_basic_bipartite(G, basic_output)
    
    # 5단계: 상세 시각화
    detailed_output = os.path.join(output_dir, 'bipartite_detailed.png')
    visualize_detailed_bipartite(G, detailed_output)
    
    # 6단계: 개선된 시각화
    improved_output = os.path.join(output_dir, 'bipartite_improved.png')
    create_improved_visualization(G, improved_output)
    
    print("\n" + "=" * 70)
    print("작업 완료!")
    print(f"결과물 저장 위치: {output_dir}")
    print("=" * 70)


if __name__ == '__main__':
    main()

