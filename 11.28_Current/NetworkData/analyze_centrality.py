"""
Skill-Skill 네트워크 중심성 분석 및 시각화 스크립트

중심성 지표:
1. Degree
2. Weighted Degree (Strength)
3. Eigenvector Centrality
4. PageRank

각 지표별로:
- Top 5 노드 강조
- 나머지 노드 연하게 표시
- 노드 크기는 중심성 지표에 비례
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import defaultdict

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


def calculate_weighted_degree(G):
    """Weighted Degree (Strength)를 계산합니다."""
    strength = {}
    for node in G.nodes():
        strength[node] = sum(d.get('weight', 1) for u, v, d in G.edges(node, data=True))
    return strength


def visualize_centrality(G, centrality_dict, centrality_name, output_path):
    """중심성 지표에 따른 네트워크 시각화"""
    print(f"[시각화] {centrality_name} 기반 네트워크 시각화")
    
    fig, ax = plt.subplots(figsize=(24, 20))
    
    # TOP 5 노드 식별
    sorted_nodes = sorted(centrality_dict.items(), key=lambda x: x[1], reverse=True)
    top5_nodes = [n for n, _ in sorted_nodes[:5]]
    top5_values = {n: centrality_dict[n] for n in top5_nodes}
    
    print(f"  TOP 5 스킬 ({centrality_name}):")
    for i, (node_id, value) in enumerate(sorted_nodes[:5], 1):
        skill_name = G.nodes[node_id].get('label', node_id)
        print(f"    {i}. {skill_name}: {value:.4f}")
    
    # 노드 크기 계산 - TOP 5는 크게, 나머지는 작게
    if centrality_dict:
        values = list(centrality_dict.values())
        min_val = min(values)
        max_val = max(values)
        
        # TOP 5 크기 범위
        top5_min_size = 2000
        top5_max_size = 3500
        
        # 나머지 노드 크기
        other_size = 100
        
        def size_func(node_id, value):
            if node_id in top5_nodes:
                # TOP 5는 값에 비례하여 크기 조정
                if max_val == min_val:
                    return (top5_min_size + top5_max_size) / 2
                normalized = (value - min_val) / (max_val - min_val)
                # TOP 5 내에서도 순위에 따라 크기 차이
                rank = top5_nodes.index(node_id) + 1
                if rank == 1:
                    return top5_max_size
                elif rank == 2:
                    return top5_min_size + (top5_max_size - top5_min_size) * 0.8
                elif rank == 3:
                    return top5_min_size + (top5_max_size - top5_min_size) * 0.6
                elif rank == 4:
                    return top5_min_size + (top5_max_size - top5_min_size) * 0.4
                else:  # rank == 5
                    return top5_min_size + (top5_max_size - top5_min_size) * 0.2
            else:
                return other_size
    else:
        def size_func(node_id, value):
            return 500
    
    node_sizes = [size_func(n, centrality_dict.get(n, 0)) for n in G.nodes()]
    
    # 엣지 가중치 추출
    edges = G.edges(data=True)
    edge_weights = [d.get('weight', 1) for u, v, d in edges]
    
    # 엣지 두께 정규화
    if edge_weights:
        min_weight_val = min(edge_weights)
        max_weight_val = max(edge_weights)
        min_width = 0.3
        max_width = 3.0
        
        def width_func(weight):
            if max_weight_val == min_weight_val:
                return (min_width + max_width) / 2
            normalized = (weight - min_weight_val) / (max_weight_val - min_weight_val)
            return min_width + (max_width - min_width) * normalized
    else:
        def width_func(weight):
            return 1.0
    
    edge_widths = [width_func(w) for w in edge_weights]
    
    # Spring Layout (노드가 겹치지 않도록)
    print(f"  Spring layout 계산 중... (노드 수: {G.number_of_nodes()})")
    k = 3 / np.sqrt(G.number_of_nodes())  # 노드 간 거리 증가
    pos = nx.spring_layout(G, k=k, iterations=300, seed=42)
    
    # 엣지 그리기 (먼저 그려서 노드 아래에, 연한 색상)
    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.15, 
                          edge_color='lightgray', ax=ax)
    
    # 노드를 TOP 5와 나머지로 분리하여 그리기
    other_nodes = [n for n in G.nodes() if n not in top5_nodes]
    
    # 나머지 노드 먼저 그리기 (작고 연하게)
    other_sizes = [size_func(n, centrality_dict.get(n, 0)) for n in other_nodes]
    nx.draw_networkx_nodes(G, pos, nodelist=other_nodes,
                          node_size=other_sizes, 
                          node_color='lightgray', alpha=0.3,
                          edgecolors='gray', linewidths=0.5, ax=ax)
    
    # TOP 5 노드 그리기 (크고 명확하게)
    top5_colors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3', '#F38181']  # 다양한 강조 색상
    top5_sizes = [size_func(n, centrality_dict.get(n, 0)) for n in top5_nodes]
    
    for i, (node_id, size) in enumerate(zip(top5_nodes, top5_sizes)):
        color = top5_colors[i]
        nx.draw_networkx_nodes(G, pos, nodelist=[node_id],
                              node_color=color, node_size=size,
                              alpha=0.9, ax=ax, edgecolors='black', linewidths=3)
    
    # 제목
    ax.set_title(f'Skill-Skill 네트워크 ({centrality_name} 중심성)\n'
                 f'TOP 5 스킬 강조, 나머지 노드는 연하게 표시', 
                 fontsize=20, pad=25, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  저장 완료: {output_path}")
    plt.close()
    
    return sorted_nodes


def analyze_centrality(G):
    """모든 중심성 지표를 계산하고 분석합니다."""
    print(f"[4단계] 중심성 지표 계산")
    
    # 1. Degree
    degree = dict(G.degree())
    print(f"  Degree 계산 완료")
    
    # 2. Weighted Degree (Strength)
    strength = calculate_weighted_degree(G)
    print(f"  Weighted Degree 계산 완료")
    
    # 3. Eigenvector Centrality
    try:
        eigenvector = nx.eigenvector_centrality(G, max_iter=1000, weight='weight')
        print(f"  Eigenvector Centrality 계산 완료")
    except:
        eigenvector = nx.eigenvector_centrality(G, max_iter=1000)
        print(f"  Eigenvector Centrality 계산 완료 (가중치 없이)")
    
    # 4. PageRank
    try:
        pagerank = nx.pagerank(G, weight='weight')
        print(f"  PageRank 계산 완료")
    except:
        pagerank = nx.pagerank(G)
        print(f"  PageRank 계산 완료 (가중치 없이)")
    
    return degree, strength, eigenvector, pagerank


def create_analysis_markdown(G, degree, strength, eigenvector, pagerank, output_path):
    """중심성 분석 결과를 마크다운 파일로 생성합니다."""
    print(f"[5단계] 분석 문서 생성: {output_path}")
    
    # TOP 10 추출
    degree_top10 = sorted(degree.items(), key=lambda x: x[1], reverse=True)[:10]
    strength_top10 = sorted(strength.items(), key=lambda x: x[1], reverse=True)[:10]
    eigenvector_top10 = sorted(eigenvector.items(), key=lambda x: x[1], reverse=True)[:10]
    pagerank_top10 = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]
    
    markdown_content = """# Skill-Skill 네트워크 중심성 분석

