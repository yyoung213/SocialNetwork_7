"""개발관련_raw: Bipartite 네트워크를 Pajek 형식으로 변환"""
import csv

csv_file = 'developer_bipartite_skill_edges.csv'
net_file = 'developer_bipartite_skill_2mode.net'

companies = []
skills = []
edges = []

with open(csv_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        company = row['기업명'].strip()
        skill = row['Skill'].strip()
        
        if company not in companies:
            companies.append(company)
        if skill not in skills:
            skills.append(skill)
        
        edges.append((company, skill))

company_to_id = {comp: idx + 1 for idx, comp in enumerate(companies)}
skill_to_id = {skill: idx + len(companies) + 1 for idx, skill in enumerate(skills)}

with open(net_file, 'w', encoding='utf-8') as f:
    total_vertices = len(companies) + len(skills)
    first_mode_count = len(companies)
    f.write(f'*Vertices    {total_vertices}    {first_mode_count}\n')
    
    for idx, company in enumerate(companies, 1):
        x = (idx - 1) % 10 / 10.0
        y = (idx - 1) // 10 / 10.0
        z = 0.5
        name_padded = f'"{company}"'.ljust(40)
        f.write(f'{idx:7d} {name_padded}{x:.4f}    {y:.4f}    {z:.4f}\n')
    
    for idx, skill in enumerate(skills, 1):
        vertex_id = len(companies) + idx
        x = (idx - 1) % 10 / 10.0
        y = (idx - 1) // 10 / 10.0
        z = 0.5
        name_padded = f'"{skill}"'.ljust(40)
        f.write(f'{vertex_id:7d} {name_padded}{x:.4f}    {y:.4f}    {z:.4f}\n')
    
    f.write('*Arcs\n')
    f.write('*Edges\n')
    
    for company, skill in edges:
        company_id = company_to_id[company]
        skill_id = skill_to_id[skill]
        f.write(f'{company_id:7d}    {skill_id:7d}       1\n')

print(f'변환 완료!')
print(f'총 기업 수: {len(companies)}')
print(f'총 스킬 수: {len(skills)}')
print(f'총 엣지 수: {len(edges)}')
print(f'출력 파일: {net_file}')



