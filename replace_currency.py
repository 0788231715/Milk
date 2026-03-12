import os
import re

path = 'backend/templates'
for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith('.html'):
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Pattern 1: $ followed by {{ (Django template variable)
            # Pattern 2: $ followed by a digit
            # We avoid matching ${ which is JS template literal
            
            new_content = re.sub(r'\$(?=\{\{)', 'RWF ', content)
            new_content = re.sub(r'\$([0-9])', r'RWF \1', new_content)
            
            if content != new_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Updated {file_path}')
