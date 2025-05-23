# Atlassian AutoTestCase Manager

*Brought to you by [TMAN Consulting](https://en.tman.ltd)*

```text
   ___ ________   ___   _______________   _  __  ___ ___________  __  ___                           
  / _ /_  __/ /  / _ | / __/ __/  _/ _ | / |/ / / _ /_  __/ ___/ /  |/  /__ ____  ___ ____ ____ ____
 / __ |/ / / /__/ __ |_\ \_\ \_/ // __ |/    / / __ |/ / / /__  / /|_/ / _ `/ _ \/ _ `/ _ `/ -_) __/
/_/ |_/_/ /____/_/ |_/___/___/___/_/ |_/_/|_/ /_/ |_/_/  \___/ /_/  /_/\_,_/_//_/\_,_/\_, /\__/_/   
                                                                                     /___/          
```

> **Seamlessly connect your test automation code with Jira (Xray, Zephyr Scale)** — extract test cases from your codebase and push them into Jira with a single command.

[![org](https://img.shields.io/static/v1?style=for-the-badge&label=org&message=TMAN%20Consulting&color=0061f9)](https://en.tman.ltd)
![license](https://img.shields.io/github/license/tman-lab/tman-atlassian-operator?style=for-the-badge)
![author](https://img.shields.io/static/v1?style=for-the-badge&label=author&message=will.shi@tman.ltd&color=blue)
[![python](https://img.shields.io/static/v1?style=for-the-badge&logo=python&label=Python&message=3.x&color=306ba1)](https://devguide.python.org/versions/)
[![pypi](https://img.shields.io/pypi/v/atlassian-auto-test-case-manager.svg?style=for-the-badge)](https://pypi.org/project/atlassian-auto-test-case-manager)

----

## 🚀 Key Features

- ✅ **Auto-detect and parse test cases** from Python (pytest, unittest), Java (JUnit-style), or Robot Framework scripts
- ✅ **Create or update corresponding test cases** in Jira (Xray, Zephyr Scale)
- ✅ **Convert test functions and docstrings** into structured test steps in Jira
- ✅ **Command-line interface (CLI)** ready for CI/CD pipeline integration
- ✅ **Supports Git-based repositories**, configurable via CLI flags or persistent auth file

----

## 🔧 Why Use This Tool?

- Reduce manual overhead of copying test cases to Jira
- Keep your test documentation and automation always in sync
- Enhance traceability between code and Jira (Xray, Zephyr Scale) artifacts
- Empower your QA/dev team to **focus on testing, not on syncing**

----

## ⚡️ Quick Start

### 🏗 Check preconditions

- [Python](https://www.python.org/downloads/) >= 3
- [pip](https://pip.pypa.io/en/stable/installation/) (Python package manager)

### 📦 Install `atlas-atc-manager` tool

```bash
pip install atlassian-auto-test-case-manager
atlas-atc-manager show-version
```

----

## 🧰 Usage

### Available Commands

```text
Usage: atlas-atc-manager [COMMAND] [OPTIONS]

Commands:
  show-version        Display version info for this tool and your Python runtime
  config-cred         Set and save Jira credentials/config (project, token, etc.)
  sync-case           Parse test code and sync test cases to Jira (Xray, Zephyr Scale, etc.)

Use 'atlas-atc-manager <command> --help' for more info on a specific command.
```

### `sync-case`

```text
Usage: atlas-atc-manager sync-case --file-path <TEST_CODE_PATH> [options]

Options:
  --file-path <TEST_CODE_PATH>      Path to a test file or folder (supports .py, .java, .robot)
  --platform <xray|zephyr-scale>    Target test management tool (default: xray)
  --project <PROJECT_KEY>           Jira project key (e.g. "TEST")
  --hosting <cloud|dc>              Jira hosting type (default: cloud)
  --jira-site <URL>                 Jira site URL (e.g. https://yourcompany.atlassian.net)
  --jira-token <TOKEN>              Jira API token for authentication
  -h, --help                        Show this help message and exit
```

- [How to Get Jira Cloud API Token](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/#Create-an-API-token)

#### 🧪 Example

```bash
atlas-atc-manager sync-case \
  --file-path ./tests/ \
  --platform xray \
  --project QA \
  --hosting dc \
  --jira-site https://jira.mycompany.com \
  --jira-token xxxx-xxxx-xxxx
```

### `config-cred`

Save frequently used configuration to a local file (`~/.atlas_atc_manager/credential.conf`), so you don’t need to pass everything each time.

```bash
atlas-atc-manager config-cred --platform xray --project QA --hosting dc --jira-site https://jira.company.com --jira-token xxxx
```

Re-run with `--overwrite` to update.

----

## 🛠 Supported Test Formats

| Language | Framework            | File Type | Auto-detect? |
| -------- | -------------------- | --------- | ------------ |
| Python   | `pytest`, `unittest` | `.py`     | ✅ Yes       |
| Java     | `JUnit-style`        | `.java`   | ✅ Yes       |
| Robot    | Robot Framework      | `.robot`  | ✅ Yes       |

## 📌 Notes

- Current version supports **Xray for Jira Data Center** and **Xray for Jira Cloud**.
- The tool works best in Git-tracked repos, as it uses the repo name to organize test set paths.

## 🌍 License

Apache License 2.0

[LICENSE](https://github.com/TMAN-Lab/tman-atlassian-atc-manager?tab=Apache-2.0-1-ov-file)

----

## 📒 Credits

Developed by [Will Shi](https://profile.willshi.space/en) at [TMAN Consulting](https://en.tman.ltd)
Designed to help teams move faster by connecting code with Jira.

----

## 📚 References

### XRAY

- [Create XRAY Cloud API Key](https://docs.getxray.app/display/XRAYCLOUD/Global+Settings%3A+API+Keys#GlobalSettings:APIKeys-CreateanAPIKey)
- [Create Test via XRAY Cloud Graphql REST API](https://us.xray.cloud.getxray.app/doc/graphql/createtest.doc.html)
