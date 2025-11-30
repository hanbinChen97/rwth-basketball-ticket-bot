Hanbin，这个**Iterative Development** (迭代开发) 的思路非常专业。对于爬虫这种高度依赖目标网站结构的任务，"Fetch -\> Analyze -\> Implement" 的流程是最稳健的。

既然你指定了 `uv` 和具体的项目结构，我们把这个任务拆解成 3 个阶段的 Prompt。你可以按顺序发给 AI。

-----

### 📂 推荐的项目结构 (Project Structure)

在开始之前，你可以先让 AI 帮你搭建这个脚手架。

```text
my_ticket_bot/
├── pyproject.toml       # uv 管理依赖
├── uv.lock
├── config/
│   └── settings.toml    # 存放 URL, 目标时间, 表单填写的 User Info
├── data/                # 存放抓取下来的 HTML (用于调试/分析)
│   └── debug_page.html
└── src/
    ├── __init__.py
    ├── fetcher.py       # 负责网络请求 (GET/POST)
    ├── parser.py        # 负责解析 HTML (BS4)
    └── main.py          # 调度逻辑
```

-----

### 🚀 Step 1: 环境搭建 & 基础抓取 (Setup & Fetch)

**目标**：初始化项目，配置 `uv`，并把目标网页原本原样地保存到本地，供下一步分析。

**Copy this Prompt to AI:**

> I am starting a Python project using `uv` for package management. I need to set up the environment and write a script to save a webpage for offline analysis.
>
> **Requirements:**
>
> 1.  **Environment:** Python 3.12+, managed by `uv`. Dependencies: `httpx`, `beautifulsoup4`, `loguru`, `toml` (or `tomli` if needed).
> 2.  **Structure:**
>       * `config/settings.toml`: Store `TARGET_URL` and `USER_HEADERS` (User-Agent, etc.).
>       * `src/fetcher.py`: A script that uses `httpx.Client` to visit `TARGET_URL` and save the raw HTML content to `data/debug_page.html`.
> 3.  **Action:**
>       * Provide the content for `pyproject.toml` (commands to add dependencies).
>       * Provide the code for `config/settings.toml` with dummy data.
>       * Provide the code for `src/fetcher.py`. It must handle basic errors (e.g., 404, 500) and log using `loguru`.

-----

### 🔍 Step 2: 静态分析 & 提取策略 (Analyze & Parse)

**目标**：你运行了 Step 1 的代码，拿到了 `data/debug_page.html`。现在把这个 HTML 文件的关键片段（或者告诉 AI 你观察到的结构）发给 AI，让它写解析器。

**Copy this Prompt to AI:**

> Now I have the webpage HTML saved in `data/debug_page.html`. I need a parser to extract the necessary form data.
>
> **Task:**
> Write `src/parser.py`. It should read the local `data/debug_page.html` file (offline mode) and use `BeautifulSoup` to:
>
> 1.  Find the main booking `<form>`.
> 2.  Extract the `action` URL (where to POST).
> 3.  **Crucial:** Extract all `<input type="hidden">` fields (names and values), as these usually contain CSRF tokens or ViewStates.
> 4.  Identify the inputs where I need to fill in my user data (e.g., matching "Name", "Phone" in labels).
>
> **Output:**
> A function `parse_booking_form(html_content)` that returns a dictionary containing the `action_url` and a `payload` dict (merged hidden tokens + placeholders for user data). Print the result to the console so I can verify the extracted tokens.

*(注意：在执行这一步时，如果 Step 1 抓下来的 HTML 过于复杂，你可以把 HTML 中 `<form>` 相关的部分复制一段贴在 Prompt 后面给 AI 参考)*

-----

### ⚡ Step 3: 整合 & 发送请求 (Integration & Action)

**目标**：解析器写好了，现在要结合 Config 里的真实数据，完成“定时 + 填表 + 提交”的闭环。

**Copy this Prompt to AI:**

> The parser is working. Now I need the main execution logic in `src/main.py` to automate the booking process.
>
> **Logic Flow:**
>
> 1.  **Load Config:** Read `TARGET_TIME`, `USER_DATA` (my real details), and `TARGET_URL` from `config/settings.toml`.
> 2.  **Wait:** Implement a lightweight loop checking system time. When current time \>= `TARGET_TIME`, proceed immediately.
> 3.  **Fetch Live:** Use `src/fetcher.py` logic to get the *live* page (refreshing just as the time hits).
> 4.  **Parse:** Pass the live HTML to `src/parser.py` to get fresh tokens.
> 5.  **Merge:** Update the extracted payload with `USER_DATA` from config.
> 6.  **Submit:** Use `httpx` to POST the data to the `action_url`.
>
> **Requirements:**
>
>   * Use `httpx.Client` (or `AsyncClient` if you recommend it for speed) to maintain cookies between the GET (fetch form) and POST (submit) steps. This is critical.
>   * Log the server's response code and body to verify success.

-----

### 💡 给你的开发建议 (Dev Tips)

1.  **Config First**: 把所有会变的东西（URL, 抢票时间, 你的身份证/姓名）都放在 `config/settings.toml` 里。这样你调整策略时不需要改代码。
2.  **Dry Run (空跑)**: 在 Step 3 完成后，先不要等到 3 点钟。找一个无关紧要的时间（比如 2:00），把 `TARGET_TIME` 设为当前时间，跑一次看看能不能提取到 Token 并发送请求（虽然会失败，但能看到服务器返回什么，比如 "Not Open Yet" 还是 "403 Forbidden"）。
3.  **Cookie Persistence**: 如果网站需要登录，你可能需要在 `config` 里加一个 `COOKIE_STRING` 字段，直接把浏览器里登录好的 Cookie 复制进去，然后在 `src/fetcher.py` 初始化 headers 时带上。这是最简单的过验证方法。