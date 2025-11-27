"""
개발관련_raw: 전체 분석 실행 스크립트
데이터관련_raw와 동일한 분석 흐름을 실행합니다.
"""

import os
import sys

# 현재 디렉토리로 이동
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print("="*60)
print("개발관련_raw: 전체 분석 실행")
print("="*60)

# 1. Bipartite 네트워크 시각화
print("\n[1단계] Bipartite 네트워크 시각화")
print("-" * 60)

from visualize_bipartite_network_dev import (
    read_2mode_network, 
    strategy1_basic_bipartite,
    strategy2_degree_based,
    strategy4_cooccurrence_heatmap,
    strategy7_projection
)

net_file = 'developer_bipartite_skill_2mode.net'
if not os.path.exists(net_file):
    print(f"오류: '{net_file}' 파일을 찾을 수 없습니다.")
    sys.exit(1)

# 네트워크 로딩
G, companies, skills, node_id_to_label, n_companies, n_skills = read_2mode_network(net_file)

# 전략 1: 기본 Bipartite 레이아웃
print("\n>>> 전략 1 실행 중...")
try:
    strategy1_basic_bipartite(G, companies, skills, node_id_to_label)
    print("✓ 전략 1 완료")
except Exception as e:
    print(f"⚠ 전략 1 오류: {e}")

# 전략 2: Degree 기반 시각화
print("\n>>> 전략 2 실행 중...")
try:
    strategy2_degree_based(G, companies, skills, node_id_to_label)
    print("✓ 전략 2 완료")
except Exception as e:
    print(f"⚠ 전략 2 오류: {e}")

# 전략 4: Co-occurrence 히트맵
print("\n>>> 전략 4 실행 중...")
try:
    strategy4_cooccurrence_heatmap(G, companies, skills, node_id_to_label)
    print("✓ 전략 4 완료")
except Exception as e:
    print(f"⚠ 전략 4 오류: {e}")

# 전략 7: Projection 네트워크
print("\n>>> 전략 7 실행 중...")
try:
    strategy7_projection(G, companies, skills, node_id_to_label)
    print("✓ 전략 7 완료")
except Exception as e:
    print(f"⚠ 전략 7 오류: {e}")

# 2. Skill-Skill 네트워크 심층 분석
print("\n[2단계] Skill-Skill 네트워크 심층 분석")
print("-" * 60)

from analyze_skill_network_dev import main as analyze_main

try:
    analyze_main()
    print("✓ 심층 분석 완료")
except Exception as e:
    print(f"⚠ 심층 분석 오류: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("전체 분석 완료!")
print("="*60)



