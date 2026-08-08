##GValli Package Repository

Official package repository for GValli, designed to store, manage, and distribute .gpkg software packages.

🇺🇸 English
Features
Fast Package Search: Powered by a centralized index.json catalog for lightning-fast queries via the CLI (GValli search).

Release-Hosted Binaries: .gpkg files are stored securely via GitHub Releases to prevent repository bloat.

Automated Installation: Fully compatible with GValli gpkg install <package_name> for automated downloading, verification, and unpacking.

Repository Structure
index.json — The package index database containing metadata, versions, download URLs, and checksums.

GitHub Releases — Storage for compiled .gpkg archive files.

🇷🇺 Русский
Особенности
Быстрый поиск пакетов: Работает на основе централизованного каталога index.json для мгновенного поиска через CLI (GValli search).

Хранение через Releases: Сами файлы .gpkg хранятся в разделе GitHub Releases, чтобы не перегружать историю Git-репозитория лишним весом.

Автоматическая установка: Полная совместимость с командой GValli gpkg install <имя_пакета> для автоматической загрузки, проверки целостности и распаковки.

Структура репозитория
index.json — База данных индекса пакетов, содержащая метаданные, версии, ссылки на скачивание и контрольные суммы.

GitHub Releases — Хранилище скомпилированных архивных файлов .gpkg.
