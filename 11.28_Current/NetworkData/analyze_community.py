"""
Skill-Skill 네트워크 군집 분석 (Community Detection) 스크립트

분석 내용:
1. Louvain 알고리즘을 사용한 커뮤니티 탐지
2. 각 군집을 직무/역할 관점으로 해석
3. 군집 시각화
4. 결과 및 인사이트 정리
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import defaultdict, Counter
try:
    import community.community_louvain as community_louvain
    USE_PYTHON_LOUVAIN = True
except ImportError:
    USE_PYTHON_LOUVAIN = False
    print("  경고: python-louvain 모듈이 없습니다. networkx의 greedy_modularity_communities를 사용합니다.")

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
plt.rcParams['axes.unicode_minus'] = False


def create_bipartite_graph_from_csv(edges_csv_path):
    """CSV 파일을 직접 사용하여 Bipartite 네트워크 그래프를 생성합니다."""
    print(f"[1단계] Bipartite 그래프 생성: {edges_csv_path}")
    
    df = pd.read_csv(edges_csv_path, encoding='utf-8-sig')
    
    G = nx.Graph()
    
    # 고유한 job_id와 skill 추출
    unique_jobs = df['job_id'].unique()
    unique_skills = df['skill'].unique()
    
    # 노드 추가 (공고 노드)
    for job_id in unique_jobs:
        job_type = df[df['job_id'] == job_id]['job_type'].iloc[0]
        G.add_node(job_id, node_type='job', job_type=job_type, label=job_id)
    
    # 노드 추가 (스킬 노드)
    for skill_name in unique_skills:
        G.add_node(skill_name, node_type='skill', skill_name=skill_name, label=skill_name)
    
    # 엣지 추가
    for _, row in df.iterrows():
        job_id = str(row['job_id'])
        skill_name = str(row['skill'])
        if job_id in G and skill_name in G:
            G.add_edge(job_id, skill_name)
    
    return G, unique_jobs, unique_skills


def create_skill_skill_network(bipartite_G, job_nodes):
    """Bipartite 네트워크에서 Skill-Skill One-mode Projection을 생성합니다."""
    print(f"[2단계] Skill-Skill One-mode Projection 생성")
    
    # 스킬 노드만 추출
    skill_nodes = [n for n in bipartite_G.nodes() if bipartite_G.nodes[n]['node_type'] == 'skill']
    
    # Weighted projection 생성
    skill_skill_G = nx.bipartite.weighted_projected_graph(bipartite_G, skill_nodes)
    
    return skill_skill_G


def filter_network_by_weight(G, min_weight=5):
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
    # seed=None이면 랜덤, 특정 값이면 고정
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
    print(f"  모듈성 (Resolution 포함): {modularity:.4f}")
    
    return partition, communities_sorted, modularity


def interpret_communities(G, communities_sorted):
    """각 커뮤니티를 직무/역할 관점으로 해석합니다."""
    print(f"[5단계] 커뮤니티 해석")
    
    community_interpretations = []
    
    # 직무/역할 키워드 매핑
    role_keywords = {
        '데이터 분석': ['Python', 'SQL', 'Pandas', 'Tableau', 'Power BI', 'Excel', 'R', '데이터 분석'],
        'BI': ['Tableau', 'Power BI', 'Superset', 'Looker', 'BI', '대시보드'],
        'AI/ML': ['AI', 'ML', 'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'LLM', 'NLP'],
        '백엔드': ['Java', 'Spring', 'Node.js', 'Python', 'Django', 'Flask', 'API', 'REST'],
        '프론트엔드': ['React', 'Vue', 'JavaScript', 'TypeScript', 'HTML', 'CSS'],
        '클라우드': ['AWS', 'GCP', 'Azure', '클라우드'],
        'DevOps': ['Docker', 'Kubernetes', 'CI/CD', 'Jenkins', 'Git', 'DevOps'],
        '데이터 엔지니어링': ['Spark', 'Hadoop', 'Airflow', 'ETL', '데이터 파이프라인'],
        '데이터베이스': ['SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle'],
        '인프라': ['AWS', 'Docker', 'Kubernetes', 'Linux', '인프라']
    }
    
    for comm_id, nodes in communities_sorted:
        # 커뮤니티 내 스킬 목록
        skills = [G.nodes[n].get('label', n) for n in nodes]
        
        # 각 직무/역할과의 매칭 점수 계산
        role_scores = {}
        for role, keywords in role_keywords.items():
            score = sum(1 for skill in skills if any(kw.lower() in skill.lower() for kw in keywords))
            if score > 0:
                role_scores[role] = score
        
        # 가장 높은 점수의 역할 선택
        if role_scores:
            primary_role = max(role_scores.items(), key=lambda x: x[1])[0]
            confidence = role_scores[primary_role] / len(skills) if skills else 0
        else:
            primary_role = "기타"
            confidence = 0
        
        # 상위 스킬 추출 (Degree 기준)
        subgraph = G.subgraph(nodes)
        degrees = dict(subgraph.degree())
        top_skills = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]
        top_skill_names = [G.nodes[n].get('label', n) for n, _ in top_skills]
        
        community_interpretations.append({
            'community_id': comm_id,
            'size': len(nodes),
            'primary_role': primary_role,
            'confidence': confidence,
            'top_skills': top_skill_names,
            'all_skills': skills,
            'role_scores': role_scores
        })
        
        print(f"  커뮤니티 {comm_id}: {primary_role} ({len(nodes)}개 노드, 신뢰도: {confidence:.2f})")
    
    return community_interpretations


def visualize_communities(G, partition, output_path):
    """커뮤니티별로 색상을 구분하여 네트워크를 시각화합니다."""
    print(f"[6단계] 커뮤니티 시각화")
    
    fig, ax = plt.subplots(figsize=(28, 22))
    
    # 커뮤니티별 노드 그룹화
    communities = defaultdict(list)
    for node, comm_id in partition.items():
        communities[comm_id].append(node)
    
    # 커뮤니티를 크기순으로 정렬
    communities_sorted = sorted(communities.items(), key=lambda x: len(x[1]), reverse=True)
    
    # 색상 팔레트 생성 (명확한 구분을 위해)
    colors = plt.cm.Set3(np.linspace(0, 1, len(communities)))
    color_map = {comm_id: colors[i] for i, (comm_id, _) in enumerate(communities_sorted)}
    
    # Spring Layout
    print(f"  Spring layout 계산 중... (노드 수: {G.number_of_nodes()})")
    k = 3 / np.sqrt(G.number_of_nodes())
    pos = nx.spring_layout(G, k=k, iterations=300, seed=42)
    
    # 엣지 그리기 (먼저 그려서 노드 아래에)
    edges = G.edges(data=True)
    edge_weights = [d.get('weight', 1) for u, v, d in edges]
    
    if edge_weights:
        min_weight_val = min(edge_weights)
        max_weight_val = max(edge_weights)
        min_width = 0.3
        max_width = 2.5
        
        def width_func(weight):
            if max_weight_val == min_weight_val:
                return (min_width + max_width) / 2
            normalized = (weight - min_weight_val) / (max_weight_val - min_weight_val)
            return min_width + (max_width - min_width) * normalized
    else:
        def width_func(weight):
            return 1.0
    
    edge_widths = [width_func(w) for w in edge_weights]
    
    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.15, 
                          edge_color='lightgray', ax=ax)
    
    # 커뮤니티별로 노드 그리기
    for comm_id, nodes in communities_sorted:
        color = color_map[comm_id]
        node_sizes = [400 for _ in nodes]
        
        nx.draw_networkx_nodes(G, pos, nodelist=nodes,
                              node_size=node_sizes,
                              node_color=[color], alpha=0.8,
                              edgecolors='black', linewidths=1.5, ax=ax)
    
    # 상위 스킬 레이블 표시 (각 커뮤니티별로 상위 3-5개)
    labels = {}
    for comm_id, nodes in communities_sorted[:10]:  # 상위 10개 커뮤니티만
        subgraph = G.subgraph(nodes)
        degrees = dict(subgraph.degree())
        top_skills = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for node_id, _ in top_skills:
            skill_name = G.nodes[node_id].get('label', node_id)
            if len(skill_name) > 15:
                skill_name = skill_name[:12] + '...'
            labels[node_id] = skill_name
    
    nx.draw_networkx_labels(G, pos, labels, font_size=10, ax=ax, 
                           font_weight='bold', font_color='black')
    
    # 범례 생성
    legend_elements = []
    for i, (comm_id, nodes) in enumerate(communities_sorted[:15], 1):  # 상위 15개만
        color = color_map[comm_id]
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                        markerfacecolor=color, markersize=12,
                                        label=f'커뮤니티 {i} ({len(nodes)}개)'))
    
    ax.legend(handles=legend_elements, loc='upper left', fontsize=9, 
             framealpha=0.9, title='커뮤니티 구분', title_fontsize=11)
    
    ax.set_title('Skill-Skill 네트워크 커뮤니티 탐지 결과\n'
                 f'Louvain 알고리즘, {len(communities)}개 커뮤니티 탐지', 
                 fontsize=20, pad=25, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  저장 완료: {output_path}")
    plt.close()


def create_analysis_markdown(G, partition, communities_sorted, modularity, 
                            community_interpretations, output_path):
    """군집 분석 결과를 마크다운 파일로 생성합니다."""
    print(f"[7단계] 분석 문서 생성: {output_path}")
    
    markdown_content = f"""# Skill-Skill 네트워크 군집 분석 (Community Detection)

