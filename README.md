# 📦 GValli Package Repository

**Официальный репозиторий индексов и дистрибуции пакетов для экосистемы G OS**

[![GValli Ecosystem](https://img.shields.io/badge/G-Operating_System-6f42c1?style=for-the-badge&logo=linux&logoColor=white)](https://github.com/AdrescorGiti/GValli)
[![Package Format](https://img.shields.io/badge/Package_Format-.gpkg-ff6b6b?style=for-the-badge)](https://github.com)
[![Architecture](https://img.shields.io/badge/Arch-x86__64_%7C_aarch64-4ecdc4?style=for-the-badge)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-45b7d1?style=for-the-badge)](LICENSE)

[🌐 English](#-english) • [🌐 Русский](#-русский) • [⚙️ Specs](#-specification--спецификация) • [🤝 Contributing](#-contributing)

---

## 🇺🇸 English

The **GValli Package Repository** is a high-performance, decentralized package catalog designed specifically for the GValli Linux distribution. It handles metadata indexing, package resolution, and secure binary delivery using custom `.gpkg` bundles.

### 🌟 Highlights

| Feature | Description |
| :--- | :--- |
| **⚡ Instant Queries** | Near-zero latency search powered by a streamlined, flattened `packages.json` catalog. |
| **📦 Bloat-Free Git** | Large binary `.gpkg` archives are offloaded to **GitHub Releases**, keeping repository footprint under 5MB. |
| **🔐 Cryptographic Integrity** | Mandatory SHA-256 verification before extraction to guarantee binary safety. |
| **🔄 Seamless Automation** | Built-in CLI sync (`gvalli update`) for effortless package index updates. |

### 🛠️ Architecture Flow

┌─────────────────┐       1. Sync Catalog        ┌────────────────────────┐
│   GValli CLI    │ ───────────────────────────> │       index.json       │
│ (gvalli update) │ <─────────────────────────── │  (Central Repository)  │
└────────┬────────┘       2. Parse Metadata      └────────────────────────┘
         │
         │ 3. Download .gpkg (HTTPS)
         ▼
┌─────────────────┐       4. SHA256 Checksum     ┌────────────────────────┐
│ GitHub Releases │ ───────────────────────────> │ Target System Path     │
│ (Binary Assets) │       5. Safe Unpack         │ (/usr/bin, /usr/lib)   │
└─────────────────┘                              └────────────────────────┘

### 🚀 Quick Start

	# 1. Update the local repository index
	$ gvalli update

	# 2. Search for available software
	$ gvalli search htop

	# 3. Install a package securely
	$ gvalli gpkg install htop

---

## 🇷🇺 Русский

**GValli Package Repository** — это централизованный каталог метаданных и индекс дистрибуции программного обеспечения для операционной системы GValli. Система обеспечивает молниеносный поиск, проверку целостности и безопасную установку бинарных пакетов `.gpkg`.

### 🌟 Ключевые преимущества

| Фича | Описание |
| :--- | :--- |
| **⚡ Мгновенный поиск** | Минимальная задержка при поиске благодаря оптимизированному индексу `packages.json`. |
| **📦 Чистая история Git** | Исполняемые `.gpkg` архивы хранятся в **GitHub Releases**, что спасает репозиторий от раздувания. |
| **🔐 Гарантия безопасности** | Обязательная проверка контрольных сумм SHA-256 перед распаковкой каждого файла. |
| **🔄 Простая автоматизация** | Синхронизация каталога одной командой (`gvalli update`). |

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
<summary>🔍 Click to view example <code>index.json</code></summary>

{
  "version": "1.0",
  "updated_at": "2026-08-09T18:00:00Z",
  "packages": [
    {
      "name": "neofetch",
      "version": "7.1.0",
      "architecture": "x86_64",
      "description": "CLI system information tool written in bash",
      "category": "utils",
      "homepage": "[https://github.com/dylanaraps/neofetch](https://github.com/dylanaraps/neofetch)",
      "download_url": "[https://github.com/gvalli-os/packages/releases/download/v7.1.0/neofetch-7.1.0-x86_64.gpkg](https://github.com/gvalli-os/packages/releases/download/v7.1.0/neofetch-7.1.0-x86_64.gpkg)",
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "size_bytes": 34812,
      "dependencies": ["bash"]
    }
  ]
}
</details>

### Repository Layout

.

├── .github/

│   └── workflows/

│       └── process_package.yml        ## Auto-upload .gpkg to GitHub Releases ##

│      

├── packages.json                 ## Master database index ##

└── README.md                  ## Documentation hub ##

---

## 🤝 Contributing

We welcome community contributions! You can help by:
1. Packaging new utilities into `.gpkg` archives.
2. Reporting broken download links or add your `.gpkg`  via [Issues](../../issues).
3. Help with G OS soft

---

*Crafted with ❤️ for the **G Operating System***