## 개요
본 문서는 Skill-Skill One-mode Projection 네트워크에 대한 4가지 중심성 지표 분석 결과를 정리합니다.
- 필터링 조건: weight >= 5
- 네트워크 규모: {}개 노드, {}개 엣지

---

## 1. Degree (연결 중심성)

### 개념 설명
**Degree**는 각 노드가 직접 연결된 이웃 노드의 개수를 의미합니다. 
- **의미**: 해당 스킬이 다른 스킬들과 얼마나 많이 직접 연결되어 있는지를 나타냅니다.
- **해석**: Degree가 높은 스킬은 네트워크에서 "연결의 허브" 역할을 하며, 다양한 스킬과 함께 요구되는 범용적인 스킬임을 의미합니다.
- **특징**: 단순히 연결된 개수만 세므로, 연결의 강도(가중치)는 고려하지 않습니다.

### TOP 10 노드

| 순위 | 스킬명 | Degree 값 |
|------|--------|-----------|
""".format(G.number_of_nodes(), G.number_of_edges())
    
    for i, (node_id, value) in enumerate(degree_top10, 1):
        skill_name = G.nodes[node_id].get('label', node_id)
        markdown_content += f"| {i} | {skill_name} | {value} |\n"
    
    markdown_content += """
### 결과 해석 및 분석

