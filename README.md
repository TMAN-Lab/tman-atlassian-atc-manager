# Atlassian AutoTestCase Manager (atlas-atc-manager)

[![org](https://img.shields.io/static/v1?style=for-the-badge&label=org&message=TMAN%20Consulting&color=0061f9)](https://en.tman.ltd)
![license](https://img.shields.io/github/license/tman-lab/tman-atlassian-operator?style=for-the-badge)
![author](https://img.shields.io/static/v1?style=for-the-badge&label=author&message=will.shi@tman.ltd&color=blue)
[![python](https://img.shields.io/static/v1?style=for-the-badge&logo=python&label=Python&message=3.x&color=306ba1)](https://devguide.python.org/versions/)
[![pypi](https://img.shields.io/pypi/v/atlassian-auto-test-case-manager.svg?style=for-the-badge)](https://pypi.org/project/atlassian-auto-test-case-manager)
[![Star on GitHub](https://img.shields.io/github/stars/TMAN-Lab/tman-atlassian-atc-manager?style=for-the-badge)](https://github.com/TMAN-Lab/tman-atlassian-atc-manager/stargazers)

> Extract test cases from automation code and sync them to Jira Xray — without manual copy-pasting!

----

This open-source CLI tool is developed and maintained by [Will Shi @ TMAN Consulting](https://en.tman.ltd), with the goal of bridging the gap between automated test code and Jira-based test management.

It helps QA and DevOps engineers **extract test cases directly from Python, Java, or Robot Framework code** and auto-create structured test cases in **Jira Xray** (both **Cloud** and **Data Center** editions).

----

## 🚀 What's Next: TMAN AutoTestCase Extractor (Jira Cloud Plugin)

We’re building a **native Jira Cloud plugin**, based on this CLI engine but designed for **remote Git repositories**, **no local installation**, and seamless integration with GitHub / GitLab / Bitbucket via API.

🎯 **No installation. No CLI. Just connect your repo and sync test cases — all inside Jira.**

🔔 **Sign up for early access:** [Google Forms](https://forms.gle/r7jsVv7j27DUThULA)  

----

## ⭐ Love this tool?

If you find this project helpful:

- 🌟 Please **star the repo** to support further development  
- 👀 Follow the repo or enable “Watch” to get notified about major updates
- 🧪 Try it in your test projects and open issues/feedback  
- 📢 Share it with your team or in your community

Your encouragement helps this project (and the upcoming plugin) grow stronger 💪

----

```text
   ___ ________   ___   ____  ___ ___________  __  ___
  / _ /_  __/ /  / _ | / __/ / _ /_  __/ ___/ /  |/  /__ ____  ___ ____ ____ ____
 / __ |/ / / /__/ __ |_\ \  / __ |/ / / /__  / /|_/ / _ `/ _ \/ _ `/ _ `/ -_) __/
/_/ |_/_/ /____/_/ |_/___/ /_/ |_/_/  \___/ /_/  /_/\_,_/_//_/\_,_/\_, /\__/_/
                                                                  /___/          
```

----

## ✨ Key Features

- ✅ **Auto-detect and parse test cases** from Python (pytest, unittest), Java (JUnit-style), or Robot Framework files 
- ✅ **Create or update corresponding test cases** in Jira (Xray) Cloud or Data Center
- ✅ **Add source code or docstrings** as structured test steps
- ✅ **CLI-based**, easy to integrate into CI/CD pipelines
- ✅ **Configurable** via command-line arguments or persistent credential file

----

## 🔧 Why Use This Tool?

- Reduce manual overhead of copying test cases to Jira
- Keep your test documentation and automation always in sync
- Enhance traceability between code and Jira Xray artifacts
- Empower your QA/dev team to **focus on testing, not on syncing**

---

## 🎯 Roadmap

| Feature | CLI (atlas-atc-manager) | Jira Cloud Plugin (TMAN AutoTestCase Extractor) |
|---------|-------------------------|-------------------------------------------------|
| Local test code parsing | ✅ Supported             | 🚫 Not applicable                               |
| Remote Git integration | 🚫                      | ✅ GitHub / GitLab / Bitbucket                   |
| UI-based management | 🚫                      | ✅ Jira-native interface                         |
| OAuth/token authentication | 🚫                      | ✅ Planned                                       |
| Incremental sync | 🚫                      | ✅ Planned                                       |
| CI/CD integration | ✅ CLI-friendly          | ✅ Native webhook support                        |

We aim to support teams who want:
- Traceability from test code to Jira
- No manual duplication of test cases
- Scalable test management for QA + DevOps

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
  show-version        display version info for this tool and your Python runtime
  show-variables      show all supported environment variables
  show-config         show config
  config-cred         set and save Jira credentials/config (project, token, etc.)
  extract-case        extract test cases from code and sync them to Jira (Xray, Zephyr Scale, etc.)

Use 'atlas-atc-manager <command> --help' for more info on a specific command.
```

### `extract-case`

```text
Usage: atlas-atc-manager extract-case --test-path <TEST_CODE_PATH> [options]

Options:
  --test-path <TEST_CODE_PATH>
                        Path to a test file or folder (supports .py, .java, .robot)
  --jira-plugin <xray>  Target test management tool on Jira : xray
  --jira-project <PROJECT_KEY>
                        Jira project key (e.g. "TEST")
  --jira-hosting <cloud|dc>
                        Jira hosting type (supports cloud, data-center) : cloud | dc
  --jira-site <URL>     Jira site URL (e.g. https://yourcompany.atlassian.net)
  --jira-user <USERNAME>
                        Specify the Jira username for authentication
  --jira-token <TOKEN>  Jira API token for authentication
  --xray-client-id <CLIENT_ID>
                        XRAY Cloud client id for authentication
  --xray-client-secret <CLIENT_SECRET>
                        XRAY Cloud client secret for authentication
  -h, --help            Show this help message and exit
```

- [How to Get Jira Cloud API Token](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/#Create-an-API-token)

#### 🧪 Example

```bash
atlas-atc-manager extract-case \
  --test-path ./tests/ \
  --jira-plugin xray \
  --jira-project QA \
  --jira-hosting dc \
  --jira-site https://jira.mycompany.com \
  --jira-token xxxx-xxxx-xxxx
```

### `config-cred`

Save frequently used configuration to a local file (`~/.atlas_atc_manager/credential.conf`), so you don’t need to pass everything each time.

```bash
atlas-atc-manager config-cred --jira-plugin xray --jira-project QA --jira-hosting dc --jira-site https://jira.company.com --jira-token xxxx
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
