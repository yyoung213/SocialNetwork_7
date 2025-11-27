import pandas as pd
import os
from collections import defaultdict
from typing import Dict, List, Set
import DataPreprocessing as dp

def load_csv_data(file_path: str) -> pd.DataFrame:
    """CSV 파일에서 데이터 로드"""
    try:
        # UTF-8로 먼저 시도
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        # UTF-8 실패 시 CP949 시도
        try:
            df = pd.read_csv(file_path, encoding='cp949')
        except:
            # 마지막으로 latin-1 시도
            df = pd.read_csv(file_path, encoding='latin-1')
    return df

def process_all_jobs(raw_data_dir: str = 'raw_data') -> Dict[str, pd.DataFrame]:
    """모든 직무별 파일에 대해 키워드 사전 생성"""
    job_dictionaries = {}
    
    # raw_data 폴더의 모든 CSV 파일 찾기
    csv_files = [f for f in os.listdir(raw_data_dir) if f.endswith('.csv')]
    
    print(f"총 {len(csv_files)}개 직무 파일 발견\n")
    
    for idx, csv_file in enumerate(csv_files, 1):
        file_path = os.path.join(raw_data_dir, csv_file)
        job_name = csv_file.replace('.csv', '')
        
        print(f"[{idx}/{len(csv_files)}] 처리 중: {job_name}")
        
        try:
            # CSV 파일 로드
            df = load_csv_data(file_path)
            print(f"  - 로드된 데이터: {df.shape[0]}개 행")
            
            # 키워드 사전 생성
            keyword_dict = dp.create_keyword_dictionary(df)
            job_dictionaries[job_name] = keyword_dict
            
            print(f"  - 추출된 키워드 수: {len(keyword_dict)}개")
            print(f"  ✓ 완료\n")
            
        except Exception as e:
            print(f"  ⚠ 오류 발생: {e}\n")
            continue
    
    return job_dictionaries

def merge_keyword_dictionaries_simple(job_dictionaries: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """여러 직무의 키워드 사전을 단순 통합 (중복 키워드 제거, 표현 축적)"""
    
    # 통합된 키워드 사전: {keyword: set of expressions}
    merged_dict = defaultdict(set)
    
    # 각 직무별 사전에서 키워드와 표현 수집
    for job_name, keyword_df in job_dictionaries.items():
        for _, row in keyword_df.iterrows():
            keyword = row['Keyword']
            expressions_str = row['Expressions']
            
            # Expressions 문자열을 개별 표현으로 분리
            expressions = [expr.strip() for expr in expressions_str.split(',') if expr.strip()]
            
            # 통합 사전에 추가 (같은 키워드면 표현만 축적)
            merged_dict[keyword].update(expressions)
    
    # 결과 데이터프레임 생성
    result_data = []
    for keyword in sorted(merged_dict.keys()):
        expressions = sorted(list(merged_dict[keyword]))
        expressions_str = ', '.join(expressions)
        
        result_data.append({
            'Keyword': keyword,
            'Expressions': expressions_str
        })
    
    result_df = pd.DataFrame(result_data)
    return result_df

def main():
    """메인 함수"""
    print("="*60)
    print("통합 키워드 사전 구축")
    print("="*60)
    
    # 1. 모든 직무별 키워드 사전 생성
    job_dictionaries = process_all_jobs('raw_data')
    
    print(f"\n총 {len(job_dictionaries)}개 직무의 키워드 사전 생성 완료\n")
    
    # 2. 키워드 사전 단순 통합 (중복 제거, 표현 축적)   
    print("="*60)
    print("키워드 사전 단순 통합 중 (중복 제거, 표현 축적)...")
    print("="*60)
    
    new_merged_dictionary = merge_keyword_dictionaries_simple(job_dictionaries)
    
    print(f"\n통합된 키워드 수: {len(new_merged_dictionary)}개")
    print("\n샘플 결과 (처음 20개):")
    print(new_merged_dictionary.head(20).to_string(index=False))
    
    # 3. 엑셀 파일로 저장
    new_output_file = 'New_필수역량_키워드_사전.xlsx'
    new_merged_dictionary.to_excel(new_output_file, index=False, engine='openpyxl')
    print(f"\n✓ 새로운 통합 키워드 사전이 '{new_output_file}'에 저장되었습니다.")
    
    # 4. 각 직무별 사전도 저장 (선택사항)
    output_dir = '직무별_키워드_사전'
    os.makedirs(output_dir, exist_ok=True)
    
    for job_name, keyword_df in job_dictionaries.items():
        job_output_file = os.path.join(output_dir, f'{job_name}_키워드_사전.xlsx')
        keyword_df.to_excel(job_output_file, index=False, engine='openpyxl')
    
    print(f"✓ 각 직무별 키워드 사전이 '{output_dir}' 폴더에 저장되었습니다.")
    
    return new_merged_dictionary, job_dictionaries

if __name__ == "__main__":
    merged_dict, job_dicts = main()

