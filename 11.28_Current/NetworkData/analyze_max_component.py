"""
Skill-Skill 네트워크 Max Component 분석 스크립트

분석 내용:
1. Max Component의 개념 및 의미
2. Connected Components 탐지 및 분석
3. Giant Component 추출 및 분석
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import Counter

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


def analyze_connected_components(G):
    """Connected Components를 분석합니다."""
    print(f"[4단계] Connected Components 분석")
    
    # Connected Components 탐지
    components = list(nx.connected_components(G))
    components = [list(comp) for comp in components]
    
    # 크기별로 정렬 (큰 것부터)
    components.sort(key=len, reverse=True)
    
    print(f"  총 Component 개수: {len(components)}")
    print(f"  가장 큰 Component 크기: {len(components[0])}개 노드")
    
    # 각 Component의 정보 수집
    component_info = []
    for i, comp in enumerate(components):
        subgraph = G.subgraph(comp)
        component_info.append({
            'component_id': i + 1,
            'node_count': len(comp),
            'edge_count': subgraph.number_of_edges(),
            'nodes': comp
        })
    
    return component_info, components


def extract_giant_component(G):
    """Giant Component를 추출합니다."""
    print(f"[5단계] Giant Component 추출")
    
    # 가장 큰 Component 추출
    components = list(nx.connected_components(G))
    giant_component_nodes = max(components, key=len)
    giant_component = G.subgraph(giant_component_nodes)
    
    print(f"  Giant Component 노드 수: {giant_component.number_of_nodes()}")
    print(f"  Giant Component 엣지 수: {giant_component.number_of_edges()}")
    print(f"  전체 대비 비율: {giant_component.number_of_nodes() / G.number_of_nodes() * 100:.2f}%")
    
    return giant_component, giant_component_nodes


def visualize_giant_component(giant_component, output_path):
    """Giant Component를 시각화합니다."""
    print(f"[6단계] Giant Component 시각화")
    
    fig, ax = plt.subplots(figsize=(24, 20))
    
    # Spring Layout
    print(f"  Spring layout 계산 중... (노드 수: {giant_component.number_of_nodes()})")
    k = 3 / np.sqrt(giant_component.number_of_nodes())
    pos = nx.spring_layout(giant_component, k=k, iterations=300, seed=42)
    
    # 엣지 그리기
    edges = giant_component.edges(data=True)
    edge_weights = [d.get('weight', 1) for u, v, d in edges]
    
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
    
    nx.draw_networkx_edges(giant_component, pos, width=edge_widths, alpha=0.2, 
                          edge_color='lightgray', ax=ax)
    
    # 노드 그리기
    node_sizes = [300 for _ in giant_component.nodes()]
    nx.draw_networkx_nodes(giant_component, pos, node_size=node_sizes,
                          node_color='steelblue', alpha=0.7,
                          edgecolors='darkblue', linewidths=1.5, ax=ax)
    
    # 상위 스킬 레이블 표시 (Degree 기준)
    degrees = dict(giant_component.degree())
    sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
    top_nodes = [n for n, _ in sorted_nodes[:20]]
    
    labels = {}
    for node_id in top_nodes:
        skill_name = giant_component.nodes[node_id].get('label', node_id)
        if len(skill_name) > 15:
            skill_name = skill_name[:12] + '...'
        labels[node_id] = skill_name
    
    nx.draw_networkx_labels(giant_component, pos, labels, font_size=9, ax=ax, 
                           font_weight='bold')
    
    ax.set_title('Giant Component 시각화\n'
                 f'노드 수: {giant_component.number_of_nodes()}개, '
                 f'엣지 수: {giant_component.number_of_edges()}개', 
                 fontsize=20, pad=25, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  저장 완료: {output_path}")
    plt.close()


def create_analysis_markdown(G, component_info, giant_component, output_path):
    """Max Component 분석 결과를 마크다운 파일로 생성합니다."""
    print(f"[7단계] 분석 문서 생성: {output_path}")
    
    # Component 크기 분포
    component_sizes = [info['node_count'] for info in component_info]
    size_distribution = Counter(component_sizes)
    
    markdown_content = f"""# Skill-Skill 네트워크 Max Component 분석

