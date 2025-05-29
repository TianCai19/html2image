# HTML 逐页截图工具 (HTML Page-by-Page Screenshot Tool)

## 1. 项目简介 (Project Introduction)

本项目是一个 Python 脚本套件，旨在使用 Playwright 自动化截取指定 HTML 文件（特指 `爱的法宝phone.html` 或其他类似结构的单页应用）中各个主要区块（被视为独立“页面”）的屏幕截图。该工具特别为模拟手机版式进行设计，允许用户通过配置文件选择或自定义不同的手机设备参数（如视口大小、User Agent、缩放比例等）来捕获内容，包括为小红书等社交媒体平台优化的特定尺寸。

这些截图可以用于多种目的，例如：
* 快速预览长篇幅 HTML 内容在不同移动设备上的各个部分。
* 为演示文稿或文档生成符合特定设备或平台要求的视觉材料。
* 内容存档和版本比较。
* 自动化测试网页在多种移动设备上的视觉展现。

目标 HTML 文件应采用适合逐屏滚动的结构，例如 CSS `scroll-snap` 和 `height: 100vh` 的页面设计，使得每个主要内容区块在滚动时都能完整占据视口。

## 2. 技术栈 (Technology Stack)

* **主要编程语言 (Main Language):** Python (3.7+)
* **核心自动化库 (Core Automation Library):** Playwright
    * 用于浏览器控制、页面导航和屏幕截图功能。
* **浏览器引擎 (Browser Engine):** Chromium (Playwright 默认支持，也可配置为 Firefox 或 WebKit)
* **异步处理 (Asynchronous Processing):** `asyncio` (Python 内置库，Playwright 的异步 API 依赖此库)
* **配置文件格式 (Configuration File Format):** JSON (用于设备参数定义)
* **目标文件格式 (Target File Format):** HTML, CSS
* **运行环境 (Operating System):** 跨平台 (Windows, macOS, Linux)

## 3. 项目结构 (Project Structure)

```
project_root/
├── screenshot_tool.py          # 主截图脚本
├── generate_device_configs.py  # 生成设备配置文件的脚本
├── 爱的法宝phone.html          # 示例 HTML 文件
├── configs/
│   └── devices/                # 存放设备配置JSON文件
│       ├── iphone_x.json
│       ├── pixel_5.json
│       ├── xiaohongshu_3_4_1080p.json
│       └── ... (其他设备配置文件)
├── screenshots/                # 默认截图输出目录
└── README.md                   # 本说明文件
```

## 4. 安装与配置 (Installation and Configuration)

### 4.1 前提条件 (Prerequisites)

1.  **安装 Python:** 请确保您已安装 Python 3.7 或更高版本。
2.  **安装 Playwright:**
    ```bash
    pip install playwright
    ```
3.  **安装 Playwright 浏览器驱动:**
    ```bash
    playwright install chromium  # 或 playwright install 来安装所有支持的浏览器
    ```

### 4.2 生成设备配置文件 (Generate Device Configurations)

本项目包含一个脚本 `generate_device_configs.py` 用于创建一系列预设的手机设备配置文件。这些文件（JSON格式）存储在 `configs/devices/` 目录下，主截图脚本将使用它们来模拟不同的设备。

1.  **运行生成脚本:**
    ```bash
    python generate_device_configs.py
    ```
    此脚本会根据预定义的列表（包括常见的 iPhone、Pixel 型号以及为小红书优化的特定尺寸如 3:4、9:16、1:1）生成相应的 `.json` 配置文件。您可以查看或修改此脚本以添加更多自定义设备。

### 4.3 运行截图脚本 (Running the Screenshot Script)

主脚本 `screenshot_tool.py` 用于执行实际的截图操作。

1.  **准备文件:**
    * 确保您的目标 HTML 文件 (例如 `爱的法宝phone.html`) 已放置在项目中。
    * 确保已运行 `generate_device_configs.py` 并生成了设备配置文件。
2.  **查看可用设备 (可选):**
    您可以使用 `--list-devices` 参数来查看 `configs/devices/` 目录下所有可用的设备配置名称：
    ```bash
    python screenshot_tool.py --list-devices
    ```
    (注意：在 `list-devices` 模式下，`html_file` 参数是可选的。)
