import os

BASE = "/Users/prh/Vault/Projects/Writing/Raise'm Right/research"
folders = ['0-12', '13-24', '25-36', '13-36-months', '132-144']

# Original non-PMC files to keep (by folder)
KEEP_ORIGINAL = {
    '0-12': ['01-NIH-MedlinePlus-Infant-Newborn-Development.md',
             '02-Harvard-Brain-Architecture.md', '03-NHS-Baby-Development.md',
             '04-WHO-Infant-Feeding.md', '05-CDC-Essentials-Parenting.md',
             '06-UNICEF-Developmental-Milestones.md'],
    '13-24': [],
    '25-36': [],
    '13-36-months': [
        "D'Cruz_2024_Physical_Activity_Sleep_Emotion_Self_Regulation.md",
        'Eisenberg_1998_Parental_Socialization_Emotion.md',
        'Gross_2015_Toddler_Social_Understanding_Prosocial.md',
        'Horm_2024_Resilience_Self_Regulation_Toddlers.md',
        'Kiel_2016_Maternal_Encouragement_Toddler_Anxiety.md',
        'Maag_2021_Toddler_Dysregulated_Fear_Anxiety.md',
        'Oxford_2013_Separation_Distress_Maltreated_Toddlers.md',
        'Spinrad_2007_Toddler_Effortful_Control_Social_Competence.md',
    ],
    '132-144': [],
}

for d in folders:
    path = os.path.join(BASE, d)
    keep_set = set(KEEP_ORIGINAL.get(d, []))
    for f in sorted(os.listdir(path)):
        fp = os.path.join(path, f)
        if not f.endswith('.md'):
            continue
        if f.startswith('PMC'):
            continue  # keep all PMC-named files
        if f in keep_set:
            continue  # keep original non-PMC files
        os.remove(fp)
        print(f'REMOVED: {d}/{f}')

print('\nDone cleaning.')

# Print final counts
for d in folders:
    path = os.path.join(BASE, d)
    mds = [f for f in os.listdir(path) if f.endswith('.md')]
    print(f'{d}: {len(mds)} .md files')
    for f in sorted(mds):
        print(f'  {f}')
    print()