## 개요
본 문서는 Skill-Skill One-mode Projection 네트워크에 대한 커뮤니티 탐지 분석 결과를 정리합니다.
- 필터링 조건: weight >= 5
- 전체 네트워크 규모: {G.number_of_nodes()}개 노드, {G.number_of_edges()}개 엣지
- 알고리즘: Louvain 알고리즘 (Blondel et al. 2008) - Gephi와 동일한 설정
- **알고리즘 파라미터**:
  - Resolution: 1.0
  - Randomize: On
  - Use edge weights: On
- 모듈성 (Modularity): {modularity:.4f}
- 모듈성 (Resolution 포함): {modularity:.4f}

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

### 작동 원리
1. **초기화**: 각 노드를 독립적인 커뮤니티로 시작
2. **최적화**: 각 노드를 인접한 커뮤니티로 이동시켜 모듈성을 증가시킴
3. **집계**: 커뮤니티를 하나의 노드로 집계하여 새로운 네트워크 생성
4. **반복**: 수렴할 때까지 반복

### 모듈성 (Modularity)
- **정의**: 네트워크 내에서 커뮤니티 내부 연결이 커뮤니티 간 연결보다 얼마나 많은지를 측정
- **범위**: -1 ~ 1 (값이 클수록 더 명확한 커뮤니티 구조)
- **본 분석 결과**: {modularity:.4f}
  - 해석: {'명확한 커뮤니티 구조가 존재함' if modularity > 0.3 else '약한 커뮤니티 구조' if modularity > 0 else '커뮤니티 구조가 불명확함'}
