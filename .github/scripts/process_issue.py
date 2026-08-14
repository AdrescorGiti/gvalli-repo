import json
import os
import re
import hashlib
import subprocess

# 1. Чтение события GitHub
event_path = os.environ.get('GITHUB_EVENT_PATH')
if not event_path or not os.path.exists(event_path):
    print("Error: GITHUB_EVENT_PATH not found.")
    exit(1)

with open(event_path, 'r', encoding='utf-8') as f:
    event = json.load(f)

issue = event.get('issue', {})
title = issue.get('title', '')
body = issue.get('body', '')
issue_author = issue.get('user', {}).get('login', '')

# Проверка метки пакета в заголовке
if '[Package]' not in title:
    print('Not a package submission. Skipping.')
    with open(os.environ['GITHUB_ENV'], 'a', encoding='utf-8') as f:
        f.write('IS_PACKAGE=false\n')
    exit(0)

# 2. Парсинг формы Issue
sections = re.split(r'###\s+', body)
data = {}
for sec in sections:
    if not sec.strip():
        continue
    lines = sec.strip().split('\n')
    data[lines[0].strip()] = '\n'.join(lines[1:]).strip()

name = data.get('Package Name', '').strip()
version = data.get('Version', '').strip()
description = data.get('Description', '').strip()
url = data.get('Direct Download URL (.gpkg)', '').strip()

deps_raw = data.get('Dependencies', '').strip()
dependencies = [
    d.strip() for d in re.split(r'[,;\s]+', deps_raw) if d.strip()
] if deps_raw and deps_raw.lower() not in ['none', '_no response_'] else []

if not name or not url:
    print('Error: Missing required fields (Name or URL).')
    with open(os.environ['GITHUB_ENV'], 'a', encoding='utf-8') as f:
        f.write('IS_PACKAGE=false\n')
    exit(0)

# Определение файла базы
json_file = 'packages.json' if os.path.exists('packages.json') else 'pakages.json' if os.path.exists('pakages.json') else 'packages.json'
pkg_data = {'packages': []}

if os.path.exists(json_file) and os.path.getsize(json_file) > 0:
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
            if isinstance(loaded, dict) and 'packages' in loaded:
                pkg_data = loaded
            elif isinstance(loaded, list):
                pkg_data = {'packages': loaded}
    except Exception as e:
        print(f'Warning: JSON read error ({e}). Initializing empty list.')

# 3. Проверка прав создателя пакета
existing_pkg = next((p for p in pkg_data.get('packages', []) if p.get('name') == name), None)
if existing_pkg:
    original_creator = existing_pkg.get('creator', '')
    if original_creator and original_creator.lower() != issue_author.lower():
        print(f'Unauthorized attempt by @{issue_author}')
        with open(os.environ['GITHUB_ENV'], 'a', encoding='utf-8') as f:
            f.write('IS_PACKAGE=true\nUNAUTHORIZED=true\n')
            f.write(f'PKG_NAME={name}\nORIGINAL_CREATOR={original_creator}\n')
        exit(0)

# 4. Скачивание пакета для вычисления SHA256
print(f"Downloading {url} via curl...")
curl_cmd = [
    "curl", "-sSLf", 
    "-A", "Mozilla/5.0 (X11; Linux x86_64)", 
    "-o", "package.gpkg", 
    url
]
res = subprocess.run(curl_cmd, capture_output=True)

if res.returncode != 0 or not os.path.exists('package.gpkg') or os.path.getsize('package.gpkg') == 0:
    print(f"Failed to download package from {url}")
    with open(os.environ['GITHUB_ENV'], 'a', encoding='utf-8') as f:
        f.write('IS_PACKAGE=false\n')
    exit(0)

# 5. Расчет SHA256 хеша
hasher = hashlib.sha256()
with open('package.gpkg', 'rb') as f:
    while chunk := f.read(8192):
        hasher.update(chunk)
sha256 = hasher.hexdigest()
print(f"Calculated SHA256: {sha256}")

# 6. Обновление JSON
creator_name = existing_pkg.get('creator', issue_author) if existing_pkg else issue_author

# Удаляем старую запись, если обновляем
pkg_data['packages'] = [p for p in pkg_data.get('packages', []) if p.get('name') != name]

# Добавляем обновленный/новый пакет
pkg_data['packages'].append({
    'name': name,
    'version': version,
    'description': description,
    'creator': creator_name,
    'dependencies': dependencies,
    'url': url,
    'sha256': sha256
})

# Запись в файл
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(pkg_data, f, indent=2, ensure_ascii=False)

# 7. Экспорт переменных окружения для GitHub Action
with open(os.environ['GITHUB_ENV'], 'a', encoding='utf-8') as f:
    f.write('IS_PACKAGE=true\n')
    f.write('UNAUTHORIZED=false\n')
    f.write(f'PKG_NAME={name}\n')
    f.write(f'PKG_SHA256={sha256}\n')
    f.write(f'TARGET_JSON={json_file}\n')

print(f"Successfully processed {name} ({sha256}) -> {json_file}")