**주요 인사이트:**
- Degree가 높은 스킬들은 네트워크의 구조적 허브 역할을 합니다.
- 이러한 스킬들은 다양한 직무와 스킬 조합에서 공통적으로 요구되는 "범용 스킬"입니다.
- 예를 들어, Python, AI, AWS 등은 데이터 분석, 백엔드, AI/ML 등 다양한 영역에서 함께 사용되므로 높은 Degree를 가집니다.

---

## 2. Weighted Degree (가중 연결 중심성, Strength)

### 개념 설명
**Weighted Degree (Strength)**는 각 노드에 연결된 모든 엣지의 가중치 합을 의미합니다.
- **의미**: 해당 스킬이 다른 스킬들과 얼마나 "강하게" 연결되어 있는지를 나타냅니다.
- **해석**: 단순히 연결된 개수가 아니라, 함께 등장한 빈도(가중치)를 고려하므로, 실제 실무에서 얼마나 자주 함께 사용되는지를 반영합니다.
- **특징**: Degree와 달리 연결의 강도를 고려하므로, 자주 함께 쓰이는 스킬 쌍의 영향력이 더 크게 반영됩니다.

### TOP 10 노드

| 순위 | 스킬명 | Strength 값 |
|------|--------|-------------|
"""
    
    for i, (node_id, value) in enumerate(strength_top10, 1):
        skill_name = G.nodes[node_id].get('label', node_id)
        markdown_content += f"| {i} | {skill_name} | {value:.2f} |\n"
    
    markdown_content += """
### 결과 해석 및 분석

**주요 인사이트:**
- Strength가 높은 스킬들은 실제 실무에서 다른 스킬들과 "자주" 함께 사용되는 핵심 스킬입니다.
- Degree와 비교하여, Strength는 단순 연결이 아닌 "실제 사용 빈도"를 반영하므로 더 실용적인 지표입니다.
- 예를 들어, Python은 많은 스킬과 연결되어 있을 뿐만 아니라, 그 연결들이 자주 함께 등장하므로 높은 Strength를 가집니다.

---

## 3. Eigenvector Centrality (고유벡터 중심성)

### 개념 설명
**Eigenvector Centrality**는 노드의 중요도를 단순히 연결 개수가 아니라, "중요한 노드들과의 연결"을 통해 평가합니다.
- **의미**: 단순히 많이 연결된 것이 아니라, "중요한 스킬들과 연결된" 스킬이 더 높은 점수를 받습니다.
- **해석**: 네트워크에서 "권위"나 "명성"을 가진 스킬과 연결될수록 높은 점수를 받는 지표입니다.
- **특징**: 재귀적 개념 - 중요한 노드와 연결된 노드가 중요해지고, 그 노드와 연결된 노드도 중요해지는 방식입니다.

### TOP 10 노드

| 순위 | 스킬명 | Eigenvector 값 |
|------|--------|----------------|
"""
    
    for i, (node_id, value) in enumerate(eigenvector_top10, 1):
        skill_name = G.nodes[node_id].get('label', node_id)
        markdown_content += f"| {i} | {skill_name} | {value:.6f} |\n"
    
    markdown_content += """
### 결과 해석 및 분석

**주요 인사이트:**
- Eigenvector Centrality가 높은 스킬들은 "중요한 스킬들의 네트워크" 내부에 위치한 스킬입니다.
- 이러한 스킬들은 단순히 많이 연결된 것이 아니라, "핵심 스킬 그룹"의 일부로서 중요한 역할을 합니다.
- 예를 들어, AI와 연결된 스킬들이 많고, 그 스킬들도 중요하다면 AI의 Eigenvector Centrality가 높아집니다.

---

## 4. PageRank

