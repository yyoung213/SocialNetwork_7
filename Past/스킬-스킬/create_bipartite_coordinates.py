"""
Bipartite 네트워크를 위한 좌표 파일 생성 스크립트
기업 노드를 왼쪽에, 스킬 노드를 오른쪽에 정렬하여 배치
"""

def create_bipartite_coordinates(partition_file: str, output_file: str = 'bipartite_coordinates.coord'):
    """
    Partition 파일을 기반으로 bipartite 네트워크의 좌표 파일을 생성합니다.
    
    Args:
        partition_file (str): Partition 파일 경로 (.clu)
        output_file (str): 출력 좌표 파일 경로 (.coord)
    """
    print(f"Partition 파일 읽기: {partition_file}")
    
    # Partition 파일 읽기
    with open(partition_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 첫 번째 줄에서 노드 수 추출
    num_vertices = int(lines[0].split()[-1])
    print(f"  총 노드 수: {num_vertices:,}개")
    
    # 노드 분류
    company_nodes = []  # partition = 1
    skill_nodes = []   # partition = 2
    
    for i in range(1, num_vertices + 1):
        partition_value = int(lines[i].strip())
        node_id = i  # Pajek은 1부터 시작
        
        if partition_value == 1:  # 기업
            company_nodes.append(node_id)
        elif partition_value == 2:  # 스킬
            skill_nodes.append(node_id)
    
    print(f"  기업 노드: {len(company_nodes):,}개")
    print(f"  스킬 노드: {len(skill_nodes):,}개")
    
    # 좌표 생성
    # 기업 노드: X=0 (왼쪽), Y는 0~1 사이 균등 분배
    # 스킬 노드: X=1 (오른쪽), Y는 0~1 사이 균등 분배
    
    coordinates = {}
    
    # 기업 노드 좌표
    num_companies = len(company_nodes)
    for idx, node_id in enumerate(company_nodes):
        x = 0.0  # 왼쪽
        y = (idx + 1) / (num_companies + 1)  # 0~1 사이 균등 분배
        coordinates[node_id] = (x, y)
    
    # 스킬 노드 좌표
    num_skills = len(skill_nodes)
    for idx, node_id in enumerate(skill_nodes):
        x = 1.0  # 오른쪽
        y = (idx + 1) / (num_skills + 1)  # 0~1 사이 균등 분배
        coordinates[node_id] = (x, y)
    
    # 좌표 파일 작성
    print(f"\n좌표 파일 생성 중: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"*Vertices {num_vertices}\n")
        
        # 노드 ID 순서대로 좌표 작성
        for node_id in range(1, num_vertices + 1):
            x, y = coordinates[node_id]
            f.write(f"{x} {y}\n")
    
    print(f"  ✓ 좌표 파일 생성 완료")
    print(f"\n사용 방법:")
    print(f"  1. Pajek에서 네트워크 파일 로드")
    print(f"  2. File → Network → Read Coordinates → {output_file}")
    print(f"  3. Draw → Network")


def create_bipartite_coordinates_vertical(partition_file: str, output_file: str = 'bipartite_coordinates_vertical.coord'):
    """
    수직 정렬 버전: 기업 노드를 위쪽에, 스킬 노드를 아래쪽에 배치
    """
    print(f"Partition 파일 읽기: {partition_file}")
    
    with open(partition_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    num_vertices = int(lines[0].split()[-1])
    print(f"  총 노드 수: {num_vertices:,}개")
    
    company_nodes = []
    skill_nodes = []
    
    for i in range(1, num_vertices + 1):
        partition_value = int(lines[i].strip())
        node_id = i
        
        if partition_value == 1:
            company_nodes.append(node_id)
        elif partition_value == 2:
            skill_nodes.append(node_id)
    
    print(f"  기업 노드: {len(company_nodes):,}개")
    print(f"  스킬 노드: {len(skill_nodes):,}개")
    
    coordinates = {}
    
    # 기업 노드: 위쪽 (Y=1), X는 0~1 사이 균등 분배
    num_companies = len(company_nodes)
    for idx, node_id in enumerate(company_nodes):
        x = (idx + 1) / (num_companies + 1)
        y = 1.0  # 위쪽
        coordinates[node_id] = (x, y)
    
    # 스킬 노드: 아래쪽 (Y=0), X는 0~1 사이 균등 분배
    num_skills = len(skill_nodes)
    for idx, node_id in enumerate(skill_nodes):
        x = (idx + 1) / (num_skills + 1)
        y = 0.0  # 아래쪽
        coordinates[node_id] = (x, y)
    
    print(f"\n좌표 파일 생성 중: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"*Vertices {num_vertices}\n")
        
        for node_id in range(1, num_vertices + 1):
            x, y = coordinates[node_id]
            f.write(f"{x} {y}\n")
    
    print(f"  ✓ 좌표 파일 생성 완료 (수직 정렬)")


if __name__ == "__main__":
    print("=" * 60)
    print("Bipartite 네트워크 좌표 파일 생성")
    print("=" * 60)
    
    partition_file = 'bipartite_skill_network.clu'
    
    # 수평 정렬 (기업 왼쪽, 스킬 오른쪽)
    create_bipartite_coordinates(partition_file, 'bipartite_coordinates.coord')
    
    print("\n" + "-" * 60)
    
    # 수직 정렬 (기업 위쪽, 스킬 아래쪽)
    create_bipartite_coordinates_vertical(partition_file, 'bipartite_coordinates_vertical.coord')
    
    print("\n" + "=" * 60)
    print("완료!")
    print("=" * 60)

