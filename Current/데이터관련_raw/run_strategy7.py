"""
전략 7: Projection 네트워크 (기업-기업, 스킬-스킬) 실행
"""

import networkx as nx
import matplotlib.pyplot as plt
import os
import sys

# 기존 모듈의 함수들 import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visualize_bipartite_network import read_2mode_network, strategy7_projection

def main():
    print("="*60)
    print("전략 7: Projection 네트워크 (기업-기업, 스킬-스킬)")
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
    
    # 전략 7 실행
    try:
        strategy7_projection(G, companies, skills, node_id_to_label)
        print("\n✓ 전략 7 완료!")
        print("출력 파일: projection_networks.png")
    except Exception as e:
        print(f"\n⚠ 전략 7 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()



