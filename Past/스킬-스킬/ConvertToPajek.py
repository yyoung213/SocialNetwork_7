"""
기존 NetworkX 그래프 파일을 Pajek .net 형식으로 변환하는 스크립트
"""

import networkx as nx
import os


def convert_graphml_to_pajek(graphml_file: str, output_file: str = None):
    """
    GraphML 파일을 Pajek .net 형식으로 변환합니다.
    
    Args:
        graphml_file (str): 입력 GraphML 파일 경로
        output_file (str): 출력 .net 파일 경로 (None이면 자동 생성)
    """
    if output_file is None:
        output_file = graphml_file.replace('.graphml', '.net')
    
    print(f"GraphML 파일 로딩 중: {graphml_file}")
    
    # GraphML 파일 읽기
    G = nx.read_graphml(graphml_file)
    
    print(f"  노드 수: {G.number_of_nodes()}개")
    print(f"  엣지 수: {G.number_of_edges()}개")
    
    # Pajek .net 형식으로 저장
    print(f"\nPajek .net 파일 생성 중: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # 노드 ID 매핑 (문자열 -> 숫자, 1부터 시작)
        sorted_nodes = sorted(G.nodes())
        node_to_id = {node: idx + 1 for idx, node in enumerate(sorted_nodes)}
        
        # Vertices 섹션
        f.write(f"*Vertices {G.number_of_nodes()}\n")
        for node in sorted_nodes:
            node_id = node_to_id[node]
            # Pajek 형식: id "label" (따옴표 안의 따옴표는 이스케이프)
            label_escaped = str(node).replace('"', '\\"')
            f.write(f'{node_id} "{label_escaped}"\n')
        
        # Edges 섹션 (무방향 그래프이므로 *Edges 사용)
        f.write(f"*Edges\n")
        for u, v in sorted(G.edges()):
            u_id = node_to_id[u]
            v_id = node_to_id[v]
            weight = G.edges[u, v].get('weight', 1)
            f.write(f"{u_id} {v_id} {weight}\n")
    
    print(f"  ✓ 변환 완료: {output_file}")
    return output_file


def main():
    """메인 함수 - 모든 graphml 파일을 .net으로 변환"""
    print("=" * 60)
    print("GraphML → Pajek .net 변환")
    print("=" * 60)
    
    # 현재 디렉토리의 모든 .graphml 파일 찾기
    graphml_files = [f for f in os.listdir('.') if f.endswith('.graphml')]
    
    if not graphml_files:
        print("⚠ .graphml 파일을 찾을 수 없습니다.")
        return
    
    print(f"\n발견된 GraphML 파일: {len(graphml_files)}개\n")
    
    for graphml_file in graphml_files:
        try:
            convert_graphml_to_pajek(graphml_file)
            print()
        except Exception as e:
            print(f"  ⚠ 변환 실패: {e}\n")
    
    print("=" * 60)
    print("변환 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()