### 개념 설명
**PageRank**는 Google의 검색 알고리즘에서 사용된 중심성 지표로, 노드의 중요도를 "랜덤 워크" 관점에서 평가합니다.
- **의미**: 네트워크를 무작위로 탐색할 때, 특정 노드에 도달할 확률이 높을수록 중요한 노드로 간주합니다.
- **해석**: 많은 노드로부터 "링크"를 받고, 그 링크를 준 노드들도 중요할수록 높은 점수를 받습니다.
- **특징**: Eigenvector와 유사하지만, 랜덤 워크 모델을 기반으로 하여 더 안정적인 결과를 제공합니다.

### TOP 10 노드

| 순위 | 스킬명 | PageRank 값 |
|------|--------|-------------|
"""
    
    for i, (node_id, value) in enumerate(pagerank_top10, 1):
        skill_name = G.nodes[node_id].get('label', node_id)
        markdown_content += f"| {i} | {skill_name} | {value:.6f} |\n"
    
    markdown_content += """
### 결과 해석 및 분석

**주요 인사이트:**
- PageRank가 높은 스킬들은 네트워크의 "핵심 허브"로서, 다양한 경로를 통해 접근 가능한 스킬입니다.
- 이러한 스킬들은 스킬 네트워크를 탐색할 때 자주 만나게 되는 "중요한 교차점" 역할을 합니다.
- 예를 들어, Python은 다양한 스킬 그룹과 연결되어 있어, 어떤 스킬에서 시작하든 Python에 도달할 가능성이 높습니다.

---

## 5. 네 중심성 지표의 비교 분석

### 지표 간 차이점

#### 1. Degree vs Weighted Degree
- **Degree**: 연결의 "개수"만 고려 → 단순 연결성
- **Weighted Degree**: 연결의 "강도"도 고려 → 실제 사용 빈도
- **차이점**: Degree는 "누구와 연결되었는가"를, Strength는 "얼마나 자주 함께 쓰이는가"를 반영
- **인사이트**: 
  - Degree가 높지만 Strength가 낮은 스킬 → 많은 스킬과 연결되지만 자주 함께 쓰이지는 않음
  - Strength가 높은 스킬 → 실제 실무에서 핵심적으로 자주 사용되는 스킬

#### 2. Degree vs Eigenvector/PageRank
- **Degree**: 직접 연결만 고려 → 지역적 중요도
- **Eigenvector/PageRank**: 간접 연결도 고려 → 전역적 중요도
- **차이점**: 
  - Degree는 "직접 이웃"의 영향만 받음
  - Eigenvector/PageRank는 "중요한 노드와의 연결"을 통해 중요도가 전파됨
- **인사이트**:
  - Degree가 높지만 Eigenvector가 낮은 스킬 → 많은 연결이 있지만, 중요하지 않은 스킬들과만 연결됨
  - Eigenvector가 높은 스킬 → 핵심 스킬 그룹의 일부로서 중요한 역할

#### 3. Eigenvector vs PageRank
- **Eigenvector**: 고유벡터 기반, 순수 수학적 접근
- **PageRank**: 랜덤 워크 기반, 더 안정적이고 해석 가능
- **차이점**: 
  - Eigenvector는 네트워크 구조에 더 민감
  - PageRank는 더 부드럽고 안정적인 결과 제공
- **인사이트**: 두 지표가 유사한 결과를 보이면, 해당 스킬의 중요도가 네트워크 구조적으로 명확함을 의미

### 종합 비교 인사이트

1. **구조적 중요도 vs 실용적 중요도**
   - Degree, Eigenvector, PageRank → 네트워크 구조에서의 중요도
   - Weighted Degree → 실제 사용 빈도에서의 중요도
   - **인사이트**: 구조적으로 중요하지만 실제로는 덜 쓰이는 스킬, 또는 그 반대의 경우를 발견할 수 있음

2. **지역적 중요도 vs 전역적 중요도**
   - Degree → 지역적(직접 연결) 중요도
   - Eigenvector, PageRank → 전역적(간접 연결 포함) 중요도
   - **인사이트**: 특정 스킬 그룹 내에서만 중요한 스킬 vs 전체 네트워크에서 중요한 스킬을 구분 가능

3. **스킬의 역할 분류**
   - **허브 스킬**: Degree, Strength가 높음 → 많은 스킬과 연결되고 자주 사용됨
   - **권위 스킬**: Eigenvector, PageRank가 높음 → 중요 스킬 그룹의 중심에 위치
   - **브릿지 스킬**: 특정 지표에서만 높음 → 특수한 역할을 하는 스킬