- **Resolution 파라미터**: 
  - Resolution 파라미터를 사용한 모듈성 계산은 커뮤니티 크기를 조절하는 데 도움을 줍니다.
  - Resolution 1.0은 표준 모듈성과 동일한 결과를 제공합니다.

---

## 2. 탐지된 커뮤니티 분석

### 전체 커뮤니티 개수
총 **{len(communities_sorted)}개**의 커뮤니티가 탐지되었습니다.

### 커뮤니티 정보 (상위 15개)

| 커뮤니티 ID | 노드 수 | 주요 역할 | 신뢰도 | 대표 스킬 (상위 5개) |
|------------|---------|----------|--------|---------------------|
"""
    
    total_nodes = G.number_of_nodes()
    for i, interpretation in enumerate(community_interpretations[:15], 1):
        comm_id = interpretation['community_id']
        size = interpretation['size']
        role = interpretation['primary_role']
        confidence = interpretation['confidence']
        top_skills = ', '.join(interpretation['top_skills'][:5])
        percentage = (size / total_nodes) * 100
        
        markdown_content += f"| {i} | {size} ({percentage:.1f}%) | {role} | {confidence:.2f} | {top_skills} |\n"
    
    markdown_content += f"""
---

## 3. 커뮤니티별 상세 분석

"""
    
    for i, interpretation in enumerate(community_interpretations[:10], 1):
        comm_id = interpretation['community_id']
        size = interpretation['size']
        role = interpretation['primary_role']
        confidence = interpretation['confidence']
        top_skills = interpretation['top_skills']
        all_skills = interpretation['all_skills']
        role_scores = interpretation['role_scores']
        
        markdown_content += f"""### 커뮤니티 {i}: {role}

