# 弹幕控制器 - README

游戏示例为黑神话悟空

注：本README文件由AI生成，仅供对软件的了解和参考。

本项目基于 Python 与 `tkinter` 实现了一个图形化应用，可实时连接到 Bilibili 直播间抓取弹幕，并按照预设规则将弹幕内容转换为本地键盘或鼠标指令。可应用于“观众控制游戏”、“远程协作演示”等互动场景。

---

## 功能概要

1. **直播间弹幕连接**  
   - 通过输入 Bilibili 直播间房间号（纯数字）建立实时连接，获取最新弹幕。

2. **指令映射与执行**  
   - 程序会将符合设定关键词的弹幕解析为具体操作，如移动、技能释放、连击等。

3. **延迟范围可调**  
   - 在 GUI 中设置“最小延迟”和“最大延迟”（单位：毫秒），程序将在此范围内随机等待后再抓取下一条弹幕，以控制频率。

4. **首次弹幕可忽略**  
   - 默认忽略连接成功后接收到的第一条弹幕，避免历史弹幕或瞬时刷屏的误触发。

5. **日志记录**  
   - 在当前目录下自动创建 `logs` 文件夹，记录程序运行信息、弹幕内容和执行情况，便于后期追踪或排错。

6. **查看操作指南**  
   - 点击“查看操作指南”按钮，可在新窗口中查看 `guide.md` 文件（内含所有弹幕指令及示例）。
7. **程序说明**
   - 由于直播延迟原因此程序并不能作为云操作游戏使用。代码非常简单，属于整活专用软件。
---

## 快速开始

1. **安装依赖**  
   - 确保已安装 Python 3.x。  
   - 在项目目录下执行：  
     ```bash
     pip install -r requirements.txt
     ```
   - 或根据需要手动安装：  
     ```bash
     pip install pyautogui websocket-client
     ```

2. **运行程序**  
   - 命令行进入项目目录，执行：  
     ```bash
     pyinstaller --onefile --noconsole --add-data "guide.md;." --icon "icon.ico" main.py
     ```
   - 若打包成可执行文件，直接双击运行即可。

3. **输入房间号并连接**  
   - 程序启动后，在主界面“房间号”输入框中输入对应的直播间ID（数字），如 `123456`;  
   - 点击 “开始连接” 按钮，若连接成功，主界面状态会变更为“连接成功”。

4. **操作指南**  
   - 若需查看可用弹幕指令及示例，可点击主界面 “查看操作指南” 按钮，将打开内置的 `guide.md` 文件。

5. **停止连接**  
   - 监听过程中，可随时点击 “停止连接” 按钮终止弹幕抓取；  
   - 再次连接时，可重新点击“开始连接”。

---

## 文件结构简述
# 程序整合入口
main
# 逻辑控制,修改这个即可改变游戏
controller.py 
# 弹幕抓取实现（WebSocket/HTTP）
danmu.py 
# 日志处理模块 
logHandler.py 
# 弹幕指令说明文件（操作指南） 
guide.md




# 所需依赖包列表
controller.py 
- `controller.py`：**核心入口**，启动 GUI、配置日志、管理弹幕监听线程。  
- `danmu.py`：封装了弹幕抓取逻辑，负责与 Bilibili 服务器进行通信。  
- `logHandler.py`：写入日志文件，处理错误信息等。  
- `guide.md`：供最终用户查看的指令说明（弹幕关键词与操作映射）。  

---

## 常见问题

1. **连接失败**  
   - 请确认网络状况和房间号有效性；若使用代理或防火墙，可尝试关闭后重试。

2. **键鼠操作无效**  
   - 在某些操作系统（尤其 macOS）可能需要开启“辅助功能”权限，以允许模拟键鼠输入。

3. **无法生成日志文件**  
   - 检查程序当前目录下是否有 `logs` 文件夹；若无则手动创建或确认是否有写权限。

4. **guide.md 加载失败**  
   - 若使用 PyInstaller 打包，请确认 `guide.md` 被正确打包或能在解压路径下访问。

5. **第一次弹幕未执行**  
   - 这是正常设计，为避免历史弹幕干扰；可在源代码中修改 `first_danmu_ignored` 的初始值。

---

## 贡献 & 反馈

若需扩展指令或自定义逻辑，请查看源码内注释并按需修改。例如在 `controller.py` 或 `handle_danmu_action.py` 中增添新的弹幕映射。

遇到问题可提交 [Issue](#)（若在 GitHub 等平台）或通过邮件2595615006@qq.com
联系客服，欢迎贡献与建议！
