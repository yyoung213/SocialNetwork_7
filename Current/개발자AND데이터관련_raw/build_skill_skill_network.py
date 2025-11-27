"""
Skill-Skill Network Builder
data&developer_bipartite_skill_edges.csv를 기반으로 스킬 간 co-occurrence 네트워크를 구축합니다.
"""

import pandas as pd
from collections import defaultdict, Counter
from itertools import combinations
import os


def load_skill_edges(csv_file: str = 'data&developer_bipartite_skill_edges.csv'):
    """
    CSV 파일에서 기업명별 스킬 리스트를 추출합니다.
    
    Args:
        csv_file (str): 입력 CSV 파일 경로
        
    Returns:
        dict: {기업명: [skill1, skill2, ...]} 형태의 딕셔너리
    """
    print(f"데이터 파일 로딩 중: {csv_file}")
    
    # CSV 파일 읽기
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    print(f"  로드된 행 수: {len(df)}개")
    
    # 기업명별로 스킬 그룹화
    company_skills = defaultdict(set)
    
    for _, row in df.iterrows():
        company = str(row['기업명']).strip()
        skill = str(row['Skill']).strip()
        
        if company and skill:
            company_skills[company].add(skill)
    
    # set을 list로 변환
    company_skills_list = {company: sorted(list(skills)) 
                          for company, skills in company_skills.items()}
    
    print(f"  총 구인공고 수: {len(company_skills_list)}개")
    
    # 스킬 통계
    all_skills = set()
    for skills in company_skills_list.values():
        all_skills.update(skills)
    print(f"  총 고유 스킬 수: {len(all_skills)}개")
    
    return company_skills_list


def calculate_cooccurrence(company_skills: dict):
    """
    구인공고별 스킬 쌍의 co-occurrence 빈도를 계산합니다.
    
    Args:
        company_skills (dict): {기업명: [skill1, skill2, ...]} 형태의 딕셔너리
        
    Returns:
        Counter: {(skill1, skill2): count} 형태의 Counter 객체
    """
    print("\n스킬 쌍 co-occurrence 계산 중...")
    
    cooccurrence = Counter()
    
    for company, skills in company_skills.items():
        # 각 구인공고에서 스킬 쌍 생성 (조합)
        # 같은 구인공고에 등장한 스킬들 간의 모든 쌍 생성
        skill_pairs = list(combinations(sorted(skills), 2))
        
        for skill1, skill2 in skill_pairs:
            # 정렬된 쌍으로 저장 (무방향 그래프)
            cooccurrence[(skill1, skill2)] += 1
    
    print(f"  총 스킬 쌍 수: {len(cooccurrence)}개")
    print(f"  최대 co-occurrence: {max(cooccurrence.values()) if cooccurrence else 0}")
    
    return cooccurrence


def build_network_and_save(cooccurrence: Counter, output_file: str = 'skill_skill_network.net'):
    """
    Co-occurrence 데이터를 기반으로 네트워크를 구축하고 Pajek .net 형식으로 저장합니다.
    
    Args:
        cooccurrence (Counter): {(skill1, skill2): count} 형태의 Counter 객체
        output_file (str): 출력 .net 파일 경로
    """
    print(f"\n네트워크 구축 및 저장 중: {output_file}")
    
    # 모든 고유 스킬 추출
    all_skills = set()
    for (skill1, skill2), count in cooccurrence.items():
        all_skills.add(skill1)
        all_skills.add(skill2)
    
    sorted_skills = sorted(all_skills)
    node_to_id = {skill: idx + 1 for idx, skill in enumerate(sorted_skills)}
    
    print(f"  노드 수: {len(sorted_skills)}개")
    print(f"  엣지 수: {len(cooccurrence)}개")
    
    # Pajek .net 형식으로 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        # Vertices 섹션
        f.write(f"*Vertices {len(sorted_skills)}\n")
        for skill in sorted_skills:
            node_id = node_to_id[skill]
            # Pajek 형식: id "label" (따옴표 안의 따옴표는 이스케이프)
            label_escaped = skill.replace('"', '\\"')
            f.write(f'{node_id} "{label_escaped}"\n')
        
        # Edges 섹션 (무방향 그래프이므로 *Edges 사용)
        f.write(f"*Edges\n")
        # 정렬된 순서로 엣지 저장
        for (skill1, skill2), weight in sorted(cooccurrence.items()):
            u_id = node_to_id[skill1]
            v_id = node_to_id[skill2]
            f.write(f"{u_id} {v_id} {weight}\n")
    
    print(f"  ✓ 저장 완료: {output_file}")
    
    # 통계 출력
    weights = list(cooccurrence.values())
    if weights:
        print(f"\n네트워크 통계:")
        print(f"  평균 가중치: {sum(weights) / len(weights):.2f}")
        print(f"  최소 가중치: {min(weights)}")
        print(f"  최대 가중치: {max(weights)}")


def main():
    """메인 함수"""
    print("="*60)
    print("Skill-Skill Network Builder (개발자+데이터 통합)")
    print("="*60)
    
    # 현재 스크립트가 있는 디렉토리로 이동
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 1. 데이터 로딩
    csv_file = 'data&developer_bipartite_skill_edges.csv'
    if not os.path.exists(csv_file):
        print(f"오류: '{csv_file}' 파일을 찾을 수 없습니다.")
        return
    
    company_skills = load_skill_edges(csv_file)
    
    # 2. Co-occurrence 계산
    cooccurrence = calculate_cooccurrence(company_skills)
    
    # 3. 네트워크 구축 및 저장
    output_file = 'skill_skill_network.net'
    build_network_and_save(cooccurrence, output_file)
    
    print("\n" + "="*60)
    print("완료!")
    print("="*60)


if __name__ == "__main__":
    main()