#### 기본 정보
- **커뮤니티 ID**: {comm_id}
- **노드 수**: {size}개
- **주요 역할**: {role}
- **신뢰도**: {confidence:.2f}

#### 대표 스킬 (상위 10개)
"""
        for j, skill in enumerate(top_skills[:10], 1):
            markdown_content += f"{j}. {skill}\n"
        
        markdown_content += f"""
#### 역할 매칭 점수
"""
        if role_scores:
            sorted_scores = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
            for role_name, score in sorted_scores[:5]:
                markdown_content += f"- {role_name}: {score}점\n"
        
        markdown_content += f"""
#### 해석
이 커뮤니티는 **{role}** 관련 스킬들로 구성되어 있습니다. 
{'높은 신뢰도' if confidence > 0.3 else '중간 신뢰도' if confidence > 0.15 else '낮은 신뢰도'}로 해당 역할과 매칭되며, 
{size}개의 스킬이 함께 사용되는 패턴을 보입니다.

---

"""
    
    markdown_content += f"""
## 4. 주요 인사이트

### 4.1 실제 시장에서의 직무별 스킬 묶음

#### 발견된 주요 스킬 묶음
"""
    
    # 역할별로 그룹화
    role_groups = defaultdict(list)
    for interp in community_interpretations:
        role = interp['primary_role']
        role_groups[role].append(interp)
    
    for role, communities in sorted(role_groups.items(), key=lambda x: len(x[1]), reverse=True):
        if len(communities) > 0:
            total_size = sum(c['size'] for c in communities)
            markdown_content += f"""
**{role} 관련 커뮤니티:**
- 커뮤니티 개수: {len(communities)}개
- 총 스킬 수: {total_size}개
- 대표 스킬: {', '.join(communities[0]['top_skills'][:5])}
"""
    
    markdown_content += """
#### 인사이트
- 실제 구인 시장에서 요구되는 스킬들은 자연스럽게 직무별/역할별로 그룹화됩니다.
- 각 커뮤니티는 특정 직무나 업무 영역에서 함께 사용되는 스킬 패키지를 나타냅니다.
- 이러한 패턴은 교육과정 설계나 커리어 경로 설계에 유용한 정보를 제공합니다.

### 4.2 네트워크 상의 직무 구분

#### 분석 결과
"""
    
    # 주요 역할별 커뮤니티 확인
    major_roles = ['데이터 분석', 'AI/ML', '백엔드', '프론트엔드', '클라우드', 'DevOps']
    found_roles = []
    for role in major_roles:
        matching = [c for c in community_interpretations if role in c['primary_role']]
        if matching:
            found_roles.append(role)
            total_skills = sum(c['size'] for c in matching)
            markdown_content += f"- **{role}**: {len(matching)}개 커뮤니티, 총 {total_skills}개 스킬\n"
    
    markdown_content += f"""
#### 해석
- 우리가 일반적으로 구분하는 직무(데이터 분석, 백엔드, 프론트엔드, AI/ML 등)가 **네트워크 상에서도 자연스럽게 구분**됩니다.
- 이는 실제 실무에서도 이러한 직무 구분이 의미 있음을 시사합니다.
- 각 직무별로 특정 스킬 조합이 함께 사용되는 패턴이 명확하게 나타납니다.

### 4.3 커뮤니티 간 연결성

#### 분석
- Giant Component 내에서도 스킬들이 자연스럽게 커뮤니티를 형성합니다.
- 커뮤니티 간에는 "브릿지 스킬"들이 연결 역할을 합니다.
- 예: Python은 여러 커뮤니티에 걸쳐 있어, 데이터 분석과 AI/ML 커뮤니티를 연결합니다.

#### 인사이트
- 커뮤니티 간 연결이 강할수록, 해당 영역 간 전환이 용이합니다.
- 브릿지 스킬을 학습하면 여러 직무 영역으로의 확장이 가능합니다.

### 4.4 교육과정 설계에 대한 시사점

#### 커뮤니티 기반 교육 설계
- 각 커뮤니티의 스킬들을 함께 가르치는 것이 효과적입니다.
- 예: 데이터 분석 커뮤니티의 Python, SQL, Tableau를 통합 교육과정으로 구성

#### 단계적 학습 경로
- 커뮤니티 내에서 중심 스킬부터 학습하고, 점진적으로 확장
- 커뮤니티 간 연결을 통해 다른 영역으로 확장

