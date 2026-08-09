<div align="center">

# 📦 GValli Package Repository

<img width="260" alt="GValli Logo" src="https://github.com/user-attachments/assets/b64078b2-4f17-49c0-bb3b-9851940f9630" />

### Официальный репозиторий индексов и дистрибуции пакетов для экосистемы G OS

[![GValli Ecosystem](https://img.shields.io/badge/G-Operating_System-6f42c1?style=for-the-badge&logo=linux&logoColor=white)](https://github.com/AdrescorGiti/GValli)
[![Package Format](https://img.shields.io/badge/Package_Format-.gpkg-ff6b6b?style=for-the-badge)](https://github.com)
[![Architecture](https://img.shields.io/badge/x86__64-v3_-4ecdc4?style=for-the-badge)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-45b7d1?style=for-the-badge)](LICENSE)

[🌐 English](#-english) • [🌐 Русский](#-русский) • [⚙️ Specs / Спецификация](#%EF%B8%8F-specification--спецификация) • [🤝 Contributing](#-contributing)

</div>

---

## 🇺🇸 English

The **GValli Package Repository** is a high-performance, decentralized package catalog designed specifically for the G OS distribution. It handles metadata indexing, package resolution, and secure binary delivery using custom `.gpkg` bundles.

### 🌟 Highlights

| Feature | Description |
| :--- | :--- |
| **⚡ Instant Queries** | Near-zero latency search powered by a streamlined, flattened `packages.json` catalog. |
| **📦 Bloat-Free Git** | Large binary `.gpkg` archives are offloaded to **GitHub Releases**, keeping repository footprint under 5MB. |
| **🔐 Cryptographic Integrity** | Mandatory SHA-256 verification before extraction to guarantee binary safety. |
| **🔄 Seamless Automation** | Built-in CLI sync (`gvalli update`) for effortless package index updates. |

### 🛠️ Architecture Flow (English)

```text
┌─────────────────────────┐          1. Sync Catalog (`packages.json`)         ┌──────────────────────────────────┐
│                         │ ─────────────────────────────────────────────────> │     GitHub Repository Catalog    │
│                         │ <───────────────────────────────────────────────── │    (AdrescorGiti/GValli Index)   │
│       GValli CLI        │          2. Parse Metadata & Check URL             └──────────────────────────────────┘
│     (gvalli update /    │
│     gvalli install)     │          3. Fetch `.gpkg` Binary Release
│                         │ ─────────────────────────────────────────────────> ┌──────────────────────────────────┐
│                         │ <───────────────────────────────────────────────── │    GitHub Releases Storage       │
│                         │          4. Download Asset (HTTPS)                 │   (Hosted Binary Assets)         │
└────────────┬────────────┘                                                    └──────────────────────────────────┘
             │
             │ 5. SHA-256 Checksum Verification
             │ 6. Safe Extraction & Installation
             ▼
┌─────────────────────────┐
│   Target System Paths   │
│  (/usr/bin, /usr/lib)   │
└─────────────────────────┘
```


### 🚀 Quick Start

	# 1. Update the local repository index
	$ gvalli update

	# 2. Search for available software
	$ gvalli search htop

	# 3. Install a package securely
	$ gvalli gpkg install htop

---

## 🇷🇺 Русский

**GValli Package Repository** — это централизованный каталог метаданных и индекс дистрибуции программного обеспечения для G OS. Система обеспечивает молниеносный поиск, проверку целостности и безопасную установку бинарных пакетов `.gpkg`.

### 🌟 Ключевые преимущества

| Фича | Описание |
| :--- | :--- |
| **⚡ Мгновенный поиск** | Минимальная задержка при поиске благодаря оптимизированному индексу `packages.json`. |
| **📦 Чистая история Git** | Исполняемые `.gpkg` архивы хранятся в **GitHub Releases**, что спасает репозиторий от раздувания. |
| **🔐 Гарантия безопасности** | Обязательная проверка контрольных сумм SHA-256 перед распаковкой каждого файла. |
| **🔄 Простая автоматизация** | Синхронизация каталога одной командой (`gvalli update`). |

### 🛠️ Схема архитектуры (Русский)
```text
┌─────────────────────────┐         1. Синхронизация индекса (`packages.json`) ┌──────────────────────────────────┐
│                         │ ─────────────────────────────────────────────────> │     Центральный репозиторий      │
│                         │ <───────────────────────────────────────────────── │   (Индекс AdrescorGiti/GValli)   │
│       GValli CLI        │         2. Парсинг метаданных и ссылок             └──────────────────────────────────┘
│     (gvalli update /    │
│     gvalli install)     │         3. Запрос `.gpkg` архива
│                         │ ─────────────────────────────────────────────────> ┌──────────────────────────────────┐
│                         │ <───────────────────────────────────────────────── │     GitHub Releases Хранилище    │
│                         │         4. Загрузка файла (HTTPS)                  │    (Готовые бинарные сборки)     │
└────────────┬────────────┘                                                    └──────────────────────────────────┘
             │
             │ 5. Проверка хеш-суммы SHA-256
             │ 6. Безопасная распаковка и установка
             ▼
┌─────────────────────────┐
│  Системные директории   │
│  (/usr/bin, /usr/lib)   │
└─────────────────────────┘
```



### 🚀 Быстрый старт

	# 1. Обновление локального индекса пакетов
	$ gvalli update

	# 2. Поиск необходимой программы
	$ gvalli search neofetch

	# 3. Автоматическая установка с проверкой хеша
	$ gvalli gpkg install neofetch

---


## ⚙️ Specification / Спецификация

### Package Index Schema (`packages.json`)

The entire repository relies on a validated JSON schema for cataloging available software.

<details>
<summary>🔍 Click to view example <code>packages.json</code></summary>

```json
{
  "version": "1.0",
  "updated_at": "2026-08-10T00:00:00Z",
  "packages": [
    {
      "name": "neofetch",
      "version": "7.1.0",
      "architecture": "x86_64-v3",
      "description": "CLI system information tool written in bash",
      "category": "utils",
      "homepage": "[https://github.com/dylanaraps/neofetch](https://github.com/dylanaraps/neofetch)",
      "download_url": "[https://github.com/AdrescorGiti/GValli/releases/download/v7.1.0/neofetch-7.1.0-x86_64-v3.gpkg](https://github.com/AdrescorGiti/GValli/releases/download/v7.1.0/neofetch-7.1.0-x86_64-v3.gpkg)",
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "size_bytes": 34812,
      "dependencies": [
        "bash"
      ]
    }
  ]
}
```
---

## 🤝 Contributing

We welcome community contributions! You can help by:
1. Packaging new utilities into `.gpkg` archives.
2. Reporting broken download links or add your `.gpkg`  via [Issues](../../issues).
3. Help with G OS soft

---

*Crafted with ❤️ for the **G Operating System***
