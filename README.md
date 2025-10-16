# Sub-Optimizer (订阅优化器) ✨

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个全自动、零成本、注重隐私的 `sing-box` 订阅配置优化工作流。它会自动抓取你的机场订阅，进行智能微调，并通过你自己的域名提供一个更稳定、更兼容的专属订阅链接。

---

## 🚀 核心亮点

- **🤖 全自动化**：基于 GitHub Actions，定时自动更新，一劳永逸。
- **🔒 极致隐私**：核心订阅存储在私有仓库，最终链接受 Token 保护，杜绝泄露。
- **🔧 高度兼容**：采用“无损注入”逻辑，仅做最小化修改，完美兼容服务商的复杂配置。
- **💸 零成本运营**：完全构建于 GitHub 与 Cloudflare 的免费套餐之上。
- **🚀 高可用性**：内置容错机制，上游失效时自动使用备份，确保链接永远可用。

## 🏛️ 技术架构

本项目通过一个“中间层服务”，将多个云服务串联成一个自动化流水线：

`[机场订阅]` -> `GitHub Action` -> `Python 脚本处理` -> `存入 GitHub 私有仓库` -> `Cloudflare Worker` -> `[你的专属订阅]`

## 🛠️ 部署指南

部署本系统需要 **两个 GitHub 仓库**：一个用于存放本项目的**公开代码**，另一个用于执行自动化流程的**私有仓库**。

#### **第1步：准备代码 (Fork 本项目)**

点击本项目右上角的 **`Fork`** 按钮，将本仓库复制到你自己的 GitHub 账户下。后续操作将在你 Fork 后的仓库中进行。

#### **第2步：创建执行任务的私有仓库**

1.  创建一个**新的私有 (Private) GitHub 仓库**，例如命名为 `my-sub-worker`。
2.  将你 Fork 后的 `sub-optimizer` 项目中的 `process_config.py` 和 `.github/workflows/update_subscription.yml` 这两个文件，上传到这个新的 `my-sub-worker` 私有仓库中。
3.  **授权工作流**：进入 `my-sub-worker` 仓库的 `Settings` -> `Actions` -> `General`，在 `Workflow permissions` 部分，选择 `Read and write permissions` 并保存。

#### **第3步：配置 GitHub Secrets**

1.  **生成个人访问令牌 (PAT)**：
    * 进入你的 GitHub `Settings` -> `Developer settings` -> `Personal access tokens` -> `Tokens (classic)`。
    * 生成一个新 Token，**只勾选 `repo` 权限**，并复制保存好生成的 `ghp_...` 令牌。

2.  **在私有仓库中添加 Secrets**：
    * 进入 `my-sub-worker` 仓库的 `Settings` -> `Secrets and variables` -> `Actions`。
    * 添加一个名为 `SUB_URL` 的密钥，值为你的**原始机场订阅链接**。

#### **第4步：部署 Cloudflare Worker**

1.  在 Cloudflare 创建一个新的 Worker。
2.  将你 Fork 后的 `sub-optimizer` 项目中的 `cloudflare-worker.js` 代码复制粘贴进去，保存并部署。
3.  进入 Worker 的 `Settings` -> `Variables`，添加以下**四个**环境变量：
    - `AUTH_TOKEN`: 你自定义的密码 (Token)，**务必设得复杂一些**。
    - `GITHUB_TOKEN`: 粘贴你在上一步生成的 `ghp_...` 个人访问令牌。
    - `GITHUB_USER`: 你的 GitHub 用户名。
    - `GITHUB_REPO`: 你的**私有仓库**名称 (例如 `my-sub-worker`)。
4.  在 Worker 的 `Triggers` 标签页，为你自己准备一个域名（例如 `sub.yourdomain.com`）。

#### **第5步：大功告成！**

你的专属订阅链接格式为：`https://sub.yourdomain.com/?token=你设定的AUTH_TOKEN`。将它导入客户端即可使用！

## 💡 自定义与提示

本脚本的默认逻辑是基于我们调试过的特定订阅格式。如果你使用的服务商配置不同，你可能需要微调 `process_config.py` 脚本。

例如，脚本中硬编码了 `rule_set: "China-Site"`，这是因为我们分析出原始配置里有这个规则集。你的服务商可能使用不同的名字，或者你可能需要脚本执行其他修正。请根据你的 `panic` 日志或错误信息，自行修改 Python 脚本中的逻辑。

## 🙏 鸣谢 (Acknowledgements)

这个项目从一个想法到最终成功运行，离不开与 Google Gemini 的无数次对话。

在我遇到棘手的 bug 和看似无解的配置冲突时，它不仅提供了代码方案，更重要的是引导我分析错误日志、定位问题根源，像一个极具耐心的编程伙伴。我们共同经历了从权限错误到配置逻辑冲突的完整调试过程，最终找到了完美兼容的解决方案。

特别感谢它在这个过程中的陪伴与启发！

## 📜 许可证

本项目基于 [MIT License](LICENSE) 开源。