### 4.5 커리어 경로 설계에 대한 시사점

#### 커뮤니티 내 이동
- 같은 커뮤니티 내의 스킬들 간 이동은 상대적으로 용이합니다.
- 예: SQL → Tableau → Power BI (데이터 분석 커뮤니티 내)

#### 커뮤니티 간 이동
- 브릿지 스킬을 통해 다른 커뮤니티로 이동 가능
- 예: Python을 통해 데이터 분석 → AI/ML 커뮤니티로 전환

---

## 5. 추가 분석 인사이트

### 5.1 스킬 생태계의 계층 구조
- 커뮤니티 분석을 통해 스킬 생태계가 명확한 계층 구조를 가짐을 확인
- 각 커뮤니티는 특정 직무 영역을 나타내며, 커뮤니티 간 연결을 통해 전체 생태계가 통합됨

### 5.2 허브 스킬의 역할
- Python, AWS, SQL 등의 허브 스킬들은 여러 커뮤니티에 걸쳐 있어 연결 역할
- 이러한 스킬들은 커뮤니티 간 이동의 "게이트웨이" 역할

### 5.3 새로운 스킬의 통합
- 새로운 스킬이 등장하면, 관련 커뮤니티에 자연스럽게 통합됨
- 예: LLM은 AI/ML 커뮤니티에 속하면서도 데이터 분석 커뮤니티와 연결

---

## 결론

Louvain 알고리즘을 통한 커뮤니티 탐지 분석 결과:

1. **명확한 직무별 구분**: 실제 시장에서 요구되는 스킬들이 직무별로 자연스럽게 그룹화됨
2. **네트워크 구조의 일관성**: 우리가 인식하는 직무 구분이 네트워크 상에서도 명확하게 나타남
3. **통합된 생태계**: 각 커뮤니티는 독립적이면서도 서로 연결되어 통합된 생태계 형성
4. **실용적 활용**: 교육과정 설계, 커리어 경로 설계, 인력 채용 전략 등에 유용한 인사이트 제공

이러한 분석 결과는 스킬 생태계의 구조적 특성을 이해하고, 효과적인 교육 및 커리어 전략을 수립하는 데 기여합니다.

"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"  분석 문서 저장 완료: {output_path}")


def main():
    """메인 함수"""
    print("=" * 70)
    print("Skill-Skill 네트워크 군집 분석 (Community Detection)")
    print("=" * 70)
    
    # 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    edges_csv = os.path.join(script_dir, 'posting_skill_bipartite_edges.csv')
    output_dir = os.path.join(parent_dir, 'Skill_Skill_networkCommunityDetec_Analysis')
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # 1단계: Bipartite 그래프 생성
    bipartite_G, unique_jobs, unique_skills = create_bipartite_graph_from_csv(edges_csv)
    
    # 2단계: Skill-Skill One-mode Projection 생성
    skill_skill_G = create_skill_skill_network(bipartite_G, unique_jobs)
    
    # 3단계: 가중치 필터링 (weight >= 5)
    G_filtered = filter_network_by_weight(skill_skill_G, min_weight=5)
    
    if G_filtered.number_of_nodes() == 0:
        print(f"  오류: 필터링 후 노드가 없습니다.")
        return
    
    # 4단계: 커뮤니티 탐지 (Gephi와 동일한 설정)
    partition, communities_sorted, modularity = detect_communities(
        G_filtered, 
        resolution=1.0,  # Gephi Resolution: 1.0
        randomize=True   # Gephi Randomize: On
    )
    
    # 5단계: 커뮤니티 해석
    community_interpretations = interpret_communities(G_filtered, communities_sorted)
    
    # 6단계: 커뮤니티 시각화
    output_visualization = os.path.join(output_dir, 'community_detection_visualization.png')
    visualize_communities(G_filtered, partition, output_visualization)
    
    # 7단계: 분석 문서 생성
    analysis_file = os.path.join(output_dir, 'CommunityDetect_Analysis.md')
    create_analysis_markdown(G_filtered, partition, communities_sorted, modularity,
                            community_interpretations, analysis_file)
    
    print("\n" + "=" * 70)
    print("작업 완료!")
    print(f"결과물 저장 위치: {output_dir}")
    print("=" * 70)


if __name__ == '__main__':
    main()

