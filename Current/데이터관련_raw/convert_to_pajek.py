import csv
import math

# Read CSV file
csv_file = 'data_bipartite_skill_edges.csv'
net_file = 'data_bipartite_skill_2mode.net'

# Collect all edges and unique nodes
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

# Create mappings
company_to_id = {comp: idx + 1 for idx, comp in enumerate(companies)}
skill_to_id = {skill: idx + len(companies) + 1 for idx, skill in enumerate(skills)}

# Write Pajek file
with open(net_file, 'w', encoding='utf-8') as f:
    # Header: *Vertices total_count first_mode_count
    total_vertices = len(companies) + len(skills)
    first_mode_count = len(companies)
    f.write(f'*Vertices    {total_vertices}    {first_mode_count}\n')
    
    # Write company vertices (first mode)
    for idx, company in enumerate(companies, 1):
        # Generate coordinates (simple layout)
        x = (idx - 1) % 10 / 10.0
        y = (idx - 1) // 10 / 10.0
        z = 0.5
        # Format to match example: pad name to ~40 characters
        name_padded = f'"{company}"'.ljust(40)
        f.write(f'{idx:7d} {name_padded}{x:.4f}    {y:.4f}    {z:.4f}\n')
    
    # Write skill vertices (second mode)
    for idx, skill in enumerate(skills, 1):
        vertex_id = len(companies) + idx
        # Generate coordinates (simple layout)
        x = (idx - 1) % 10 / 10.0
        y = (idx - 1) // 10 / 10.0
        z = 0.5
        # Format to match example: pad name to ~40 characters
        name_padded = f'"{skill}"'.ljust(40)
        f.write(f'{vertex_id:7d} {name_padded}{x:.4f}    {y:.4f}    {z:.4f}\n')
    
    # Write edges section
    f.write('*Arcs\n')
    f.write('*Edges\n')
    
    # Write edges (company to skill)
    for company, skill in edges:
        company_id = company_to_id[company]
        skill_id = skill_to_id[skill]
        f.write(f'{company_id:7d}    {skill_id:7d}       1\n')

print(f'Conversion complete!')
print(f'Total companies: {len(companies)}')
print(f'Total skills: {len(skills)}')
print(f'Total edges: {len(edges)}')
print(f'Output file: {net_file}')