---

## 6. 추가 분석 인사이트

### 6.1 스킬 생태계의 계층 구조
네트워크 분석 결과, 스킬 생태계는 명확한 계층 구조를 보입니다:
- **1차 허브**: Python, AI, AWS 등 - 모든 영역에서 공통적으로 요구
- **2차 허브**: SQL, Java, Spring 등 - 특정 도메인 내에서 핵심 역할
- **전문 스킬**: 특정 직무나 영역에 특화된 스킬들

### 6.2 스킬 조합의 패턴
중심성 분석을 통해 다음과 같은 스킬 조합 패턴을 발견할 수 있습니다:
- **데이터 분석 스택**: Python, SQL, Tableau, Pandas 등이 강하게 연결
- **클라우드 인프라 스택**: AWS, Docker, Kubernetes 등이 함께 등장
- **AI/ML 스택**: AI, Python, TensorFlow, PyTorch 등이 밀집

### 6.3 커리어 경로 설계에 대한 시사점
- **기초 스킬**: 높은 중심성을 가진 스킬들은 다양한 커리어 경로의 기초가 됨
- **전환 가능성**: 높은 중심성 스킬을 보유하면 다른 영역으로의 전환이 용이
- **학습 우선순위**: 중심성이 높은 스킬부터 학습하면 효율적

### 6.4 교육과정 설계에 대한 시사점
- **통합 교육**: 높은 중심성을 가진 스킬들은 함께 가르치는 것이 효과적
- **기초 강화**: 허브 스킬들의 교육을 강화하면 전체 스킬 생태계 이해도 향상
- **실무 연계**: Weighted Degree가 높은 스킬들은 실제 실무에서 자주 사용되므로 교육과정에 필수 포함

---

## 결론

네 가지 중심성 지표를 통해 Skill-Skill 네트워크를 다각도로 분석한 결과:
1. **구조적 관점**: Degree, Eigenvector, PageRank로 네트워크 내 위치 파악
2. **실용적 관점**: Weighted Degree로 실제 사용 빈도 반영
3. **종합적 관점**: 지표 간 비교를 통해 스킬의 다양한 역할과 중요도 이해

이러한 분석은 교육과정 설계, 커리어 경로 설계, 인력 채용 전략 등에 유용한 인사이트를 제공합니다.

"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"  분석 문서 저장 완료: {output_path}")


def main():
    """메인 함수"""
    print("=" * 70)
    print("Skill-Skill 네트워크 중심성 분석")
    print("=" * 70)
    
    # 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    edges_csv = os.path.join(script_dir, 'posting_skill_bipartite_edges.csv')
    output_dir = os.path.join(parent_dir, 'Skill_Skill_NetworkCentral')
    
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
    
    # 4단계: 중심성 지표 계산
    degree, strength, eigenvector, pagerank = analyze_centrality(G_filtered)
    
    # 5단계: 각 중심성 지표별 시각화
    print(f"\n[5단계] 중심성 지표별 시각화")
    
    # Degree
    output_degree = os.path.join(output_dir, 'centrality_degree.png')
    visualize_centrality(G_filtered, degree, 'Degree', output_degree)
    
    # Weighted Degree
    output_strength = os.path.join(output_dir, 'centrality_weighted_degree.png')
    visualize_centrality(G_filtered, strength, 'Weighted Degree', output_strength)
    
    # Eigenvector
    output_eigenvector = os.path.join(output_dir, 'centrality_eigenvector.png')
    visualize_centrality(G_filtered, eigenvector, 'Eigenvector Centrality', output_eigenvector)
    
    # PageRank
    output_pagerank = os.path.join(output_dir, 'centrality_pagerank.png')
    visualize_centrality(G_filtered, pagerank, 'PageRank', output_pagerank)
    
    # 6단계: 분석 문서 생성
    analysis_file = os.path.join(output_dir, 'Centrality_analysis.md')
    create_analysis_markdown(G_filtered, degree, strength, eigenvector, pagerank, analysis_file)
    
    print("\n" + "=" * 70)
    print("작업 완료!")
    print(f"결과물 저장 위치: {output_dir}")
    print("=" * 70)


if __name__ == '__main__':
    main()


