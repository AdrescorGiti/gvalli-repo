import json, os, re, hashlib, subprocess, shutil

# 1. Чтение события GitHub
event_path = os.environ['GITHUB_EVENT_PATH']
with open(event_path, 'r', encoding='utf-8') as f:
    event = json.load(f)

issue = event.get('issue', {})
title = issue.get('title', '')
body = issue.get('body', '')
issue_author = issue.get('user', {}).get('login', '')

if '[Package]' not in title:
    print('Not a package submission. Skipping.')
    with open(os.environ['GITHUB_ENV'], 'a', encoding='utf-8') as f:
        f.write('IS_PACKAGE=false\n')
    exit(0)

# Парсинг формы Issue
sections = re.split(r'###\s+', body)
data = {}
for sec in sections:
    if not sec.strip(): continue
    lines = sec.strip().split('\n')
    data[lines[0].strip()] = '\n'.join(lines[1:]).strip()

name = data.get('Package Name', '').strip()
version = data.get('Version', '').strip()
description = data.get('Description', '').strip()
url = data.get('Direct Download URL (.gpkg)', '').strip()

deps_raw = data.get('Dependencies', '').strip()
dependencies = [d.strip() for d in re.split(r'[,;\s]+', deps_raw) if d.strip()] if deps_raw and deps_raw.lower() not in ['none', '_no response_'] else []

if not name or not url:
    print('Error: Missing required fields.')
    with open(os.environ['GITHUB_ENV'], 'a', encoding='utf-8') as f:
        f.write('IS_PACKAGE=true\nUNAUTHORIZED=false\nMALWARE=true\n')
        f.write(f'PKG_NAME={name or "Unknown"}\nMALWARE_REASON=Заполнены не все обязательные поля.\n')
    exit(0)

# Поиск индексного файла
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
        print(f'Warning: JSON read error ({e}).')

# 2. ПРОВЕРКА ПРАВ
existing_pkg = next((p for p in pkg_data.get('packages', []) if p.get('name') == name), None)
if existing_pkg:
    original_creator = existing_pkg.get('creator', '')
    if original_creator and original_creator.lower() != issue_author.lower():
        print(f'Unauthorized attempt by @{issue_author}')
        with open(os.environ['GITHUB_ENV'], 'a', encoding='utf-8') as f:
            f.write('IS_PACKAGE=true\nUNAUTHORIZED=true\nMALWARE=false\n')
            f.write(f'PKG_NAME={name}\nORIGINAL_CREATOR={original_creator}\n')
        exit(0)

# 3. УСТАНОВКА ИНСТРУМЕНТОВ (GVALLI И VTEST)
print("Подготовка окружения (zstd)...")
subprocess.run(["sudo", "apt-get", "update"], capture_output=True)
subprocess.run(["sudo", "apt-get", "install", "-y", "zstd"], capture_output=True)

print("Скачивание и распаковка GValli...")
subprocess.run(["curl", "-sSLf", "-o", "gvalli.pkg.tar.zst", "https://github.com/AdrescorGiti/gvalli-repo/raw/refs/heads/main/gvalli-0.5.0-1-x86_64.pkg.tar.zst"])
subprocess.run(["sudo", "tar", "-I", "zstd", "-xf", "gvalli.pkg.tar.zst", "-C", "/"])

print("Скачивание и установка vtest через GValli...")
subprocess.run(["curl", "-sSLf", "-o", "vtest.gpkg", "https://github.com/AdrescorGiti/gvalli-repo/raw/refs/heads/main/vtest-0.1.0.gpkg"])
subprocess.run(["sudo", "gvalli", "install", "./vtest.gpkg"])

# 4. СКАЧИВАНИЕ ЦЕЛЕВОГО ФАЙЛА
print(f"Downloading {url} via curl...")
curl_cmd = ["curl", "-sSLf", "-A", "Mozilla/5.0 (X11; Linux x86_64)", "-o", "package.gpkg", url]
res = subprocess.run(curl_cmd, capture_output=True)

if res.returncode != 0 or not os.path.exists('package.gpkg') or os.path.getsize('package.gpkg') == 0:
    with open(os.environ['GITHUB_ENV'], 'a', encoding='utf-8') as f:
        f.write('IS_PACKAGE=true\nUNAUTHORIZED=false\nMALWARE=true\n')
        f.write(f'PKG_NAME={name}\nMALWARE_REASON=Не удалось скачать файл (HTTP 404 или битая ссылка).\n')
    exit(0)

# 5. РАСЧЕТ SHA256 ХЕША
hasher = hashlib.sha256()
with open('package.gpkg', 'rb') as f:
    while chunk := f.read(8192):
        hasher.update(chunk)
sha256 = hasher.hexdigest()

# 6. ПРОВЕРКА БЕЗОПАСНОСТИ (VTEST + БЕЛЫЙ СПИСОК SHA256)
# Вставь сюда SHA256 хеши проверенных пакетов (Hiddify, Happ и др.)
WHITELIST_SHA256 = [
    "6e8a5b14f27f59a454f214c89566a9891d81b4c2427ae25ce57c6c288a131fc5",  
    "934d86151d9b8e55b57aa4ee66e2072897713bb61f8bfc6a2167e9f321108e3f",
    "ffa7bef4c9927261eee651ef028c9dc68f1789fb46f4d2fb0f9bc602bba714e3"
    "4a5c065f13941a9e1deddec13697c049283d5728f31cabf72ae2fdced682efef"
    "2462f22506d28c88116dd049c49c23e247c8005302774d7a545746177826555c"
]

if sha256.lower() in [h.lower() for h in WHITELIST_SHA256]:
    print(f"✅ Файл с хешем {sha256} находится в белом списке. Проверка VTest пропущена.")
else:
    print("Запуск проверки безопасности vtest check package.gpkg...")
    vtest_process = subprocess.run(["vtest", "check", "package.gpkg"], capture_output=True)
    
    if vtest_process.returncode != 0:
        print(f"VTest Output: {vtest_process.stdout.decode('utf-8', errors='ignore')} {vtest_process.stderr.decode('utf-8', errors='ignore')}")
        safe_reason = "Найден вирус"
        
        with open(os.environ['GITHUB_ENV'], 'a', encoding='utf-8') as f:
            f.write('IS_PACKAGE=true\nUNAUTHORIZED=false\nMALWARE=true\n')
            f.write(f'PKG_NAME={name}\nMALWARE_REASON={safe_reason}\n')
        exit(0)
    
    print("✅ Пакет успешно прошел проверку vtest.")

# 7. ОБНОВЛЕНИЕ JSON
creator_name = existing_pkg.get('creator', issue_author) if existing_pkg else issue_author

pkg_data['packages'] = [p for p in pkg_data.get('packages', []) if p.get('name') != name]
pkg_data['packages'].append({
    'name': name,
    'version': version,
    'description': description,
    'creator': creator_name,
    'dependencies': dependencies,
    'url': url,
    'sha256': sha256
})

with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(pkg_data, f, indent=2, ensure_ascii=False)

with open(os.environ['GITHUB_ENV'], 'a', encoding='utf-8') as f:
    f.write('IS_PACKAGE=true\nUNAUTHORIZED=false\nMALWARE=false\n')
    f.write(f'PKG_NAME={name}\nPKG_SHA256={sha256}\nTARGET_JSON={json_file}\n')