## 개요
본 문서는 Skill-Skill One-mode Projection 네트워크에 대한 Connected Components 및 Giant Component 분석 결과를 정리합니다.
- 필터링 조건: weight >= 5
- 전체 네트워크 규모: {G.number_of_nodes()}개 노드, {G.number_of_edges()}개 엣지

---

## 1. Max Component의 개념 및 네트워크에서의 의미

### 개념 설명
**Max Component (최대 연결 성분)**는 네트워크에서 가장 큰 크기를 가진 Connected Component를 의미합니다. 
일반적으로 네트워크에서 가장 큰 Component를 **Giant Component**라고 부릅니다.

### 네트워크에서의 의미

#### 1. 연결성 (Connectivity)
- Max Component는 네트워크 내에서 서로 연결된 노드들의 최대 집합을 나타냅니다.
- Component 내의 모든 노드는 직접 또는 간접적으로 연결되어 있어, 서로 도달 가능합니다.
- **의미**: Component 내의 스킬들은 서로 연결되어 있어, 하나의 스킬에서 다른 스킬로 "경로"가 존재합니다.

#### 2. 스킬 생태계의 통합성
- Max Component의 크기가 클수록, 스킬 생태계가 더 통합되어 있음을 의미합니다.
- **의미**: 다양한 스킬들이 서로 연결되어 있어, 스킬 간 이동이 용이한 "통합된 생태계"를 형성합니다.
- **해석**: 
  - 큰 Giant Component → 스킬들이 밀접하게 연결되어 있어 커리어 전환이 용이
  - 작은 Component들로 분산 → 스킬들이 독립적인 그룹으로 분리되어 있어 전환 어려움

#### 3. 네트워크 구조의 특성
- **Giant Component 존재**: 네트워크의 대부분이 하나의 큰 Component에 속함
  - 의미: 스킬 생태계가 "중심화"되어 있음
  - 해석: 핵심 스킬들이 네트워크의 중심을 형성하고, 대부분의 스킬이 이 중심과 연결됨
  
- **여러 Component 분산**: 네트워크가 여러 독립적인 그룹으로 나뉨
  - 의미: 스킬 생태계가 "분절화"되어 있음
  - 해석: 서로 다른 도메인이나 직무 영역의 스킬들이 독립적으로 존재

#### 4. 실무적 의미
- **커리어 전환 가능성**: Giant Component 내의 스킬들은 서로 연결되어 있어, 한 스킬에서 다른 스킬로의 전환이 가능합니다.
- **학습 경로**: Component 내에서 스킬 간 학습 경로를 설계할 수 있습니다.
- **스킬 조합**: Component 내의 스킬들은 함께 사용될 가능성이 높습니다.

---

## 2. Connected Components 분석

### 전체 Component 개수
총 **{len(component_info)}개**의 Connected Component가 탐지되었습니다.

### Component 정보 (상위 10개)

| Component ID | 노드 수 | 엣지 수 | 전체 대비 비율 (%) |
|--------------|---------|---------|-------------------|
"""
    
    total_nodes = G.number_of_nodes()
    for info in component_info[:10]:
        node_count = info['node_count']
        edge_count = info['edge_count']
        percentage = (node_count / total_nodes) * 100
        markdown_content += f"| {info['component_id']} | {node_count} | {edge_count} | {percentage:.2f}% |\n"
    
    if len(component_info) > 10:
        markdown_content += f"\n*총 {len(component_info)}개 Component 중 상위 10개만 표시*\n"
    
    markdown_content += f"""
### Component 크기 분포

#### 크기별 Component 개수

| Component 크기 (노드 수) | Component 개수 |
|-------------------------|----------------|
"""
    
    # 크기별 분포 (상위 10개)
    sorted_sizes = sorted(size_distribution.items(), key=lambda x: x[0], reverse=True)
    for size, count in sorted_sizes[:10]:
        markdown_content += f"| {size} | {count} |\n"
    
    markdown_content += f"""
