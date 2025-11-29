"""
구인공고-스킬 Bipartite Network 생성 스크립트

업무1:
- data_bipartite_skill_edges.csv에서 고유 스킬 목록 추출
- 직군별 CSV 파일들에서 각 구인공고별 스킬 추출
- 구인공고(직군명 포함)-스킬 bipartite network .net 파일 생성
"""

import pandas as pd
import os
import re
import math

def load_unique_skills(skill_edges_file):
    """data_bipartite_skill_edges.csv에서 고유 스킬 목록을 추출합니다."""
    print(f"[1단계] 고유 스킬 목록 추출: {skill_edges_file}")
    
    if not os.path.exists(skill_edges_file):
        print(f"경고: {skill_edges_file} 파일을 찾을 수 없습니다.")
        return []
    
    df = pd.read_csv(skill_edges_file, encoding='utf-8-sig')
    unique_skills = sorted(df['Skill'].unique().tolist())
    
    print(f"  추출된 고유 스킬 수: {len(unique_skills)}개")
    return unique_skills


def extract_skills_from_text(text, skill_list):
    """텍스트에서 스킬을 추출합니다."""
    if pd.isna(text) or not text:
        return set()
    
    text_str = str(text).upper()
    found_skills = set()
    
    # 스킬 목록을 길이 순으로 정렬 (긴 것부터 매칭하여 부분 문자열 문제 방지)
    sorted_skills = sorted(skill_list, key=len, reverse=True)
    
    for skill in sorted_skills:
        # 대소문자 구분 없이 매칭
        skill_upper = skill.upper()
        if skill_upper in text_str:
            # 단어 경계 확인 (부분 문자열이 아닌 실제 단어인지)
            pattern = r'\b' + re.escape(skill_upper) + r'\b'
            if re.search(pattern, text_str, re.IGNORECASE):
                found_skills.add(skill)
    
    return found_skills


def load_job_postings(job_csv_dir):
    """직군별 CSV 파일들에서 구인공고 데이터를 로드합니다."""
    print(f"\n[2단계] 구인공고 데이터 로드: {job_csv_dir}")
    
    all_postings = []
    csv_files = [
        'BI 엔지니어.csv',
        'DBA.csv',
        '데이터 분석가.csv',
        '데이터 사이언티스트.csv',
        '데이터 엔지니어.csv',
        '머신러닝 엔지니어.csv',
        '빅데이터 엔지니어.csv',
        '프로덕트 매니저.csv'
    ]
    
    for csv_file in csv_files:
        file_path = os.path.join(job_csv_dir, csv_file)
        if not os.path.exists(file_path):
            print(f"  경고: {file_path} 파일을 찾을 수 없습니다.")
            continue
        
        print(f"  로딩 중: {csv_file}")
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        print(f"    로드된 공고 수: {len(df)}개")
        
        # 직군명 추출 (파일명에서 .csv 제거)
        job_type = csv_file.replace('.csv', '')
        
        for idx, row in df.iterrows():
            posting = {
                'job_id': f"{job_type}_{idx + 1}",
                'job_type': job_type,
                'company': str(row['기업명']).strip() if '기업명' in row else '',
                'job_description': str(row.get('주요업무', '')),
                'requirements': str(row.get('자격요건', '')),
                'preferences': str(row.get('우대사항', ''))
            }
            all_postings.append(posting)
    
    print(f"\n  총 구인공고 수: {len(all_postings)}개")
    return all_postings


def create_job_skill_edges(postings, skill_list):
    """구인공고-스킬 엣지를 생성합니다."""
    print(f"\n[3단계] 구인공고별 스킬 추출 중...")
    
    job_skill_edges = []
    
    for posting in postings:
        # 자격요건과 우대사항에서 스킬 추출
        all_text = f"{posting['requirements']} {posting['preferences']}"
        skills = extract_skills_from_text(all_text, skill_list)
        
        for skill in skills:
            job_skill_edges.append({
                'job_id': posting['job_id'],
                'job_type': posting['job_type'],
                'company': posting['company'],
                'skill': skill
            })
    
    print(f"  생성된 구인공고-스킬 엣지 수: {len(job_skill_edges)}개")
    return job_skill_edges


