# AI 磁盘空间分析助手

本项目旨在开发一款利用AI技术分析磁盘扫描数据（如WizTree导出的CSV文件），帮助用户理解文件组成、识别大文件/冗余文件、追踪文件增长趋势，并提供清理建议的智能工具。

## 项目目标

- 智能分析磁盘数据，轻松释放存储空间，洞察文件变化趋势。
- 提供超越传统工具的简单统计，提供更深层次的洞察和建议。
- 清晰展示文件/文件夹随时间的变化，帮助用户理解存储增长模式。
- 支持导入WizTree等流行磁盘扫描工具的CSV数据，降低用户使用门槛。
- 基于AI分析结果，提供针对性的文件清理建议，并能结合用户具体问题对特定文件夹内容进行解答。
- 优化了与AI交互的数据量，通过发送摘要信息来应对API的字数限制。
- **更灵活的CSV路径处理**：即使WizTree导出的CSV文件中没有直接的“Path”列，只要存在“文件名称”（或英文“File Name”）列，程序也能智能识别并将其作为路径信息进行分析，增强了对不同导出格式的兼容性。

## 如何开始

1.  **准备环境**:
    *   确保您的计算机上已安装 Python (建议版本 3.7+)。您可以从 [Python官网](https://www.python.org/downloads/) 下载并安装。
    *   如果您使用代码编辑器（如 VS Code），打开项目文件夹。

2.  **获取代码**:
    *   如果您通过 Git 克隆了仓库，请跳至下一步。
    *   如果直接下载了文件，请确保所有文件和文件夹结构完整。

3.  **创建虚拟环境 (推荐)**:
    *   打开终端或命令提示符，导航到项目根目录 (`Pycsstoai`)。
    *   运行以下命令创建虚拟环境 (例如，命名为 `.venv`):
        ```bash
        python -m venv .venv
        ```
    *   激活虚拟环境:
        *   Windows (CMD/PowerShell):
            ```bash
            .venv\Scripts\activate
            ```
        *   macOS/Linux (bash/zsh):
            ```bash
            source .venv/bin/activate
            ```

4.  **安装依赖**:
    *   在激活的虚拟环境中，运行以下命令安装所需的库:
        ```bash
        pip install -r requirements.txt
        ```

5.  **运行程序**:
    *   在项目根目录下，运行主程序:
        ```bash
        python src/main.py
        ```
    *   程序启动后，会弹出一个文件选择对话框，请选择一个 WizTree 导出的 CSV 文件进行分析。
    *   分析结果将打印在终端或命令提示符窗口中。

6.  **退出虚拟环境 (可选)**:
    *   当您完成操作后，可以在终端中输入以下命令退出虚拟环境:
        ```bash
        deactivate
        ```
7. **查看已安装的库**:
   * 在激活的虚拟环境中，运行以下命令查看所有已安装的Python库:
       ```bash
       pip list
       ```
   * 或者使用以下命令将已安装的库导出到文件:
       ```bash
       pip freeze > requirements.txt
       ```

## 使用方法

1.  **准备 WizTree CSV 文件**: 
    *   使用 WizTree 工具扫描您的磁盘。
    *   扫描完成后，通过 WizTree 的菜单导出数据为 CSV 文件 (通常在 “文件” -> “导出CSV文件...”)。
    *   请确保导出的 CSV 文件至少包含 **文件名称** (或英文 "File Name") 和 **大小** (或英文 "Size") 这两列信息。如果导出的文件有明确的 **路径** (或英文 "Path") 列，程序也会优先使用它。

2.  **运行程序**: 
    *   按照上面的“如何开始”步骤安装并运行程序 (`streamlit run src/app.py`)。
    *   程序启动后，会在浏览器中显示一个网页界面。

3.  **上传 CSV 文件**: 
    *   在网页界面上，点击 “选择 WizTree CSV 文件” 按钮，或者直接将您的 CSV 文件拖拽到指定区域。

4.  **查看分析结果**: 
    *   文件上传成功后，程序会自动进行分析，并在页面上展示各种统计数据、图表和 AI 的建议。
    *   您可以滚动页面查看所有分析内容。

5.  **与 AI 互动**: 
    *   在 “AI 分析特定文件夹内容” 部分，您可以输入 CSV 文件中存在的某个文件夹路径，并提出您关心的问题，然后点击按钮让 AI 进行分析和回答。

为了提供更友好的用户体验，本项目现在包含一个基于 Streamlit 的图形用户界面。

1.  **确保 Streamlit 已安装**: 如果您按照前面的步骤安装了 `requirements.txt` 中的依赖，Streamlit应该已经安装好了。
2.  **运行 Streamlit 应用**: 
    *   在激活的虚拟环境中，导航到项目根目录 (`Pycsstoai`)。
    *   运行以下命令:
        ```bash
        streamlit run src/app.py
        ```
    *   命令执行后，您的默认浏览器应该会自动打开一个新的标签页，显示应用的界面。如果没有自动打开，终端会显示一个本地网址 (通常是 `http://localhost:8501`)，您可以手动复制到浏览器中打开。
3.  **使用应用**: 
    *   通过界面上的“选择 WizTree CSV 文件”按钮上传您的 WizTree 导出的 CSV 文件。
    *   应用会自动分析文件并展示结果，包括基本统计、大文件列表、文件类型分析以及 AI 提供的建议。

## 主要功能特性

### AI 驱动的分析与建议

程序能够：

*   **智能解析CSV**：自动识别并处理WizTree导出的CSV文件，提取关键信息如文件名称、大小等。
    *   特别地，对于路径信息，程序会优先寻找名为“Path”的列。如果找不到，它会尝试使用名为“文件名称”或“File Name”的列作为路径来源。这使得即使用户导出的CSV格式稍有不同，程序也能大概率正确工作。
*   **基本统计展示**：清晰展示扫描项目总数、总占用空间等基础数据。
*   **识别大文件/文件夹**：快速定位占用空间最多的文件和文件夹。
*   **按类型/扩展名分类**：统计不同文件类型（如视频、图片、文档）和扩展名（如.mp4, .jpg, .docx）的空间占用情况，并以图表形式直观展示。
*   **AI摘要与清理建议**：利用AI大模型分析磁盘使用摘要，并根据大文件列表提供初步的文件清理建议。
*   **特定文件夹AI问答**：允许用户针对CSV中存在的特定文件夹路径提出问题，AI会结合该文件夹下的文件信息进行解答。

本项目现在包含一个初步的AI分析模块 (`src/ai_analyzer.py`)，用于对磁盘扫描结果进行更深层次的洞察。目前，该模块提供了以下占位符功能：

1.  **磁盘使用摘要分析 (`analyze_disk_usage_summary`)**: 
    当您想了解整个磁盘或某个较大范围的存储使用概览时，此功能非常有用。
    - **输入**: 磁盘使用摘要字符串 (例如："总大小: 100GB, 图片: 20GB (20%), 视频: 50GB (50%), 其他: 30GB (30%)")。
    - **AI处理**: AI会分析这个摘要，识别主要的空间占用类别，并给出通用的优化建议。
    - **输出**: AI生成的分析结果和优化建议。
2.  **文件清理建议 (`suggest_files_for_cleanup`)**: 
    如果您有一份文件列表（比如来自某个文件夹，或者整个磁盘的大文件列表），AI可以帮助您判断哪些文件可能适合清理。
    - **输入**: 一个包含文件信息的Pandas DataFrame (至少需要 'File Name', 'Size', 'Path' 列)。
    - **AI处理**: AI会查看文件列表的摘要（比如最大的几个文件），并根据这些信息给出清理建议，例如哪些类型的文件通常可以被归档或删除。
    - **输出**: AI生成的具体文件清理建议。
3.  **AI分析特定文件夹内容 (`analyze_folder_contents`)**:
    这是本次更新的重点功能！当您对某个特定文件夹里的文件感到困惑时（比如不知道这些文件是干什么的，是否重要，能不能删除），这个功能可以帮到您。
    - **输入**:
        - `folder_path`: 您想分析的文件夹的路径。
        - `file_details_df`: 一个包含该文件夹内详细文件信息的Pandas DataFrame (应有 'File Name', 'Size', 'Path', 'Type' 等列)。
        - `user_query` (可选): 您关于这个文件夹的具体问题。例如：“这个文件夹里的 .tmp 文件都是什么？” 或者 “哪些文件可以安全删除？”
    - **AI处理**:
        - 程序会首先生成该文件夹内容的摘要信息，包括主要文件类型统计、占用空间较大的文件示例等。
        - 然后，这个摘要连同您的具体问题（如果有的话）会一起发送给AI。
        - AI会基于这些信息，尝试回答您的问题，分析文件夹内容，并给出整理建议。
    - **输出**: AI针对您的文件夹和问题生成的分析和解答。

    **如何有效提问以获得更好的文件夹分析结果？**

    - **具体化您的问题**：与其问“这个文件夹能清理吗？”，不如问“这个文件夹里的 `*.log` 文件是做什么用的？我可以删除旧的日志文件吗？”
    - **提供上下文**：如果可能，在问题中提及文件夹的用途，例如：“这是我的'下载'文件夹，里面的这些大文件是什么？”
    - **理解AI的局限性**：AI的回答基于提供给它的文件摘要信息。它不能直接“看到”您的文件内容。对于非常关键或不确定的文件，AI通常会建议您谨慎操作或先备份。

    通过这种方式，即使我们不能把所有文件细节都发给AI，AI也能通过摘要和您的问题，给您提供有价值的帮助！

#### 如何在代码中使用

在 `src/main.py` 脚本中，`AIAnalyzer` 类被实例化并用于调用分析方法。分析结果会打印到控制台。

```python
# src/main.py (示例片段)
from src.ai_analyzer import AIAnalyzer

# ... (加载数据后)
if csv_data is not None and not csv_data.empty:
    analyzer = AIAnalyzer() # AIAnalyzer 会尝试从环境变量读取API密钥
    # 为AI分析准备摘要数据
    total_size_bytes = csv_data['Size'].sum()
    num_files = len(csv_data)
    summary_for_ai = f"总扫描项目数: {num_files}, 总占用空间: {format_size_dynamically(total_size_bytes)}."
    
    ai_summary_analysis = analyzer.analyze_disk_usage_summary(summary_for_ai)
    print("\n--- AI磁盘使用摘要分析 ---")
    print(ai_summary_analysis)

    ai_cleanup_suggestion = analyzer.suggest_files_for_cleanup(csv_data)
    print("\n--- AI文件清理建议 ---")
    print(ai_cleanup_suggestion)
```

**重要提示**: 当前的AI实现是基于占位符的，它模拟AI的响应。要获得真实的AI分析，您需要在 `src/ai_analyzer.py` 中集成实际的AI服务API调用（例如 OpenAI, Google Gemini, 或其他），并确保已正确配置API密钥（见下面的“AI 服务配置”部分）。

## 开发与调试建议

为了提高代码质量并减少常见错误，建议在开发过程中使用以下工具：

- **Linter (如 Flake8, Pylint)**: 帮助检查代码风格和潜在的语法错误。
- **Formatter (如 Black, autopep8)**: 自动格式化代码，保持风格一致性。

这些工具可以集成到您的开发环境中，在编码时实时提供反馈。

## 🚀 部署到服务器 🚀

想让你的 AI 磁盘空间分析助手被更多人访问吗？把它部署到云服务器上是个好主意！这里，我们以华为云服务器为例，一步步教你怎么做。

#### 更新服务器并安装基本工具

登录服务器后，最好先更新一下系统软件包，并安装一些我们接下来会用到的基本工具，比如 `git`（用来下载代码）、`python3` 和 `pip`（用来运行我们的 Python 程序）。

以 Ubuntu 为例，运行以下命令：

```bash
# 更新软件包列表
sudo apt update

# 升级已安装的软件包
sudo apt upgrade -y

# 安装 git, python3, python3-pip 和 python3-venv (用于创建虚拟环境)
sudo apt install -y git python3 python3-pip python3-venv
```

对于 CentOS 或其他 Linux 发行版，命令会略有不同（例如使用 `yum` 而不是 `apt`）。你可以搜索“<你的Linux发行版名称> 安装 git python3 pip”来找到对应的命令。

### 3. 上传并配置 AI 磁盘分析助手

#### 获取项目代码

你有两种主要方式把项目代码弄到服务器上：

1.  **使用 Git 克隆 (推荐)**: 如果你的代码已经放到了像 GitHub、Gitee 这样的代码托管平台上，可以直接在服务器上克隆下来。
    ```bash
    git clone <你的代码仓库URL>
    cd Pycsstoai # 进入项目目录
    ```
2.  **手动上传**: 你可以把整个项目文件夹（比如 `Pycsstoai`）压缩成一个 `.zip` 文件，然后通过 SCP (Secure Copy Protocol) 或者 FTP (File Transfer Protocol) 工具上传到服务器上，再解压缩。
    *   例如使用 SCP (在你的本地电脑上运行，不是在服务器上):
        ```bash
        scp -r /path/to/your/local/Pycsstoai 用户名@你的服务器公网IP:/home/用户名/ # 将本地文件夹上传到服务器的用户主目录
        ```
        然后在服务器上解压 (如果上传的是压缩包)。

#### 创建虚拟环境并安装依赖

为了不和服务器上其他 Python 项目搞混，我们最好为这个AI助手创建一个独立的 Python 环境，这叫做“虚拟环境”。

在服务器的项目目录 (`Pycsstoai`) 里，运行：

```bash
# 创建一个名为 .venv 的虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 现在你的命令行提示符前面应该会有一个 (.venv) 标记
# 确保你的 requirements.txt 文件是最新的，并且在项目根目录中
# 安装项目依赖
pip install -r requirements.txt
```

#### 配置 AI API 密钥

为了保护您的 API 密钥不被意外上传到代码仓库，本项目采用了 `config.py.example` 的方式管理配置。

1.  **复制示例文件**：在 `src` 目录下，找到 `config.py.example` 文件，复制一份并将其重命名为 `config.py`。
2.  **填写您的密钥**：打开新创建的 `src/config.py` 文件，将 `YOUR_API_KEY_HERE` 替换为您真实的 API 密钥。根据需要，您也可以修改 `api_endpoint` 和 `model_name`。

```python
# src/config.py (修改后的示例)
class AIConfig:
    def __init__(self):
        # AI服务配置
        self.api_key = "sk-YourActualAPIKey"  # 替换为你的AI服务的API密钥
        self.api_endpoint = "https://api.siliconflow.cn/v1/chat/completions" 
        self.model_name = "Qwen/Qwen3-8B"  
        # ... 其他配置 ...
```

`config.py` 文件已被添加到 `.gitignore` 中，因此不会被 Git跟踪和上传。

和你在本地电脑上一样，AI 功能需要 API 密钥。你有以下几种方式在服务器上配置它：

1.  **环境变量 (推荐)**: 这是在服务器上配置密钥的最好方式。
    *   编辑你的 shell 配置文件，比如 `~/.bashrc` 或 `~/.zshrc` (取决于你用的 shell)：
        ```bash
        nano ~/.bashrc 
        ```
    *   在文件末尾添加你的 API 密钥信息 (具体变量名参考 `src/config.py` 或 `src/ai_analyzer.py` 中是如何读取的，例如 `OPENAI_API_KEY`):
        ```bash
        export OPENAI_API_KEY="sk-YourActualOpenAIKey"
        export OPENAI_BASE_URL="YourOptionalBaseURL"
        # 如果有其他模型的密钥，也类似添加
        # export MOONSHOT_API_KEY="sk-YourMoonshotKey"
        ```
    *   保存文件 (在 `nano` 中是 `Ctrl+O`，然后回车，再 `Ctrl+X` 退出)。
    *   让配置生效：
        ```bash
        source ~/.bashrc
        ```
    *   你可以通过 `echo $OPENAI_API_KEY` 来检查环境变量是否设置成功。
2.  **通过 `src/config.py` 文件**: 你也可以直接在服务器上编辑 `src/config.py` 文件，填入你的密钥。但这种方式不如环境变量安全，因为密钥会直接写在代码文件里。如果你选择这种方式，**强烈建议不要把包含真实密钥的 `config.py` 文件提交到公开的 Git 仓库中！** 你可以先在服务器上复制 `src/config.py.example` 为 `src/config.py`，然后编辑。

### 4. 运行 Streamlit 应用

一切准备就绪后，就可以在服务器上启动我们的 Streamlit 应用了！

在激活了虚拟环境的项目目录 (`Pycsstoai`) 中，运行：

```bash
streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0
```

解释一下这个命令：
*   `streamlit run src/app.py`: 这是标准的运行 Streamlit 应用的命令。
*   `--server.port 8501`: 指定应用监听的端口号。`8501` 是 Streamlit 的默认端口，你可以根据需要改成其他的，但要确保这个端口没被其他程序占用。
*   `--server.address 0.0.0.0`: 这非常重要！它让 Streamlit 应用监听所有可用的网络接口，也就是说，不仅仅是服务器自己 (localhost)，外部网络也能访问到它。**如果缺少这个参数，你可能只能在服务器内部访问，而无法从你的电脑浏览器通过公网IP访问。**

此时，应用应该已经在服务器上运行起来了。但如果你关闭 SSH 连接，应用也会跟着停止。我们需要让它在后台持久运行。

### 5. 让应用在后台持久运行

有几种方法可以让你的 Streamlit 应用在你断开 SSH 连接后继续运行：

1.  **使用 `nohup` (简单快捷)**:
    ```bash
    nohup streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0 > streamlit_app.log 2>&1 &
    ```
    *   `nohup`: 命令，表示 no hang up，即使终端关闭，命令也会继续执行。
    *   `> streamlit_app.log`: 把应用的正常输出重定向到 `streamlit_app.log` 文件。
    *   `2>&1`: 把错误输出也重定向到和正常输出一样的地方 (即 `streamlit_app.log`)。
    *   `&`: 让命令在后台运行。
    *   你可以通过 `cat streamlit_app.log` 查看应用的日志。
    *   要停止它，你需要找到它的进程 ID (PID)，然后用 `kill <PID>` 命令。可以用 `ps aux | grep streamlit` 来查找。

2.  **使用 `screen` 或 `tmux` (更灵活的会话管理)**:
    `screen` 和 `tmux` 是终端复用工具，它们可以让你创建持久的会话，即使 SSH 断开，会话和里面的程序也会继续运行。下次登录时可以重新连接到这个会话。
    *   **Screen 示例**:
        ```bash
        # 安装 screen (如果还没有的话)
        # sudo apt install screen (Ubuntu)
        # sudo yum install screen (CentOS)

        # 创建一个新的 screen 会话，名叫 myapp
        screen -S myapp

        # 在 screen 会话中，激活虚拟环境并运行 streamlit
        source .venv/bin/activate
        streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0

        # 现在你可以按 Ctrl+A 然后按 D 来“分离 (detach)”这个会话，程序会继续在后台运行。
        # 要重新连接，运行: screen -r myapp
        # 要彻底关闭，连接后按 Ctrl+C 停止 streamlit，然后输入 exit 关闭 screen 会话。
        ```
    *   `tmux` 的用法类似，但快捷键不同，功能更强大一些。

3.  **使用 `systemd` 服务 (更健壮和专业的做法)**:
    把 Streamlit 应用配置成一个系统服务，这样服务器开机时它可以自动启动，如果意外挂掉也能自动重启。这种方式配置起来稍微复杂一点，但更稳定可靠。
    *   创建一个服务文件，比如 `/etc/systemd/system/streamlit_app.service`:
        ```bash
        sudo nano /etc/systemd/system/streamlit_app.service
        ```
    *   填入以下内容 (记得修改 `User`, `WorkingDirectory`, `ExecStart` 中的路径为你自己的实际情况):
        ```ini
        [Unit]
        Description=AI Disk Space Analyzer Streamlit App
        After=network.target

        [Service]
        User=你的服务器登录用户名 # 例如 ubuntu, root, ecs-user
        WorkingDirectory=/path/to/your/Pycsstoai # 例如 /home/ubuntu/Pycsstoai
        ExecStart=/path/to/your/Pycsstoai/.venv/bin/streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0
        Restart=always # 或者 on-failure
        RestartSec=5s
        Environment="PYTHONUNBUFFERED=1"
        # 如果需要设置环境变量给 Streamlit 应用，可以在这里加，例如：
        # Environment="OPENAI_API_KEY=sk-YourKey"
        # Environment="STREAMLIT_SERVER_MAX_UPLOAD_SIZE=1024" # 比如设置最大上传文件大小为1GB

        [Install]
        WantedBy=multi-user.target
        ```
    *   保存并关闭文件。
    *   让 systemd 重新加载配置，并启动/启用你的服务：
        ```bash
        sudo systemctl daemon-reload
        sudo systemctl start streamlit_app  # 启动服务
        sudo systemctl enable streamlit_app # 设置开机自启
        sudo systemctl status streamlit_app # 查看服务状态
        sudo journalctl -u streamlit_app -f # 查看服务日志 (按 Ctrl+C 退出)
        ```

选择哪种方式取决于你的需求。对于初学者，`nohup` 或 `screen` 可能更容易上手。

### 6. 配置华为云安全组

即使你的 Streamlit 应用已经在服务器上运行并监听 `0.0.0.0`，默认情况下，云服务器的防火墙（在华为云上叫做“安全组”）可能仍然会阻止外部访问你指定的端口（比如 `8501`）。

你需要登录到你的华为云控制台，找到你的 ECS 实例，然后配置其关联的安全组规则：

1.  登录华为云管理控制台。
2.  导航到 “弹性云服务器 ECS”。
3.  找到你的目标服务器实例，点击实例名称进入详情。
4.  在左侧导航栏或实例详情页中找到 “安全组” 或 “网络与安全” -> “安全组” 的选项。
5.  选择你的实例正在使用的安全组，点击 “配置规则” 或 “修改规则”。
6.  在 “入方向规则” 中，点击 “添加规则”。
7.  配置如下：
    *   **优先级**: 默认即可 (通常是 1 到 100 之间的数字，越小优先级越高)。
    *   **策略**: 选择 “允许”。
    *   **协议类型**: 选择 “TCP”。
    *   **端口范围**: 输入你 Streamlit 应用使用的端口，例如 `8501` (如果只开放一个端口，起始和结束端口都填它；如果是范围，比如 `8500-8510`，则分别填写)。
    *   **源地址**: 
        *   为了让任何人都能访问，可以设置为 `0.0.0.0/0` (表示所有 IPv4 地址)。
        *   如果你只想让特定 IP 地址访问，可以填入具体的 IP 或 IP段。
        *   **注意安全风险**：`0.0.0.0/0` 会将端口暴露给整个互联网，请确保你的应用本身是安全的。
    *   **描述**: 可选，可以写一个方便自己识别的描述，比如 “Streamlit App Port”。
8.  点击 “确定” 保存规则。

规则添加后，通常会立即生效。现在，你应该可以通过 `http://你的服务器公网IP:端口号` (例如 `http://123.45.67.89:8501`) 来访问你的 AI 磁盘分析助手了！

### 7. （可选）进阶：使用域名和 HTTPS

如果你想用一个好记的域名（比如 `myanalyzer.example.com`）而不是 IP 地址来访问，并且希望通过 HTTPS 加密连接来提高安全性，你通常需要：

1.  **注册一个域名**。
2.  **配置 DNS 解析**，把你的域名指向服务器的公网 IP。
3.  **在服务器上安装一个 Web 服务器软件**，如 Nginx 或 Apache，作为反向代理。
4.  **配置反向代理**，把来自域名的请求转发到你的 Streamlit 应用 (运行在 `localhost:8501` 上)。
5.  **获取并配置 SSL/TLS 证书** (例如使用 Let's Encrypt 的免费证书) 来启用 HTTPS。

这部分内容相对复杂，可以作为后续的优化步骤。

### 8. 更新和维护

*   **更新代码**: 如果你更新了本地的代码并推送到了 Git 仓库，你需要在服务器上 `git pull` 来获取最新代码，然后可能需要重启 Streamlit 应用 (如果是用 `systemd`，就是 `sudo systemctl restart streamlit_app`)。
*   **查看日志**: 定期检查应用的日志 (比如 `streamlit_app.log` 或通过 `journalctl`)，可以帮助你发现和解决问题。
*   **依赖更新**: 偶尔也需要在服务器的虚拟环境中更新依赖包 (`pip install -r requirements.txt --upgrade`)。

部署 Web 应用是一个涉及多个环节的过程，遇到问题是很正常的。多尝试，多搜索，你会成功的！祝你的 AI 磁盘分析助手顺利上线！


## 注意事项

*   **CSV 文件格式**: 
    *   程序主要针对 WizTree 导出的标准 CSV 格式进行了优化。请确保您的 CSV 文件包含可识别的列名，特别是关于文件路径（如 “文件名称”、“Path”）和文件大小（如 “大小”、“Size”）的列。
    *   如果程序提示找不到关键列（如 'Path'、'File Name' 或 'Size'），请检查您的 CSV 文件格式是否正确，或者列名是否与程序预期的有所不同。程序在无法找到 'Path' 列时，会尝试使用 'File Name' 列作为替代。
*   **AI API 密钥**: 
    *   AI 分析功能依赖于大语言模型服务。您需要在 `src/config.py` 文件中配置好您的 API 密钥，或者设置相应的环境变量。具体请参考 `src/config.py.example` 文件。
    *   如果未配置 API 密钥，AI 相关的功能将无法正常使用，但基础的磁盘数据统计和展示功能仍然可用。
*   **数据量与性能**: 
    *   处理非常大的 CSV 文件（例如包含数百万条目）可能会消耗较多时间和内存。程序在设计时已考虑优化，但极端情况下仍需耐心等待。
    *   AI 分析部分为了避免超出 API 的 token 限制，会选择性地发送数据摘要或部分数据（如最大的文件列表）给 AI。

## 故障排除

- **CSV 文件导入与解析**:
    - 支持通过图形界面选择 WizTree 导出的 CSV 文件。
    - 尝试多种编码 (UTF-8, GBK, Latin1) 以提高文件兼容性。
    - **重要提示：** 程序设计为自动跳过 WizTree CSV文件的第一行（通常是WizTree的生成信息），直接从第二行开始读取数据和表头。请确保您的CSV文件符合此格式。
    - 请确保您的 CSV 文件从第二行开始包含有效的数据列，特别是用于分析大小的列（如 'Size' 或 '大小'）以及文件/文件夹名称 ('File Name') 和路径 ('Path') 信息。
- **基本数据统计**:
    - 显示扫描文件的总大小 (尝试基于WizTree CSV中根目录条目的大小进行计算，以避免重复统计，并动态显示单位如KB, MB, GB, TB)。
    - 显示扫描到的总文件/文件夹数量。
- **大文件/文件夹识别**:
    - 列出占用空间最大的 Top 10 条目 (可能是文件或文件夹，基于WizTree的输出)。
    - 显示每个条目的完整路径和大小 (动态显示单位如KB, MB, GB, TB)。
- **文件类型分析**:
    - 根据文件扩展名自动分类文件。
    - 预设分类包括：图片, 视频, 音频, 文档, 压缩包, 应用程序, 系统/缓存, 其他, 无扩展名/文件夹。
    - 统计每个分类下的文件总大小 (动态显示单位如KB, MB, GB, TB)、条目数量以及占总空间大小的百分比。
- **控制台输出**: 
    - 所有分析结果清晰地打印在控制台/终端窗口。
- **按类型或后缀名查询文件 (新增)**:
    - 能够根据文件分类（如“图片”、“视频”）或文件扩展名（如“jpg”、“exe”）查询并列出匹配的文件及其路径和大小。
    <!-- - **使用方法 (当前版本)**: 此功能已在 `src/main.py` 文件中的 `query_files_by_type_or_extension` 函数实现。开发者可以在 `main` 函数中取消注释并修改示例代码来调用此查询功能。例如，查询所有“视频”文件：`query_files_by_type_or_extension(csv_data, 'category', '视频')`；查询所有扩展名为 `exe` 的文件：`query_files_by_type_or_extension(csv_data, 'extension', 'exe')`。 -->

## AI 服务配置

为了让AI分析功能真正运作（而不仅仅是显示模拟/占位符的回复），您需要配置AI服务。这主要通过编辑项目中的 `src/config.py` 文件来完成。

1.  **获取API密钥**：您需要从某个AI服务提供商那里获取一个API密钥。常见的提供商有OpenAI (提供GPT系列模型), Google (Gemini), Anthropic (Claude), SiliconFlow 等。具体获取方式请参考对应服务商的官方文档。

2.  **编辑配置文件**：打开 `src/config.py` 文件。您会看到类似下面的内容：
    ```python
    # src/config.py

    class AIConfig:
        def __init__(self):
            # AI服务配置
            self.api_key = None  # 在这里填入您的AI服务的API密钥
            self.api_endpoint = None  # 如果需要，填入AI服务的API端点
            self.model_name = "Qwen/Qwen3-8B"  # 默认使用的AI模型，您可以根据需要修改
            
            # 其他配置项
            self.max_tokens = 1000  # 每次请求的最大token数
            self.temperature = 0.7  # AI回复的创造性程度（0-1）
            
        # ... (其他方法)

    # 创建全局配置实例
    ai_config = AIConfig()
    ```
    您需要修改 `self.api_key` 的值为您获取到的API密钥。如果您的服务商提供了特定的API端点，也请相应修改 `self.api_endpoint`。您还可以根据需要调整 `self.model_name`、`self.max_tokens` 和 `self.temperature` 等参数。

    **示例：**
    ```python
    class AIConfig:
        def __init__(self):
            self.api_key = "sk-yourActualApiKeyHere12345"
            self.api_endpoint = "https://api.example.com/v1/chat/completions"
            self.model_name = "gpt-4-turbo"
            # ...
    ```

如果 `api_key` 未在 `src/config.py` 中配置，AI分析功能将返回提示信息，告知服务未配置。在这种情况下，程序可能使用**模拟/占位符**的AI响应（取决于具体实现），或者直接提示配置错误。这意味着您仍然可以看到功能如何工作，但得到的分析结果可能不是真实的AI分析。为了获得有意义的AI洞察，请确保正确配置API密钥。

## 文档

- [产品需求文档 (PRD)](./docs/PRD.md)
- [产品路线图 (Roadmap)](./docs/Roadmap.md)
- [用户故事地图 (User Story Map)](./docs/User_Story_Map.md)
- [产品评估指标框架 (Metrics Framework)](./docs/Metrics_Framework.md)

## 未来展望与可能的改进方向

*   **更智能的列名识别**：
    *   **当前**：程序主要依赖固定的中文（“文件名称”、“大小”、“路径”）和英文（“File Name”, “Size”, “Path”）列名，并在“Path”列缺失时尝试使用“文件名称”列。如果用户导出的CSV列名有细微差异（比如多了空格，或者使用了其他相近的词语），可能无法正确识别。
    *   **改进设想**：引入更灵活的列名匹配机制。例如，可以使用模糊匹配或正则表达式来识别可能代表文件路径、文件大小的列。或者，在列名不完全匹配时，给用户一个选择界面，让他们手动指定哪个CSV列对应哪个数据项（如“请选择代表文件路径的列：”）。
*   **交互式图表与筛选**：引入更高级的交互式图表库（如 Plotly Express, Bokeh），允许用户在图表上进行缩放、筛选、点击查看详情等操作。
*   **历史数据对比**：支持导入多次扫描的CSV文件，并对它们进行对比，分析文件和文件夹大小随时间的变化趋势。
*   **自定义清理规则**：允许用户设置自定义规则来识别冗余文件（例如，查找重复文件、特定时间范围内的临时文件等）。
*   **用户界面优化**：持续改进用户界面的美观性和易用性，提供更友好的用户体验，特别是对于不太懂技术的用户。
*   **更深入的AI集成**：探索更多AI应用场景，例如根据文件内容（如果可能获取摘要）进行分类、自动生成文件夹整理建议等。
*   **错误处理与用户引导**：当CSV文件格式不符合预期，或缺少关键信息时，提供更清晰、更具指导性的错误提示和解决建议，帮助用户快速定位并解决问题。

## 项目总结与展望 (V0.1)

### 当前状态总结

AI 磁盘空间分析助手 (Pycsstoai) 当前版本 (V0.1) 已经成功实现了以下核心功能：

1.  **CSV 数据导入与处理**：
    *   通过 `tkinter` 图形界面引导用户选择 WizTree 导出的 CSV 文件。
    *   支持多种文件编码 (UTF-8, GBK, Latin1) 以增强兼容性。
    *   自动跳过 WizTree CSV 文件的元数据行，直接读取数据。
    *   对列名进行标准化处理（例如，将 '文件名称' 统一为 'File Name'，'大小' 统一为 'Size'）。
    *   对 'Size' 列进行数值转换和空值处理。
2.  **核心数据分析**：
    *   计算并展示扫描的总文件/文件夹数量和总占用空间（动态格式化单位）。
    *   识别并列出占用空间最大的 Top N (默认为20) 个文件或文件夹，显示其路径和大小。
    *   **文件分类统计**：根据预设的类别（图片、视频、文档等）对文件进行归类，并统计每个类别的总大小、文件数量及占总空间的百分比。
    *   **文件扩展名统计**：统计不同文件扩展名的总大小，并列出 Top N (默认为20) 的扩展名及其占用空间。
    *   所有分析结果通过控制台清晰输出。
3.  **AI 分析集成 (初步)**：
    *   集成了 `AIAnalyzer` 类，能够接收分析结果的摘要信息，并（在配置真实AI服务后）调用AI进行磁盘使用摘要分析和文件清理建议。
    *   提供了通过 `src/config.py` 文件配置 AI 服务 API 密钥和模型参数的机制。
    *   目前若未配置真实AI服务，则使用占位符/模拟AI响应。
4.  **模块化设计**：
    *   代码结构清晰，主要逻辑分布在 `src/main.py` (主流程、数据分析)、`src/ai_analyzer.py` (AI分析逻辑) 和 `src/config.py` (配置管理)。
    *   定义了 `AnalysisResult` 类来结构化存储分析结果，便于传递和处理。

### 交互性现状与改进思考

**当前交互方式**：

*   **输入**：通过 `tkinter` 实现的简单文件对话框选择 CSV 文件。
*   **输出**：所有分析结果和 AI 建议均直接打印到命令行控制台。

这种方式对于开发者或有技术背景的用户是可行的，但对于普通用户（尤其是您提到的初中生用户）来说，交互性较弱，不够直观友好。

**交互性改进方向**：

为了提升用户体验，特别是让不熟悉代码的用户也能轻松使用，可以考虑以下几个方向来增强交互性：

1.  **图形用户界面 (GUI) 展示**：
    *   **方案一 (轻量级)**：扩展使用 `tkinter`，创建一个简单的主窗口来展示分析结果。例如，可以使用列表框、文本区域或者简单的图表（如条形图）来可视化显示最大的文件、文件类型分布等。
    *   **方案二 (更现代的GUI)**：考虑使用如 `PyQt` 或 `Kivy` 等更强大的GUI库，但这会增加项目的复杂度和依赖。
2.  **Web 应用界面**：
    *   **方案一 (简单快速)**：使用 `Streamlit` 或 `Flask` 快速搭建一个本地 Web 应用。用户在浏览器中上传 CSV 文件，分析结果以更丰富的形式（表格、图表、交互式元素）展示在网页上。这种方式跨平台性好，界面也更容易做得美观。
    *   **优势**：可以更容易地集成交互式图表库（如 Plotly, Bokeh），提供更动态的数据探索体验。
3.  **交互式命令行 (增强型)**：
    *   如果暂时不引入完整的GUI或Web界面，也可以考虑使用像 `rich` 或 `prompt_toolkit` 这样的库来美化命令行输出，增加颜色、表格、进度条等，并提供更友好的交互式查询选项。

**初步建议**：

考虑到用户的技术背景和快速实现友好界面的需求，**使用 `Streamlit` 构建一个简单的 Web 应用**可能是一个不错的选择。Streamlit 学习曲线相对平缓，能够快速将 Python 数据分析脚本转化为可交互的 Web 应用，非常适合展示数据和图表。

### 下一阶段规划 (V0.2 - 交互性提升)

基于以上思考，下一阶段 (V0.2) 的主要目标可以设定为：

1.  **引入交互式用户界面**：
    *   **核心任务**：选择一种方案（初步推荐 Streamlit）来实现图形化/Web化的用户界面。
    *   **界面功能**：
        *   允许用户通过界面上传 CSV 文件。
        *   清晰展示 `main.py` 中已有的各项分析结果（总览、大文件列表、分类统计、扩展名统计）。
        *   （可选）以图表形式（如饼图、条形图）可视化文件类型分布和扩展名分布。
        *   展示 AI 分析师的摘要和清理建议。
2.  **AI 功能完善与测试**：
    *   鼓励用户配置真实的 AI 服务 API 密钥，并测试 AI 分析功能的实际效果。
    *   根据测试结果，优化传递给 AI 的提示信息 (prompts)，以获得更准确、更有用的分析和建议。
3.  **错误处理与用户引导**：
    *   在界面中提供更友好的错误提示和操作指引。
4.  **文档更新**：
    *   更新 `README.md` 和其他相关文档，说明新界面的使用方法。

通过这些改进，AI 磁盘空间分析助手将变得更加易用和实用，特别是对于非技术用户。