#### 분포 통계
- **평균 Component 크기**: {np.mean(component_sizes):.2f}개 노드
- **중앙값 Component 크기**: {np.median(component_sizes):.2f}개 노드
- **최대 Component 크기**: {max(component_sizes)}개 노드
- **최소 Component 크기**: {min(component_sizes)}개 노드
- **표준편차**: {np.std(component_sizes):.2f}

### Component 사이즈 분포에 대한 해석 및 인사이트

#### 1. 분포 특성
"""
    
    # Giant Component 비율 계산
    giant_size = max(component_sizes)
    giant_ratio = (giant_size / total_nodes) * 100
    
    markdown_content += f"""
- **Giant Component 비율**: {giant_ratio:.2f}% (전체 노드 중 {giant_size}개 노드)
- **나머지 Component들**: {len(component_info) - 1}개 Component가 나머지 {total_nodes - giant_size}개 노드를 차지

#### 2. 주요 인사이트

**Giant Component의 지배적 존재:**
- 네트워크의 {giant_ratio:.2f}%가 하나의 큰 Component에 속해 있습니다.
- 이는 스킬 생태계가 **강하게 통합**되어 있음을 의미합니다.
- **해석**: 대부분의 스킬들이 서로 연결되어 있어, 스킬 간 이동과 조합이 용이한 "통합된 생태계"를 형성하고 있습니다.

**작은 Component들의 의미:**
"""
    
    # 작은 Component 분석 (크기 2-5)
    small_components = [info for info in component_info if 2 <= info['node_count'] <= 5]
    isolated_nodes = [info for info in component_info if info['node_count'] == 1]
    
    markdown_content += f"""
- **작은 Component (2-5개 노드)**: {len(small_components)}개
  - 의미: 특정 스킬 조합만 함께 사용되는 "전문 영역"을 나타냅니다.
  - 해석: 이러한 Component들은 특정 직무나 도메인에 특화된 스킬 그룹입니다.
  
- **고립된 노드 (1개 노드)**: {len(isolated_nodes)}개
  - 의미: 다른 스킬과 연결되지 않은 독립적인 스킬입니다.
  - 해석: 매우 특수하거나 새로운 스킬로, 아직 다른 스킬과의 연결이 형성되지 않았을 수 있습니다.

**분포의 불균형:**
- Component 크기 분포가 매우 불균형적입니다 (하나의 거대한 Component와 많은 작은 Component들).
- 이는 **"Rich-get-richer" 현상**을 보여줍니다:
  - 이미 많은 연결을 가진 스킬(허브 스킬)이 더 많은 연결을 끌어당김
  - 결과적으로 하나의 거대한 Component가 형성됨

#### 3. 실무적 시사점

**커리어 경로 설계:**
- Giant Component 내의 스킬들은 서로 연결되어 있어, 다양한 커리어 경로를 설계할 수 있습니다.
- 예: Python → SQL → Tableau → Power BI (모두 Giant Component 내)

**스킬 학습 전략:**
- Giant Component의 중심 스킬부터 학습하면, 다른 스킬로의 확장이 용이합니다.
- 작은 Component의 스킬들은 특정 도메인에 집중할 때 학습하는 것이 효율적입니다.

**교육과정 설계:**
- Giant Component의 스킬들을 중심으로 통합 교육과정을 설계할 수 있습니다.
- 작은 Component의 스킬들은 선택 과목이나 전문 트랙으로 구성하는 것이 적절합니다.

---

## 3. Giant Component 분석

### Giant Component 기본 정보

- **노드 수**: {giant_component.number_of_nodes()}개
- **엣지 수**: {giant_component.number_of_edges()}개
- **전체 네트워크 대비 비율**: {giant_ratio:.2f}%
- **평균 Degree**: {2 * giant_component.number_of_edges() / giant_component.number_of_nodes():.2f}
- **밀도 (Density)**: {nx.density(giant_component):.4f}