def create_pajek_network(job_skill_edges, all_skills_list, output_file):
    """Pajek 형식의 bipartite 네트워크 파일을 생성합니다.
    
    Args:
        job_skill_edges: 구인공고-스킬 엣지 리스트
        all_skills_list: 모든 스킬 목록 (data_bipartite_skill_edges.csv의 전체 스킬)
        output_file: 출력 파일 경로
    """
    print(f"\n[4단계] Pajek 네트워크 파일 생성: {output_file}")
    
    # 고유 구인공고 ID 추출
    job_ids = sorted(set(edge['job_id'] for edge in job_skill_edges))
    
    # 모든 스킬 목록 사용 (엣지에 나타난 스킬만이 아니라 전체 스킬 목록)
    skills = sorted(all_skills_list)
    
    n_jobs = len(job_ids)
    n_skills = len(skills)
    total_nodes = n_jobs + n_skills
    
    print(f"  구인공고 수 (Mode 1): {n_jobs}개")
    print(f"  스킬 수 (Mode 2): {n_skills}개")
    print(f"  총 노드 수: {total_nodes}개")
    
    # ID 매핑 생성
    job_id_to_num = {job_id: idx + 1 for idx, job_id in enumerate(job_ids)}
    skill_to_num = {skill: idx + n_jobs + 1 for idx, skill in enumerate(skills)}
    
    # 엣지 집계 (중복 제거)
    edges_set = set()
    for edge in job_skill_edges:
        job_num = job_id_to_num[edge['job_id']]
        skill_num = skill_to_num[edge['skill']]
        edges_set.add((job_num, skill_num))
    
    print(f"  총 엣지 수: {len(edges_set)}개")
    
    # Pajek 파일 작성
    with open(output_file, 'w', encoding='utf-8') as f:
        # 헤더: *Vertices total_count first_mode_count
        f.write(f"*Vertices {total_nodes} {n_jobs}\n")
        
        # 구인공고 노드 (Mode 1) - 직군명 포함
        for job_id in job_ids:
            job_num = job_id_to_num[job_id]
            f.write(f'{job_num} "{job_id}" 0.0000 0.0000 0.5000\n')
        
        # 스킬 노드 (Mode 2)
        for skill in skills:
            skill_num = skill_to_num[skill]
            # 좌표 계산 (원형 배치)
            angle = 2 * math.pi * (skill_num - n_jobs - 1) / n_skills
            x = 0.5 + 0.3 * math.cos(angle)
            y = 0.5 + 0.3 * math.sin(angle)
            f.write(f'{skill_num} "{skill}" {x:.4f} {y:.4f} 0.5000\n')
        
        # 엣지
        f.write("*Arcs\n")
        f.write("*Edges\n")
        for job_num, skill_num in sorted(edges_set):
            f.write(f"{job_num} {skill_num} 1\n")
    
    print(f"  파일 생성 완료: {output_file}")


def main():
    """메인 함수"""
    print("=" * 70)
    print("구인공고-스킬 Bipartite Network 생성")
    print("=" * 70)
    
    # 현재 스크립트 위치 기준으로 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)  # 데이터관련_raw 폴더
    
    # 파일 경로 설정
    skill_edges_file = os.path.join(parent_dir, 'data_bipartite_skill_edges.csv')
    job_csv_dir = os.path.join(parent_dir, '직군별데이터_raw')
    output_file = os.path.join(script_dir, 'job_skill_bipartite_2mode.net')
    csv_output_file = os.path.join(script_dir, 'job_skill_bipartite_edges.csv')
    
    # 1단계: 고유 스킬 목록 추출
    unique_skills = load_unique_skills(skill_edges_file)
    
    if not unique_skills:
        print("오류: 스킬 목록을 추출할 수 없습니다.")
        return
    
    # 2단계: 구인공고 데이터 로드
    postings = load_job_postings(job_csv_dir)
    
    if not postings:
        print("오류: 구인공고 데이터를 로드할 수 없습니다.")
        return
    
    # 3단계: 구인공고-스킬 엣지 생성
    job_skill_edges = create_job_skill_edges(postings, unique_skills)
    
    # CSV 파일로 저장 (참고용)
    if job_skill_edges:
        df_edges = pd.DataFrame(job_skill_edges)
        df_edges.to_csv(csv_output_file, index=False, encoding='utf-8-sig')
        print(f"\nCSV 파일 저장 완료: {csv_output_file}")
    
    # 4단계: Pajek 네트워크 파일 생성
    if job_skill_edges:
        create_pajek_network(job_skill_edges, unique_skills, output_file)
    
    print("\n" + "=" * 70)
    print("작업 완료!")
    print("=" * 70)


if __name__ == '__main__':
    main()

