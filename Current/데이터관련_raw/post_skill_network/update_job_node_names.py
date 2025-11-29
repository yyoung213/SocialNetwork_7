"""
구인공고 노드명을 직군명으로 통일하는 스크립트
예: "BI 엔지니어_1" → "BI 엔지니어"
"""

import re
import os

def update_node_names(input_file, output_file):
    """구인공고 노드명에서 _숫자 부분을 제거합니다."""
    print(f"파일 읽기: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 첫 줄에서 노드 정보 읽기
    first_line = lines[0].strip()
    if not first_line.startswith('*Vertices'):
        print("오류: 잘못된 파일 형식입니다.")
        return
    
    parts = first_line.split()
    total_nodes = int(parts[1])
    mode1_count = int(parts[2])  # 구인공고 수
    
    print(f"  총 노드: {total_nodes}개")
    print(f"  구인공고 노드 (Mode 1): {mode1_count}개")
    print(f"  스킬 노드 (Mode 2): {total_nodes - mode1_count}개")
    
    # 파일 수정
    updated_lines = []
    updated_lines.append(first_line + '\n')
    
    node_id = 1
    in_vertices = True
    in_edges = False
    
    for line in lines[1:]:
        line_stripped = line.strip()
        
        # Edges/Arcs 섹션 시작
        if line_stripped.startswith('*Edges') or line_stripped.startswith('*Arcs'):
            in_vertices = False
            in_edges = True
            updated_lines.append(line)
            continue
        
        # Vertices 섹션 처리
        if in_vertices and line_stripped and not line_stripped.startswith('*'):
            # Mode 1 (구인공고) 노드만 수정
            if node_id <= mode1_count:
                # 형식: "번호 "노드명" x y z" 또는 "    번호 "노드명" x y z"
                if '"' in line_stripped:
                    # 노드명 추출
                    parts = line_stripped.split('"', 2)
                    if len(parts) >= 2:
                        node_name = parts[1].strip()
                        # _숫자 부분 제거
                        updated_name = re.sub(r'_\d+$', '', node_name)
                        
                        # 나머지 부분 (좌표 등) 유지
                        rest = parts[2] if len(parts) > 2 else ''
                        
                        # 노드 번호 추출
                        node_num = parts[0].strip()
                        
                        # 수정된 라인 생성
                        updated_line = f'{node_num} "{updated_name}"{rest}\n'
                        updated_lines.append(updated_line)
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)
            else:
                # Mode 2 (스킬) 노드는 그대로 유지
                updated_lines.append(line)
            
            node_id += 1
        else:
            # Edges 섹션이나 기타 라인은 그대로 유지
            updated_lines.append(line)
    
    # 파일 저장
    print(f"\n파일 저장: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    print("완료!")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'job_skill_bipartite_2mode.net')
    output_file = os.path.join(script_dir, 'job_skill_bipartite_2mode.net')
    
    update_node_names(input_file, output_file)


if __name__ == '__main__':
    main()