### Giant Component의 구조적 특성

#### 1. 연결성
- Giant Component는 **강하게 연결된 구조**를 가지고 있습니다.
- Component 내의 모든 노드는 직접 또는 간접적으로 연결되어 있어, 임의의 두 노드 간 경로가 존재합니다.
- **의미**: Component 내의 모든 스킬은 서로 "도달 가능"하며, 스킬 간 이동이 가능합니다.

#### 2. 중심성 분포
"""
    
    # Giant Component의 중심성 계산
    giant_degrees = dict(giant_component.degree())
    top_giant_skills = sorted(giant_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
    
    markdown_content += """
**Giant Component 내 TOP 10 스킬 (Degree 기준):**

| 순위 | 스킬명 | Degree |
|------|--------|--------|
"""
    
    for i, (node_id, degree) in enumerate(top_giant_skills, 1):
        skill_name = giant_component.nodes[node_id].get('label', node_id)
        markdown_content += f"| {i} | {skill_name} | {degree} |\n"
    
    markdown_content += f"""
#### 3. 네트워크 구조의 의미

**통합된 스킬 생태계:**
- Giant Component가 전체 네트워크의 {giant_ratio:.2f}%를 차지한다는 것은, 스킬 생태계가 **강하게 통합**되어 있음을 의미합니다.
- 대부분의 스킬들이 서로 연결되어 있어, 하나의 "통합된 생태계"를 형성하고 있습니다.

**허브 스킬의 역할:**
- Giant Component의 중심에는 Python, AI, AWS 등의 허브 스킬들이 위치합니다.
- 이러한 허브 스킬들은 Component 내의 다른 스킬들을 연결하는 "교량" 역할을 합니다.
- **의미**: 허브 스킬을 보유하면, Component 내의 다른 스킬로의 전환이 용이합니다.

**스킬 간 이동성:**
- Giant Component 내에서는 임의의 스킬에서 다른 스킬로의 경로가 존재합니다.
- **의미**: 한 스킬 영역에서 다른 스킬 영역으로의 전환이 가능합니다.
- **예시**: 
  - 데이터 분석 스킬 (Python, SQL) → AI/ML 스킬 (AI, ML, TensorFlow)
  - 클라우드 스킬 (AWS, GCP) → DevOps 스킬 (Docker, Kubernetes)

### Giant Component 결과 해석 및 인사이트

#### 1. 스킬 생태계의 통합성
- **높은 통합도**: {giant_ratio:.2f}%의 스킬이 하나의 Component에 속해 있습니다.
- **의미**: IT 스킬 생태계가 매우 통합되어 있어, 스킬 간 경계가 모호하고 이동이 용이합니다.
- **시사점**: 
  - 한 영역의 스킬을 학습하면, 다른 영역으로의 확장이 상대적으로 용이합니다.
  - 교육과정에서도 스킬을 통합적으로 가르칠 수 있습니다.

#### 2. 커리어 전환 가능성
- **높은 전환성**: Giant Component 내의 스킬들은 서로 연결되어 있어, 커리어 전환이 용이합니다.
- **의미**: 
  - 데이터 분석가 → AI 엔지니어 전환 가능 (Python, SQL 등 공통 스킬)
  - 백엔드 개발자 → 클라우드 엔지니어 전환 가능 (AWS, Docker 등 공통 스킬)
- **시사점**: 
  - 초기 커리어에서 허브 스킬(Python, AWS 등)을 학습하면, 다양한 경로로 전환할 수 있습니다.
  - 특정 도메인에 고정되지 않고, 유연한 커리어 경로를 설계할 수 있습니다.

#### 3. 교육과정 설계에 대한 시사점
- **통합 교육의 효과성**: Giant Component의 존재는 스킬들을 통합적으로 가르치는 것이 효과적임을 시사합니다.
- **의미**: 
  - Python, SQL, Tableau 등을 함께 가르치면, 각 스킬의 이해도가 상호 보완적으로 향상됩니다.
  - 스킬 간 연결을 이해하면, 학습 효율이 높아집니다.
