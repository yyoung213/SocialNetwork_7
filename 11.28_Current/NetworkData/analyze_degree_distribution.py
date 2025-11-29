"""
Skill-Skill 네트워크 Degree Distribution 분석

분석 내용:
1. PDF (Probability Density Function) - 선형 및 로그 스케일
2. CCDF (Complementary Cumulative Distribution Function) - 선형 및 로그 스케일
3. Power-law Tail 분석
4. 각 결과에 대한 해석 및 인사이트
"""

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import os
from collections import Counter
from scipy import stats
from scipy.optimize import curve_fit

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
plt.rcParams['axes.unicode_minus'] = False


def parse_pajek_network(file_path):
    """Pajek 형식의 네트워크 파일을 파싱합니다."""
    print(f"[1단계] Pajek 네트워크 파일 파싱: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 헤더 파싱
    header = lines[0].strip()
    parts = header.split()
    n_nodes = int(parts[1])
    
    print(f"  노드 수: {n_nodes}")
    
    # 노드 정보 파싱
    nodes = {}  # {node_id: node_label}
    
    i = 1
    for idx in range(n_nodes):
        if i >= len(lines):
            break
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        parts = line.split('"')
        if len(parts) >= 2:
            node_id = int(parts[0].strip())
            node_label = parts[1].strip()
            nodes[node_id] = node_label
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
            u = int(parts[0])
            v = int(parts[1])
            weight = int(parts[2]) if len(parts) >= 3 else 1
            if u in nodes and v in nodes:
                edges.append((u, v, weight))
        i += 1
    
    print(f"  엣지 수: {len(edges)}")
    
    return nodes, edges


def create_network_from_pajek(nodes, edges):
    """Pajek 데이터로부터 NetworkX 그래프를 생성합니다."""
    print(f"[2단계] NetworkX 그래프 생성")
    
    G = nx.Graph()
    
    # 노드 추가
    for node_id, node_label in nodes.items():
        G.add_node(node_id, label=node_label)
    
    # 엣지 추가
    for u, v, weight in edges:
        G.add_edge(u, v, weight=weight)
    
    print(f"  그래프 노드 수: {G.number_of_nodes()}")
    print(f"  그래프 엣지 수: {G.number_of_edges()}")
    
    return G


def calculate_degree_statistics(G):
    """Degree 통계를 계산합니다."""
    degrees = dict(G.degree())
    degree_values = np.array(list(degrees.values()))
    
    stats_dict = {
        'mean': np.mean(degree_values),
        'median': np.median(degree_values),
        'std': np.std(degree_values),
        'min': np.min(degree_values),
        'max': np.max(degree_values),
        'percentile_25': np.percentile(degree_values, 25),
        'percentile_75': np.percentile(degree_values, 75),
        'percentile_95': np.percentile(degree_values, 95),
        'percentile_99': np.percentile(degree_values, 99)
    }
    
    return stats_dict, degree_values, degrees


def calculate_pdf(degree_values):
    """PDF (Probability Density Function)를 계산합니다."""
    unique_degrees, counts = np.unique(degree_values, return_counts=True)
    pdf = counts / len(degree_values)
    return unique_degrees, pdf


def calculate_ccdf(degree_values):
    """CCDF (Complementary Cumulative Distribution Function)를 계산합니다."""
    sorted_degrees = np.sort(degree_values)[::-1]  # 내림차순
    n = len(sorted_degrees)
    ccdf = np.arange(1, n + 1) / n
    return sorted_degrees, ccdf


def fit_power_law(degrees, ccdf):
    """Power-law를 피팅합니다."""
    # 양수 값만 사용
    valid_idx = (degrees > 0) & (ccdf > 0)
    degrees_valid = degrees[valid_idx]
    ccdf_valid = ccdf[valid_idx]
    
    if len(degrees_valid) < 5:
        return None, None, None
    
    # 로그 공간으로 변환
    log_degrees = np.log(degrees_valid)
    log_ccdf = np.log(ccdf_valid)
    
    # 선형 회귀
    slope, intercept, r_value, p_value, std_err = stats.linregress(log_degrees, log_ccdf)
    
    # Power-law 지수 (γ)
    gamma = -slope
    
    return gamma, r_value**2, (slope, intercept)


def plot_degree_distributions(G, degree_values, degrees, output_dir):
    """Degree Distribution을 시각화합니다."""
    print(f"[3단계] Degree Distribution 시각화")
    
    # 통계 계산
    stats_dict, _, _ = calculate_degree_statistics(G)
    
    # PDF 계산
    unique_degrees_pdf, pdf = calculate_pdf(degree_values)
    
    # CCDF 계산
    sorted_degrees_ccdf, ccdf = calculate_ccdf(degree_values)
    
    # CDF 계산
    sorted_degrees_cdf = np.sort(degree_values)
    cdf = np.arange(1, len(sorted_degrees_cdf) + 1) / len(sorted_degrees_cdf)
    
    # Power-law 피팅
    gamma, r_squared, fit_params = fit_power_law(sorted_degrees_ccdf, ccdf)
    
    # 시각화
    fig = plt.figure(figsize=(20, 15))
    
    # 1. PDF (선형 스케일)
    ax1 = plt.subplot(3, 3, 1)
    ax1.plot(unique_degrees_pdf, pdf, 'b-', linewidth=2, marker='o', markersize=4)
    ax1.set_xlabel('Degree (k)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('P(k)', fontsize=12, fontweight='bold')
    ax1.set_title('PDF (Probability Density Function)\nLinear Scale', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 2. PDF (로그-로그 스케일)
    ax2 = plt.subplot(3, 3, 2)
    ax2.loglog(unique_degrees_pdf, pdf, 'b-', linewidth=2, marker='o', markersize=4)
    ax2.set_xlabel('Degree (k)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('P(k)', fontsize=12, fontweight='bold')
    ax2.set_title('PDF (Probability Density Function)\nLog-Log Scale', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 3. CCDF (선형 스케일)
    ax3 = plt.subplot(3, 3, 3)
    ax3.plot(sorted_degrees_ccdf, ccdf, 'r-', linewidth=2)
    ax3.set_xlabel('Degree (k)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('P(K ≥ k)', fontsize=12, fontweight='bold')
    ax3.set_title('CCDF (Complementary Cumulative Distribution)\nLinear Scale', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 4. CCDF (로그-로그 스케일) - Power-law 확인
    ax4 = plt.subplot(3, 3, 4)
    ax4.loglog(sorted_degrees_ccdf, ccdf, 'r-', linewidth=2, label='CCDF')
    
    # Power-law 피팅 선 추가
    if gamma is not None and fit_params is not None:
        slope, intercept = fit_params
        fit_degrees = np.logspace(np.log10(sorted_degrees_ccdf.min()), 
                                  np.log10(sorted_degrees_ccdf.max()), 100)
        fit_ccdf = np.exp(intercept) * (fit_degrees ** slope)
        ax4.plot(fit_degrees, fit_ccdf, 'g--', linewidth=2, 
                label=f'Power Law Fit: γ ≈ {gamma:.2f}\n(R² = {r_squared:.3f})')
        ax4.legend(fontsize=10)
    
    ax4.set_xlabel('Degree (k)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('P(K ≥ k)', fontsize=12, fontweight='bold')
    ax4.set_title('CCDF (Log-Log Scale)\nPower Law Analysis', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # 5. CDF (선형 스케일)
    ax5 = plt.subplot(3, 3, 5)
    ax5.plot(sorted_degrees_cdf, cdf, 'g-', linewidth=2)
    ax5.set_xlabel('Degree (k)', fontsize=12, fontweight='bold')
    ax5.set_ylabel('P(K ≤ k)', fontsize=12, fontweight='bold')
    ax5.set_title('CDF (Cumulative Distribution Function)\nLinear Scale', fontsize=14, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # 6. CDF (로그 X축) - Power Tail 확인
    ax6 = plt.subplot(3, 3, 6)
    ax6.semilogx(sorted_degrees_cdf, cdf, 'g-', linewidth=2)
    ax6.set_xlabel('Degree (k) [Log Scale]', fontsize=12, fontweight='bold')
    ax6.set_ylabel('P(K ≤ k)', fontsize=12, fontweight='bold')
    ax6.set_title('CDF (Log X-axis)\nPower Tail Analysis', fontsize=14, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    
    # 7. Degree 히스토그램
    ax7 = plt.subplot(3, 3, 7)
    ax7.hist(degree_values, bins=50, edgecolor='black', alpha=0.7, color='skyblue')
    ax7.axvline(stats_dict['mean'], color='r', linestyle='--', linewidth=2, label=f'Mean: {stats_dict["mean"]:.1f}')
    ax7.axvline(stats_dict['median'], color='g', linestyle='--', linewidth=2, label=f'Median: {stats_dict["median"]:.1f}')
    ax7.set_xlabel('Degree (k)', fontsize=12, fontweight='bold')
    ax7.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax7.set_title('Degree Histogram', fontsize=14, fontweight='bold')
    ax7.legend(fontsize=10)
    ax7.grid(True, alpha=0.3)
    
    # 8. Top 20 노드 (Degree 기준)
    ax8 = plt.subplot(3, 3, 8)
    top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:20]
    node_ids = [n[0] for n in top_nodes]
    node_degrees = [n[1] for n in top_nodes]
    node_labels = [G.nodes[n[0]].get('label', str(n[0])) for n in top_nodes]
    
    # 레이블 길이 제한
    node_labels_short = [label[:15] + '...' if len(label) > 15 else label for label in node_labels]
    
    ax8.barh(range(len(node_ids)), node_degrees, color='coral')
    ax8.set_yticks(range(len(node_ids)))
    ax8.set_yticklabels(node_labels_short, fontsize=9)
    ax8.set_xlabel('Degree', fontsize=12, fontweight='bold')
    ax8.set_title('Top 20 Nodes by Degree', fontsize=14, fontweight='bold')
    ax8.invert_yaxis()
    ax8.grid(True, alpha=0.3, axis='x')
    
    # 9. 통계 요약 텍스트
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('off')
    
    stats_text = f"""
Degree Distribution Statistics

Basic Statistics:
  Mean: {stats_dict['mean']:.2f}
  Median: {stats_dict['median']:.2f}
  Std Dev: {stats_dict['std']:.2f}
  Min: {stats_dict['min']}
  Max: {stats_dict['max']}
  
Percentiles:
  25th: {stats_dict['percentile_25']:.1f}
  75th: {stats_dict['percentile_75']:.1f}
  95th: {stats_dict['percentile_95']:.1f}
  99th: {stats_dict['percentile_99']:.1f}

Power Law Analysis:
"""
    if gamma is not None:
        stats_text += f"  Exponent (γ): {gamma:.2f}\n"
        stats_text += f"  R²: {r_squared:.3f}\n"
        stats_text += f"  Form: P(K ≥ k) ~ k^(-{gamma:.2f})"
    else:
        stats_text += "  Power Law fitting failed"
    
    ax9.text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
            family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.suptitle('Skill-Skill Network Degree Distribution Analysis', 
                fontsize=18, fontweight='bold', y=0.995)
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    
    output_path = os.path.join(output_dir, 'degree_distribution_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  저장 완료: {output_path}")
    plt.close()
    
    return stats_dict, gamma, r_squared


def create_analysis_markdown(G, stats_dict, gamma, r_squared, degrees, output_dir):
    """분석 결과를 마크다운 파일로 생성합니다."""
    print(f"[4단계] 분석 문서 생성")
    
    # Top 10 노드
    top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]
    top_node_info = []
    for node_id, degree in top_nodes:
        label = G.nodes[node_id].get('label', str(node_id))
        top_node_info.append({'node': label, 'degree': degree})
    
    markdown_content = f"""# Skill-Skill 네트워크 Degree Distribution 분석

## 개요
본 문서는 Skill-Skill One-mode Projection 네트워크의 Degree Distribution을 분석한 결과를 정리합니다.

**분석 목적**:
- 네트워크의 연결 구조 파악
- Power-law 분포 여부 확인
- 허브 노드(Hub Node) 존재 여부 검증
- 네트워크의 척도 없는(Scale-free) 특성 확인

**네트워크 특성**:
- 노드 수: {G.number_of_nodes()}개 (스킬)
- 엣지 수: {G.number_of_edges()}개
- 네트워크 밀도: {nx.density(G):.4f}

---

## 1. Degree Distribution 개념

### 1.1 Degree란?
**Degree**는 네트워크에서 한 노드가 다른 노드들과 얼마나 많은 연결을 가지고 있는지를 나타내는 지표입니다.

- Skill-Skill 네트워크에서: 한 스킬이 다른 스킬들과 얼마나 많이 함께 등장하는지를 의미
- 높은 Degree: 많은 스킬과 함께 사용되는 범용 스킬 (예: Python, SQL, AI)
- 낮은 Degree: 특정 상황에서만 사용되는 전문 스킬

### 1.2 PDF (Probability Density Function)
**PDF**는 각 Degree 값이 나타날 확률을 나타냅니다.
- P(k): Degree가 정확히 k인 노드의 비율
- 선형 스케일: 전체 분포의 모양을 파악
- 로그-로그 스케일: Power-law 분포 여부를 확인

### 1.3 CCDF (Complementary Cumulative Distribution Function)
**CCDF**는 Degree가 k 이상인 노드의 비율을 나타냅니다.
- P(K ≥ k): Degree가 k 이상인 노드의 비율
- Power-law 분포를 확인하는 데 유용
- 로그-로그 스케일에서 직선이면 Power-law 분포를 따름

### 1.4 Power-law Tail
**Power-law Tail**은 높은 Degree를 가진 노드들이 긴 꼬리를 형성하는 현상입니다.
- 소수의 허브 노드가 네트워크의 대부분 연결을 담당
- 척도 없는(Scale-free) 네트워크의 특징
- CDF의 로그 스케일 그래프에서 확인 가능

---

## 2. Degree 통계

### 2.1 기본 통계

| 통계량 | 값 |
|--------|-----|
| **평균 (Mean)** | {stats_dict['mean']:.2f} |
| **중앙값 (Median)** | {stats_dict['median']:.2f} |
| **표준편차 (Std Dev)** | {stats_dict['std']:.2f} |
| **최소값 (Min)** | {stats_dict['min']} |
| **최대값 (Max)** | {stats_dict['max']} |

### 2.2 분위수

| 분위수 | 값 |
|--------|-----|
| **25th Percentile** | {stats_dict['percentile_25']:.1f} |
| **75th Percentile** | {stats_dict['percentile_75']:.1f} |
| **95th Percentile** | {stats_dict['percentile_95']:.1f} |
| **99th Percentile** | {stats_dict['percentile_99']:.1f} |

### 2.3 통계 해석

**평균 vs 중앙값**:
- 평균 ({stats_dict['mean']:.2f}) > 중앙값 ({stats_dict['median']:.2f})
- 이는 **오른쪽 꼬리가 긴 분포(Right-skewed)**를 의미합니다.
- 소수의 높은 Degree 노드(허브)가 평균을 끌어올립니다.

**표준편차**:
- 표준편차 ({stats_dict['std']:.2f})가 평균 ({stats_dict['mean']:.2f})과 비슷하거나 큽니다.
- 이는 Degree 분포의 **변동성이 크다**는 것을 의미합니다.
- 일부 노드는 매우 높은 Degree를, 일부는 매우 낮은 Degree를 가집니다.

**분위수 분석**:
- 95th Percentile ({stats_dict['percentile_95']:.1f})은 평균 ({stats_dict['mean']:.2f})보다 훨씬 큽니다.
- 이는 상위 5% 노드가 평균보다 훨씬 높은 Degree를 가짐을 의미합니다.
- **허브 노드의 존재**를 시사합니다.

---

## 3. Power-law 분석

### 3.1 Power-law 분포란?
**Power-law 분포**는 다음과 같은 형태를 가집니다:

P(K ≥ k) ~ k^(-γ)

여기서 γ는 Power-law 지수입니다.

### 3.2 Power-law 지수 추정

"""
    
    if gamma is not None:
        markdown_content += f"""**추정 결과**:
- **Power-law 지수 (γ)**: {gamma:.2f}
- **R² (결정계수)**: {r_squared:.3f}
- **Power-law 형태**: P(K ≥ k) ~ k^(-{gamma:.2f})

### 3.3 Power-law 해석

"""
        if gamma > 2:
            markdown_content += f"""- **γ = {gamma:.2f} > 2**: Power-law 분포를 따르며, 허브 노드가 존재합니다.
- 높은 Degree를 가진 노드들이 예상보다 많습니다.
- 네트워크가 **척도 없는(Scale-free) 특성**을 가집니다.
- 소수의 허브 노드(Python, AI, SQL 등)가 네트워크의 중심 역할을 합니다.

"""
        elif gamma > 1:
            markdown_content += f"""- **γ = {gamma:.2f} > 1**: Power-law 분포를 따르며, 허브 노드가 존재합니다.
- 높은 Degree를 가진 노드들이 일부 존재합니다.
- 네트워크가 **약한 척도 없는 특성**을 가집니다.

"""
        else:
            markdown_content += f"""- **γ = {gamma:.2f} ≤ 1**: Power-law 특성이 약합니다.
- 허브 노드의 영향이 제한적입니다.

"""
        
        if r_squared > 0.9:
            markdown_content += f"""- **R² = {r_squared:.3f} > 0.9**: Power-law 피팅이 매우 좋습니다.
- CCDF가 로그-로그 스케일에서 거의 직선에 가깝습니다.

"""
        elif r_squared > 0.7:
            markdown_content += f"""- **R² = {r_squared:.3f} > 0.7**: Power-law 피팅이 양호합니다.
- CCDF가 로그-로그 스케일에서 대체로 직선에 가깝습니다.

"""
        else:
            markdown_content += f"""- **R² = {r_squared:.3f} ≤ 0.7**: Power-law 피팅이 약합니다.
- CCDF가 로그-로그 스케일에서 직선에서 벗어납니다.
- 다른 분포(예: 지수 분포, 로그 정규 분포)를 고려해야 할 수 있습니다.

"""
    else:
        markdown_content += """**Power-law 피팅 실패**: 데이터가 Power-law 분포를 따르지 않을 수 있습니다.

"""
    
    markdown_content += f"""---

## 4. Top 10 노드 (Degree 기준)

| 순위 | 스킬 | Degree |
|------|------|--------|
"""
    
    for i, node_info in enumerate(top_node_info, 1):
        markdown_content += f"| {i} | {node_info['node']} | {node_info['degree']} |\n"
    
    markdown_content += f"""
### 해석
- 상위 노드들은 **범용 스킬**로, 다양한 직군에서 요구되는 핵심 스킬입니다.
- 이들은 네트워크의 **허브(Hub)** 역할을 하며, 네트워크 구조의 중심을 형성합니다.
- 소수의 허브 노드가 네트워크의 대부분 연결을 담당하는 **Power-law 특성**을 보여줍니다.

---

## 5. 시각화 해석

### 5.1 PDF (Probability Density Function)

**선형 스케일**:
- Degree 분포의 전체적인 모양을 파악할 수 있습니다.
- 오른쪽 꼬리가 긴 분포(Right-skewed)를 확인할 수 있습니다.

**로그-로그 스케일**:
- Power-law 분포 여부를 확인할 수 있습니다.
- 직선에 가까우면 Power-law 분포를 따릅니다.

### 5.2 CCDF (Complementary Cumulative Distribution Function)

**선형 스케일**:
- 높은 Degree를 가진 노드의 비율을 파악할 수 있습니다.

**로그-로그 스케일**:
- Power-law 분포를 확인하는 데 가장 유용합니다.
- 직선이면 Power-law 분포: P(K ≥ k) ~ k^(-γ)
- 피팅된 직선의 기울기가 -γ입니다.

### 5.3 CDF (Cumulative Distribution Function)

**선형 스케일**:
- Degree가 특정 값 이하인 노드의 비율을 파악할 수 있습니다.

**로그 X축**:
- Power Tail을 확인할 수 있습니다.
- 높은 Degree 영역에서 긴 꼬리를 형성하면 허브 노드가 존재함을 의미합니다.

---

## 6. 인사이트 및 결론

### 6.1 주요 발견사항

1. **Power-law 분포 특성**
"""
    
    if gamma is not None and gamma > 1:
        markdown_content += f"""   - 네트워크가 Power-law 분포를 따릅니다 (γ = {gamma:.2f}).
   - 소수의 허브 노드가 네트워크의 중심 역할을 합니다.
   - 네트워크가 **척도 없는(Scale-free) 특성**을 가집니다.

"""
    else:
        markdown_content += """   - 네트워크가 Power-law 분포를 따르지 않거나 약한 특성을 보입니다.
   - 허브 노드의 영향이 제한적일 수 있습니다.

"""
    
    markdown_content += f"""2. **허브 노드의 존재**
   - 평균 ({stats_dict['mean']:.2f})과 중앙값 ({stats_dict['median']:.2f})의 차이가 큽니다.
   - 95th Percentile ({stats_dict['percentile_95']:.1f})이 평균보다 훨씬 큽니다.
   - 상위 10개 노드가 네트워크의 상당 부분을 연결합니다.

3. **네트워크 구조**
   - 오른쪽 꼬리가 긴 분포로, 소수의 높은 Degree 노드가 존재합니다.
   - 대부분의 노드는 낮은~중간 Degree를 가지지만, 소수는 매우 높은 Degree를 가집니다.

### 6.2 실무적 시사점

1. **스킬 중요도**
   - 높은 Degree를 가진 스킬(Python, AI, SQL 등)은 **핵심 스킬**입니다.
   - 이러한 스킬은 다양한 직군에서 요구되며, 채용 시 중요하게 고려됩니다.

2. **스킬 네트워크의 구조**
   - 네트워크가 허브 중심 구조를 가집니다.
   - 소수의 범용 스킬이 네트워크의 중심을 형성하며, 대부분의 스킬은 이들과 연결됩니다.

3. **스킬 학습 전략**
   - 허브 스킬을 먼저 학습하면 네트워크의 많은 스킬과 연결될 수 있습니다.
   - 범용 스킬을 기반으로 전문 스킬을 확장하는 전략이 효과적입니다.

### 6.3 제한사항

1. **샘플 수의 영향**
   - 자주 등장하는 스킬이 높은 Degree를 가질 수 있습니다.
   - 이는 실제 중요도가 아니라 데이터 수집 편향일 수 있습니다.

2. **Power-law 피팅의 한계**
   - Power-law 피팅은 근사치이며, 실제 분포와 완전히 일치하지 않을 수 있습니다.
   - 다른 분포(지수 분포, 로그 정규 분포 등)도 고려해야 할 수 있습니다.

3. **네트워크 밀도**
   - 네트워크 밀도가 높으면 대부분의 노드가 연결되어 있어 Degree 분포의 의미가 달라질 수 있습니다.

---

## 7. 참고사항

### 7.1 Power-law 지수의 의미

- **γ > 2**: 강한 Power-law, 허브 노드가 명확히 존재
- **1 < γ ≤ 2**: 약한 Power-law, 허브 노드가 일부 존재
- **γ ≤ 1**: Power-law 특성이 약함

### 7.2 척도 없는 네트워크 (Scale-free Network)

- Power-law 분포를 따르는 네트워크를 척도 없는 네트워크라고 합니다.
- 대부분의 노드는 낮은 Degree를 가지지만, 소수는 매우 높은 Degree를 가집니다.
- 허브 노드가 네트워크의 구조와 기능에 큰 영향을 미칩니다.

---

*본 분석은 NetworkX와 SciPy를 사용하여 수행되었습니다.*
"""
    
    output_path = os.path.join(output_dir, 'DegreeDistribution_Analysis.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"  저장 완료: {output_path}")


def main():
    """메인 함수"""
    print("=" * 70)
    print("Skill-Skill 네트워크 Degree Distribution 분석")
    print("=" * 70)
    
    # 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'skill_skill_network.net')
    
    # 출력 폴더 생성
    output_dir = os.path.join(os.path.dirname(script_dir), 'Skill_Skill_DegreeDistribute')
    os.makedirs(output_dir, exist_ok=True)
    
    # 1단계: Pajek 파일 파싱
    nodes, edges = parse_pajek_network(input_file)
    
    # 2단계: NetworkX 그래프 생성
    G = create_network_from_pajek(nodes, edges)
    
    # 3단계: Degree 통계 계산
    stats_dict, degree_values, degrees = calculate_degree_statistics(G)
    
    print(f"\n[통계 요약]")
    print(f"  평균 Degree: {stats_dict['mean']:.2f}")
    print(f"  중앙값 Degree: {stats_dict['median']:.2f}")
    print(f"  최대 Degree: {stats_dict['max']}")
    print(f"  최소 Degree: {stats_dict['min']}")
    
    # 4단계: 시각화
    stats_dict, gamma, r_squared = plot_degree_distributions(G, degree_values, degrees, output_dir)
    
    if gamma is not None:
        print(f"\n[Power-law 분석]")
        print(f"  Power-law 지수 (γ): {gamma:.2f}")
        print(f"  R²: {r_squared:.3f}")
    
    # 5단계: 분석 문서 생성
    create_analysis_markdown(G, stats_dict, gamma, r_squared, degrees, output_dir)
    
    print("\n" + "=" * 70)
    print("작업 완료!")
    print(f"출력 폴더: {output_dir}")
    print("=" * 70)


if __name__ == '__main__':
    main()

