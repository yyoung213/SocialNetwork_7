"""
bipartite_skill_wide.csv 데이터셋에서 모든 고유한 스킬을 추출하는 스크립트
"""

import pandas as pd
import ast
from collections import Counter


def extract_unique_skills(csv_file='bipartite_skill_wide.csv'):
    """
    CSV 파일에서 모든 고유한 스킬을 추출합니다.
    
    Args:
        csv_file (str): 읽을 CSV 파일 경로
        
    Returns:
        list: 정렬된 고유 스킬 목록
    """
    # CSV 파일 읽기
    df = pd.read_csv(csv_file)
    
    # 모든 고유한 스킬을 저장할 집합
    all_skills = set()
    
    # Skills_List 컬럼에서 스킬 추출
    for idx, row in df.iterrows():
        skills_list_str = row['Skills_List']
        
        # 문자열을 리스트로 변환 (ast.literal_eval 사용)
        try:
            skills_list = ast.literal_eval(skills_list_str)
            # 각 스킬을 집합에 추가
            for skill in skills_list:
                all_skills.add(skill.strip())  # 공백 제거 후 추가
        except (ValueError, SyntaxError) as e:
            print(f"Row {idx} 파싱 오류: {skills_list_str}")
            continue
    
    # 고유한 스킬들을 정렬된 리스트로 변환
    unique_skills = sorted(list(all_skills))
    
    return unique_skills


def get_skill_frequency(csv_file='bipartite_skill_wide.csv'):
    """
    스킬별 출현 빈도를 계산합니다.
    
    Args:
        csv_file (str): 읽을 CSV 파일 경로
        
    Returns:
        list: (스킬명, 출현횟수) 튜플의 리스트 (빈도순 정렬)
    """
    df = pd.read_csv(csv_file)
    
    skill_counts = Counter()
    for idx, row in df.iterrows():
        skills_list_str = row['Skills_List']
        try:
            skills_list = ast.literal_eval(skills_list_str)
            for skill in skills_list:
                skill_counts[skill.strip()] += 1
        except (ValueError, SyntaxError):
            continue
    
    # 빈도순으로 정렬
    return skill_counts.most_common()


def save_skills_to_file(unique_skills, filename='unique_skills_list.txt'):
    """
    고유 스킬 목록을 파일로 저장합니다.
    
    Args:
        unique_skills (list): 고유 스킬 목록
        filename (str): 저장할 파일명
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"총 고유 스킬 개수: {len(unique_skills)}\n\n")
        for i, skill in enumerate(unique_skills, 1):
            f.write(f"{i}. {skill}\n")


def main():
    """메인 실행 함수"""
    # 고유 스킬 추출
    unique_skills = extract_unique_skills()
    
    # 결과 출력
    print(f"총 고유 스킬 개수: {len(unique_skills)}")
    print("\n=== 모든 고유 스킬 목록 ===")
    for i, skill in enumerate(unique_skills, 1):
        print(f"{i}. {skill}")
    
    # 스킬별 출현 빈도 계산 및 출력
    skill_frequency = get_skill_frequency()
    print("\n=== 스킬별 출현 빈도 (상위 20개) ===")
    for skill, count in skill_frequency[:20]:
        print(f"{skill}: {count}회")
    
    # 파일로 저장
    save_skills_to_file(unique_skills)
    print(f"\n고유 스킬 목록이 'unique_skills_list.txt' 파일에 저장되었습니다.")
    
    return unique_skills


# 스크립트 실행 시 메인 함수 호출
if __name__ == "__main__":
    # 모든 고유 스킬 목록을 변수로 저장
    ALL_UNIQUE_SKILLS = main()
    
    # 다른 스크립트에서 import하여 사용할 수 있도록 export
    # 예: from DataProcessing import ALL_UNIQUE_SKILLS
