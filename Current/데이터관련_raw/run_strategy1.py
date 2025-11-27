"""
전략 1: 기본 Bipartite 레이아웃 실행
"""

import networkx as nx
import matplotlib.pyplot as plt
import os
import sys

# 기존 모듈의 함수들 import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visualize_bipartite_network import read_2mode_network, strategy1_basic_bipartite

def main():
    print("="*60)
    print("전략 1: 기본 Bipartite 레이아웃 (양쪽 정렬)")
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
    G, companies, skills, node_id_to_label, n_companies, n_skills = read_2mode_network(net_file)
    
    # 전략 1 실행
    try:
        strategy1_basic_bipartite(G, companies, skills, node_id_to_label)
        print("\n✓ 전략 1 완료!")
        print("출력 파일: bipartite_basic.png")
    except Exception as e:
        print(f"\n⚠ 전략 1 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