3.  **执行截图:**
    使用以下命令格式运行截图脚本：
    ```bash
    python screenshot_tool.py <html_file_path> --device <device_name> [--output-dir <output_directory>]
    ```
    * `<html_file_path>`: 必需，您的目标 HTML 文件路径 (例如 `爱的法宝phone.html`)。
    * `--device <device_name>`: 必需，要模拟的设备名称。此名称对应 `configs/devices/` 目录下 JSON 文件名（不含 `.json` 后缀，例如 `iphone_x` 或 `xiaohongshu_3_4_1080p`）。
    * `--output-dir <output_directory>`: 可选，指定保存截图的目录。默认为 `screenshots/`。

    **示例命令:**
    * 使用 iPhone X 配置截图：
        ```bash
        python screenshot_tool.py 爱的法宝phone.html --device iphone_x
        ```
    * 使用为小红书优化的 3:4 尺寸配置，并指定输出目录：
        ```bash
        python screenshot_tool.py 爱的法宝phone.html --device xiaohongshu_3_4_1080p --output-dir ./my_xhs_shots
        ```

    **示例截图:**

    | iPhone X 示例 | 小红书 3:4 示例 |
    |---|---|
    | <img src="./screenshots/iphone_x_slide-hero.png" alt="iPhone X Screenshot" width="400"> | <img src="./screenshots/xiaohongshu_3_4_1080p_slide-hero.png" alt="Xiaohongshu 3:4 Screenshot" width="400"> |

4.  **查看结果:** 脚本执行完毕后，截图将保存在指定的输出目录中。截图文件名将包含设备名称和页面ID/索引 (例如 `iphone_x_slide-hero.png`)。

## 5. 当前功能 (Current Features)

* 自动从本地文件系统加载指定的 HTML 文件。
* **可配置的设备模拟:** 通过 `configs/devices/` 目录下的 JSON 文件灵活定义和选择模拟的移动设备参数（视口、User Agent、缩放因子等）。
* **设备配置生成:** 提供 `generate_device_configs.py` 脚本，方便地从 Playwright 内置设备列表和自定义模板生成配置文件。
* **预置常用及特定平台配置:** 默认包含多种常见手机型号及为小红书优化的特定尺寸（如 3:4, 9:16, 1:1）配置。
* **命令行参数支持:**
    * `--list-devices`: 列出所有可用的设备配置。
    * `--device`: 指定使用的设备配置。
    * `--output-dir`: 自定义截图保存位置。
* 准确识别 HTML 文件中定义的每个独立页面/区块 (通过 `.slide` CSS 类选择器)。
* 通过滚动操作，确保每个页面在其截图前完整可见。
* 为每个识别出的页面截取 PNG 格式的屏幕截图。
* **带设备信息的截图命名:** 截图文件名包含所用设备配置的名称，方便区分不同设备下的截图结果。

## 6. 自定义设备配置 (Customizing Device Configurations)

如果您需要当前预设之外的设备配置，可以通过以下方式添加：

1.  **编辑 `generate_device_configs.py`:**
    * 在脚本中找到 `CUSTOM_GENERIC_MOBILE` 或 `CUSTOM_XIAOHONGSHU_DEVICES` 这样的字典。
    * 您可以向这些字典中添加新的设备条目，或者创建新的类似字典。每个条目应包含 `name` (描述性名称), `user_agent`, `viewport` (`width`, `height`), `device_scale_factor`, `is_mobile`, `has_touch` 等 Playwright `browser.new_context()` 支持的参数。
    * 确保将新设备配置的键名（例如 `my_custom_device`）添加到 `DEVICES_TO_GENERATE` 列表中。
    * （可选）如果创建了新的自定义字典，请确保它被合并到 `all_potential_devices` 变量中。
2.  **重新运行 `generate_device_configs.py`:**
    ```bash
    python generate_device_configs.py
    ```
    这将在 `configs/devices/` 目录下生成您新定义的设备配置文件。
3.  之后，您就可以在 `screenshot_tool.py` 中通过 `--device <your_new_device_key>` 来使用它了。

## 7. 未来展望与可完善之处 (Future Improvements)

* **更高级的配置选项:**
    * 允许通过主脚本的单个配置文件来管理所有参数（HTML源、设备选择、输出等）。
    * 支持更多截图格式 (JPEG, WebP) 和质量调整。
* **更灵活的页面元素定义:** 允许用户通过命令行参数或配置文件传入自定义的 CSS 选择器来定义哪些元素应被视为“页面”。
* **交互模拟与状态捕获:** 在截图前执行预定义的 JavaScript 或模拟用户交互。
* **支持远程 URL:** 直接从网络 URL 加载并截图网页内容。
* **批量处理能力:** 支持输入多个 HTML 文件路径或 URL 进行批量截图。
* **GUI 界面:** 为非技术用户开发一个简单的图形用户界面。
* **特定元素截图:** 增加只截取页面内某个特定元素的功能。
* **PDF 报告生成:** 将所有截取的图片按顺序合并成一个 PDF 文件。
* **与 CI/CD 集成:** 方便集成到自动化测试或文档生成流程中。

---

希望这份更新后的 README 对您项目的理解和使用更有帮助！