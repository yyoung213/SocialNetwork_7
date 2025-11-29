"""
직군별데이터_raw 폴더의 각 CSV 파일별 샘플 개수 확인
"""

import pandas as pd
import os
from pathlib import Path

def count_samples_by_job_type():
    """직군별 CSV 파일의 샘플 개수를 확인합니다."""
    print("=" * 70)
    print("직군별 데이터셋 샘플 개수 확인")
    print("=" * 70)
    
    # 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    job_csv_dir = os.path.join(os.path.dirname(script_dir), '직군별데이터_raw')
    
    # CSV 파일 목록
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
    
    results = []
    total_samples = 0
    
    print(f"\n직군별 데이터셋 샘플 개수:\n")
    print(f"{'직군':<20} {'샘플 개수':>12} {'비율':>10}")
    print("-" * 45)
    
    for csv_file in csv_files:
        file_path = os.path.join(job_csv_dir, csv_file)
        if not os.path.exists(file_path):
            print(f"{csv_file.replace('.csv', ''):<20} {'파일 없음':>12}")
            continue
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            sample_count = len(df)
            job_type = csv_file.replace('.csv', '')
            results.append({
                '직군': job_type,
                '샘플 개수': sample_count
            })
            total_samples += sample_count
        except Exception as e:
            print(f"{csv_file.replace('.csv', ''):<20} {'오류':>12} - {e}")
            continue
    
    # 비율 계산 및 출력
    for result in results:
        ratio = (result['샘플 개수'] / total_samples * 100) if total_samples > 0 else 0
        print(f"{result['직군']:<20} {result['샘플 개수']:>12,} {ratio:>9.2f}%")
    
    print("-" * 45)
    print(f"{'총계':<20} {total_samples:>12,} {'100.00%':>10}")
    
    # 표 형식으로도 출력
    print("\n" + "=" * 70)
    print("표 형식 요약:")
    print("=" * 70)
    print("\n| 직군 | 샘플 개수 | 비율 (%) |")
    print("|------|----------|---------|")
    
    for result in sorted(results, key=lambda x: x['샘플 개수'], reverse=True):
        ratio = (result['샘플 개수'] / total_samples * 100) if total_samples > 0 else 0
        print(f"| {result['직군']} | {result['샘플 개수']:,} | {ratio:.2f}% |")
    
    print(f"| **총계** | **{total_samples:,}** | **100.00%** |")
    
    return results, total_samples


if __name__ == '__main__':
    results, total = count_samples_by_job_type()
    print(f"\n총 {len(results)}개 직군 데이터셋, 총 {total:,}개 샘플")

