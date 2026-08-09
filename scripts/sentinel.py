#!/usr/bin/env python3
import asyncio
import aiohttp
import tarfile
import hashlib
import os
import sys
import logging
import json
import subprocess
from pathlib import Path

# ==========================================
# КОНФИГУРАЦИЯ
# ==========================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("GValliBot")

VIRUSTOTAL_API = os.getenv("VT_API_KEY")
VT_URL = "https://www.virustotal.com/api/v3/files/{}"

# ==========================================
# АБСОЛЮТНЫЙ ЧЕРНЫЙ СПИСОК УГРОЗ
# ==========================================
BLACKLIST = [
    # 1. Тотальное уничтожение и форматирование
    b"rm -rf / ", b"rm -rf /*", b"rm -rf --no-preserve-root", 
    b"mkfs.", b"mkswap", b"wipefs", b"fdisk ", b"cfdisk",
    b"dd if=/dev/zero", b"dd if=/dev/random", b"of=/dev/sda", b"of=/dev/nvme",
    
    # 2. Попытки сломать права и доступы
    b"chmod -R 777 /", b"chmod 777 /etc", b"chmod 777 /root",
    b"chown -R root:root /",
    
    # 3. Кража и подмена паролей/пользователей
    b"> /etc/passwd", b">> /etc/passwd",
    b"> /etc/shadow", b">> /etc/shadow",
    b"> /etc/sudoers", b">> /etc/sudoers",
    b"usermod -aG sudo", b"usermod -aG wheel", b"useradd -o -u 0",
    
    # 4. Реверс-шеллы (открытие доступа хакеру)
    b"bash -i", b"nc -e", b"nc -c", b"/dev/tcp/", b"/dev/udp/",
    b"socat exec", b"perl -e 'use Socket", b"python -c 'import socket",
    
    # 5. Скрытые загрузки малвари из сети
    b"curl | bash", b"curl | sh", b"curl -sL | bash",
    b"wget -qO- | bash", b"wget -O- | sh",
    
    # 6. Закрепление в системе (Persistence)
    b".ssh/authorized_keys", b"echo ssh-rsa >>",
    b"crontab -e", b"/etc/cron.d/", b"/etc/cron.hourly/",
    
    # 7. Обфускация (попытка спрятать код)
    b"base64 -d | sh", b"base64 -d | bash", b"base64 --decode | bash"
]

def get_urls_from_json(json_content):
    urls = set()
    try:
        data = json.loads(json_content)
        packages = data if isinstance(data, list) else data.get('packages', [])
        for pkg in packages:
            if isinstance(pkg, dict) and 'url' in pkg:
                urls.add(pkg['url'])
    except Exception as e:
        logger.error(f"Ошибка парсинга JSON: {e}")
    return urls

def get_new_package_urls(json_path: str):
    logger.info(f"Сверка изменений в {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        current_urls = get_urls_from_json(f.read())
        
    old_urls = set()
    try:
        old_json = subprocess.check_output(['git', 'show', f'origin/main:{json_path}']).decode('utf-8')
        old_urls = get_urls_from_json(old_json)
    except Exception:
        logger.warning("Не удалось вытянуть старый JSON. Проверяем всё!")
        
    return current_urls - old_urls

async def download_package(session, url, dest_dir: Path):
    file_name = url.split('/')[-1]
    dest_path = dest_dir / file_name
    async with session.get(url) as response:
        if response.status == 200:
            with open(dest_path, 'wb') as f:
                f.write(await response.read())
            return dest_path
    return None

def extract_and_verify_structure(gpkg_path: Path, extract_dir: Path) -> bool:
    try:
        with tarfile.open(gpkg_path, "r:*") as tar:
            for member in tar.getmembers():
                if member.name.startswith("/") or "../" in member.name:
                    logger.critical(f"ZIP-SLIP АТАКА! Пакет пытается вылезти за пределы папки: {member.name}")
                    return False
            tar.extractall(path=extract_dir)
        return True
    except tarfile.TarError:
        return False

def scan_all_files_for_backdoors(target_dir: Path) -> bool:
    is_clean = True
    for root, _, files in os.walk(target_dir):
        for file in files:
            file_path = Path(root) / file
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                    for danger in BLACKLIST:
                        if danger in content:
                            logger.critical(f"БЛОКИРОВКА! Найдена разрушительная команда: {danger.decode('utf-8', errors='ignore')}")
                            logger.critical(f"Файл: {file_path.name}")
                            is_clean = False
            except Exception:
                pass
    return is_clean

async def process_binaries_async(target_dir: Path, session: aiohttp.ClientSession) -> bool:
    if not VIRUSTOTAL_API: return True
    tasks = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            file_path = Path(root) / file
            if os.access(file_path, os.X_OK):
                sha256_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
                tasks.append(check_hash_vt(session, sha256_hash, file_path.name))
    if not tasks: return True
    results = await asyncio.gather(*tasks)
    return all(results)

async def check_hash_vt(session, sha256_hash, filename) -> bool:
    headers = {"x-apikey": VIRUSTOTAL_API}
    async with session.get(VT_URL.format(sha256_hash), headers=headers) as resp:
        if resp.status == 200:
            data = await resp.json()
            stats = data['data']['attributes']['last_analysis_stats']
            if stats['malicious'] > 0:
                logger.critical(f"VIRUSTOTAL: Бинарник {filename} заражен! ({stats['malicious']} детектов)")
                return False
    return True

async def main():
    if len(sys.argv) < 2: sys.exit(2)
    json_path = sys.argv[1]
    
    new_urls = get_new_package_urls(json_path)
    if not new_urls:
        logger.info("Новых пакетов нет. Выход.")
        sys.exit(0)
        
    download_dir = Path("/tmp/gpkg_downloads")
    extract_dir = Path("/tmp/gpkg_eval")
    download_dir.mkdir(exist_ok=True)
    extract_dir.mkdir(exist_ok=True)
    
    all_clean = True
    async with aiohttp.ClientSession() as session:
        for url in new_urls:
            logger.info(f"Проверка {url}...")
            gpkg_path = await download_package(session, url, download_dir)
            if not gpkg_path: continue
                
            pkg_extract_dir = extract_dir / gpkg_path.name
            pkg_extract_dir.mkdir(exist_ok=True)
            
            if not extract_and_verify_structure(gpkg_path, pkg_extract_dir): all_clean = False
            if not scan_all_files_for_backdoors(pkg_extract_dir): all_clean = False
            if not await process_binaries_async(pkg_extract_dir, session): all_clean = False
                
    if not all_clean:
        logger.critical("ВЕРДИКТ: ПАКЕТ СОДЕРЖИТ УГРОЗУ СИСТЕМЕ.")
        sys.exit(1)
        
    logger.info("ВЕРДИКТ: БЕЗОПАСНО.")
    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
  