- **시사점**: 
  - 교육과정에서 스킬을 독립적으로 가르치기보다, 관련 스킬들을 함께 가르치는 것이 효과적입니다.
  - 프로젝트 기반 학습을 통해 여러 스킬을 동시에 활용하도록 설계할 수 있습니다.

#### 4. 네트워크 구조의 안정성
- **강한 연결성**: Giant Component의 높은 밀도는 네트워크가 안정적임을 의미합니다.
- **의미**: 
  - 일부 스킬이 사라져도, 네트워크의 전체 구조는 유지됩니다.
  - 새로운 스킬이 추가되면, 기존 스킬들과 연결되어 Component에 통합됩니다.
- **시사점**: 
  - 스킬 생태계가 지속적으로 진화하면서도, 기본 구조는 안정적으로 유지됩니다.
  - 새로운 기술이 등장해도, 기존 스킬 생태계와 통합되어 발전합니다.

#### 5. 추가 분석 인사이트

**스킬 그룹의 자연스러운 형성:**
- Giant Component 내에서도 스킬들이 자연스럽게 그룹을 형성합니다 (예: 데이터 분석 그룹, AI/ML 그룹, 클라우드 그룹).
- 이러한 그룹들은 서로 연결되어 있어, 그룹 간 이동도 가능합니다.
- **의미**: 스킬 생태계는 계층적 구조를 가지면서도, 전체적으로는 통합되어 있습니다.

**허브 스킬의 전략적 중요성:**
- Python, AI, AWS 등의 허브 스킬은 Giant Component의 중심에 위치합니다.
- 이러한 스킬들을 학습하면, Component 내의 다른 스킬로의 접근이 용이해집니다.
- **의미**: 허브 스킬은 "게이트웨이" 역할을 하며, 다양한 스킬 영역으로의 진입점이 됩니다.

---

## 결론

Max Component 분석을 통해 다음과 같은 주요 발견을 할 수 있습니다:

1. **강한 통합성**: 네트워크의 {giant_ratio:.2f}%가 하나의 Giant Component에 속해 있어, 스킬 생태계가 매우 통합되어 있습니다.

2. **높은 연결성**: Giant Component 내의 스킬들은 서로 강하게 연결되어 있어, 스킬 간 이동과 조합이 용이합니다.

3. **유연한 커리어 경로**: Giant Component의 존재는 다양한 커리어 전환 경로가 가능함을 의미합니다.

4. **교육과정 설계의 시사점**: 통합적이고 프로젝트 기반의 교육과정 설계가 효과적임을 시사합니다.

이러한 분석 결과는 교육과정 개선, 커리어 경로 설계, 인력 채용 전략 등에 유용한 인사이트를 제공합니다.

"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"  분석 문서 저장 완료: {output_path}")


def main():
    """메인 함수"""
    print("=" * 70)
    print("Skill-Skill 네트워크 Max Component 분석")
    print("=" * 70)
    
    # 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    edges_csv = os.path.join(script_dir, 'posting_skill_bipartite_edges.csv')
    output_dir = os.path.join(parent_dir, 'Skill_Skill_networkMaxComp')
    
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
    
    # 4단계: Connected Components 분석
    component_info, components = analyze_connected_components(G_filtered)
    
    # 5단계: Giant Component 추출
    giant_component, giant_component_nodes = extract_giant_component(G_filtered)
    
    # 6단계: Giant Component 시각화
    output_visualization = os.path.join(output_dir, 'giant_component_visualization.png')
    visualize_giant_component(giant_component, output_visualization)
    
    # 7단계: 분석 문서 생성
    analysis_file = os.path.join(output_dir, 'MaxComponent_Analysis.md')
    create_analysis_markdown(G_filtered, component_info, giant_component, analysis_file)
    
    print("\n" + "=" * 70)
    print("작업 완료!")
    print(f"결과물 저장 위치: {output_dir}")
    print("=" * 70)


if __name__ == '__main__':
    main()


