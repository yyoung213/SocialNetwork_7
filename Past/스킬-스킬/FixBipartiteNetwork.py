"""
bipartite_skill_network.net 파일을 Pajek 2-Mode 네트워크 형식으로 수정하는 스크립트

Pajek 2-Mode 네트워크 형식:
*Vertices N
1 "노드명" 1
2 "노드명" 2
...

각 노드에 모드 값(1 또는 2)을 추가해야 합니다.
"""

def fix_bipartite_network_to_2mode(input_file: str = 'bipartite_skill_network.net',
                                   partition_file: str = 'bipartite_skill_network.clu',
                                   output_file: str = 'bipartite_skill_network_2mode.net'):
    """
    bipartite 네트워크 파일을 Pajek 2-Mode 형식으로 수정합니다.
    
    Args:
        input_file (str): 입력 .net 파일
        partition_file (str): Partition 파일 (.clu) - 노드 타입 구분용
        output_file (str): 출력 .net 파일 (2-Mode 형식)
    """
    print("=" * 60)
    print("Bipartite Network → 2-Mode Network 변환")
    print("=" * 60)
    
    # Partition 파일 읽기 (노드 타입 확인)
    print(f"\nPartition 파일 읽기: {partition_file}")
    partition_values = {}
    
    with open(partition_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    num_vertices = int(lines[0].split()[-1])
    print(f"  총 노드 수: {num_vertices:,}개")
    
    for i in range(1, num_vertices + 1):
        partition_value = int(lines[i].strip())
        partition_values[i] = partition_value
    
    company_count = sum(1 for v in partition_values.values() if v == 1)
    skill_count = sum(1 for v in partition_values.values() if v == 2)
    
    print(f"  기업 노드 (모드 1): {company_count:,}개")
    print(f"  스킬 노드 (모드 2): {skill_count:,}개")
    
    # .net 파일 읽기 및 수정
    print(f"\n네트워크 파일 읽기: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Vertices 섹션 찾기
    vertices_start_idx = None
    edges_start_idx = None
    
    for i, line in enumerate(lines):
        if line.startswith('*Vertices'):
            vertices_start_idx = i
            num_vertices_declared = int(line.split()[-1])
        elif line.startswith('*Edges'):
            edges_start_idx = i
            break
    
    if vertices_start_idx is None:
        print("  ⚠ *Vertices 섹션을 찾을 수 없습니다.")
        return
    
    if edges_start_idx is None:
        print("  ⚠ *Edges 섹션을 찾을 수 없습니다.")
        return
    
    print(f"  Vertices 섹션: {vertices_start_idx + 1}번째 줄부터")
    print(f"  Edges 섹션: {edges_start_idx + 1}번째 줄부터")
    
    # 2-Mode 형식으로 수정
    print(f"\n2-Mode 형식으로 변환 중...")
    
    new_lines = []
    
    # 헤더 복사
    new_lines.append(lines[vertices_start_idx])
    
    # Vertices 섹션 수정 (모드 값 추가)
    vertex_count = 0
    for i in range(vertices_start_idx + 1, edges_start_idx):
        line = lines[i].strip()
        if not line:
            continue
        
        vertex_count += 1
        node_id = vertex_count
        
        # 노드 정의 파싱: "번호 "레이블"" 또는 "번호 레이블"
        if '"' in line:
            # 따옴표가 있는 경우
            parts = line.split('"', 1)
            node_num = parts[0].strip()
            label = '"' + parts[1] if len(parts) > 1 else ''
            
            # 모드 값 가져오기
            mode = partition_values.get(node_id, 1)
            
            # 2-Mode 형식: "번호 "레이블" 모드"
            new_line = f'{node_num} "{label.split('"')[1]}" {mode}'
            new_lines.append(new_line)
        else:
            # 따옴표가 없는 경우 (일반적으로 발생하지 않음)
            parts = line.split()
            if len(parts) >= 2:
                node_num = parts[0]
                label = ' '.join(parts[1:])
                mode = partition_values.get(node_id, 1)
                new_line = f'{node_num} "{label}" {mode}'
                new_lines.append(new_line)
    
    print(f"  처리된 노드 수: {vertex_count:,}개")
    
    # Edges 섹션 복사
    new_lines.append('')  # 빈 줄
    for i in range(edges_start_idx, len(lines)):
        new_lines.append(lines[i])
    
    # 새 파일 저장
    print(f"\n2-Mode 네트워크 파일 저장 중: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f"  ✓ 변환 완료!")
    
    # 검증
    print(f"\n검증 중...")
    with open(output_file, 'r', encoding='utf-8') as f:
        sample_lines = f.readlines()[:20]
    
    print(f"  샘플 노드 정의 (처음 5개):")
    for i, line in enumerate(sample_lines[1:6], 1):
        if line.strip() and not line.startswith('*'):
            print(f"    {line.strip()}")
    
    print(f"\n  샘플 노드 정의 (기업→스킬 경계 근처):")
    # 기업 마지막 노드와 스킬 첫 노드 확인
    with open(output_file, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
    
    # 기업 마지막 (1260번째 노드)
    if len(all_lines) > 1260:
        print(f"    {all_lines[1260].strip()}")
    # 스킬 첫 번째 (1261번째 노드)
    if len(all_lines) > 1261:
        print(f"    {all_lines[1261].strip()}")
    
    print("\n" + "=" * 60)
    print("변환 완료!")
    print("=" * 60)
    print(f"\n생성된 파일: {output_file}")
    print(f"\nPajek 사용 방법:")
    print(f"  1. File → Network → Read → {output_file}")
    print(f"  2. Pajek이 자동으로 2-Mode 네트워크로 인식합니다")
    print(f"  3. Draw → Network → Draw-Partition")
    print(f"  4. 또는 Draw → Energy → Kamada-Kawai → Bipartite")


if __name__ == "__main__":
    fix_bipartite_network_to_2mode()

