# MyDouban —— 个人书影音标记站

自托管的个人「豆瓣」：标记电影、书、日本动画、BBC 纪录片、YouTube 视频、灵活就业调研等任何内容。

- **程序**：[Wiki.js 2](https://js.wiki/)（免费开源，完整中文界面）
- **存储**：每个页面就是本仓库里的一个 Markdown 文件，目录可分层级
- **同步**：Wiki.js 原生 Git 双向同步——网页上编辑自动 push 到 GitHub；在电脑上改了 push 上来，wiki 几分钟内自动更新
- **部署**：fnOS（飞牛OS）Docker Compose，见下文

## 目录结构

```
home.md                      首页（Wiki.js 默认主页路径是 /home）
movies.md                    🎬 电影：想看 / 在看 / 已看
books.md                     📖 书：想读 / 在读 / 已读
anime/
  watchlist.md               🗾 日本动画标记
  2024.md  2025.md           历年佳作评分对照（MAL/Bangumi/Filmarks/Anikore/豆瓣）
documentary/
  watchlist.md               🌍 纪录片标记
  bbc-nature.md              BBC 高分自然纪录片大全（60+ 部）
youtube/
  videos.md                  ▶️ YouTube 视频标记
  geography-now.md           Geography Now 全集追踪（579 集，含已看标记）
  lei-adventure.md           冒险雷探长 全集追踪（487 集，含已看标记）
  yuege-movies.md            越哥说电影 全集追踪（536 集）
scripts/
  sync_channels.py           刷新频道新视频用（yt-dlp，不是 wiki 页面）
  anime/                     生成历年动画评分对照表的工具（MAL/Bangumi/Filmarks 抓取）
archive/
  *.db                       原 SQLite tracker 数据库存档（已迁移至 youtube/ 下的 md）
career/
  bay-area-flexible-jobs.md  💼 湾区灵活就业种类大全
templates/
  item.md                    📋 条目格式模板
```

约定：**文件路径用英文，页面标题用中文**（写在 frontmatter 的 `title` 里）。Wiki.js 的 Git 同步对非 ASCII 文件名兼容性不佳，这样最稳。

## 一、部署 Wiki.js（fnOS）

1. fnOS 打开 **Docker → 项目(Compose) → 新建项目**，名称 `wikijs`，粘贴本仓库的 `docker-compose.yml`，启动；
2. 浏览器访问 `http://NAS的IP:8020`，进入安装向导：
   - 语言选 **简体中文**；
   - 设置管理员邮箱和密码；
   - Site URL 填 `http://NAS的IP:8020`；
3. 登录后如界面还是英文：**Administration → Locale** → 下载并选择 `Chinese (Simplified)`。

## 二、配置 GitHub 双向同步

1. 在 GitHub 创建访问令牌：**Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**
   - Repository access：只勾选 `voyagerzxj/MyDouban`
   - Permissions：**Contents → Read and write**
   - 生成后复制令牌（只显示一次）；
2. Wiki.js **管理区 → 存储 → Git**，启用并填写：

   | 配置项 | 值 |
   |---|---|
   | 认证类型 | `basic` |
   | 仓库 URI | `https://github.com/voyagerzxj/MyDouban.git` |
   | 分支 | `main` |
   | 用户名 | `voyagerzxj` |
   | 密码 / PAT | 上一步生成的令牌 |
   | 默认作者邮箱 | `voyagerzxj@gmail.com` |
   | 同步方向 | **双向（Bi-directional）** |

   点「应用」；
3. 同一页面拉到最下面，点 **「导入全部」(Import Everything)**——把本仓库已有的 md 全部导入成 wiki 页面；
4. 完成。访问 `http://NAS的IP:8020/home` 应该能看到首页。之后：
   - 网页上每次保存 → 自动 commit + push 到 GitHub；
   - 默认每 5 分钟自动 pull 一次（管理区可调），所以在电脑 / GitHub 网页上的修改也会自动出现在 wiki 里。

## 三、日常使用

- **标记**：打开对应板块页面 → 右下角编辑 → 往表格加一行 → 保存，状态符号用 ⬜ 想看 / 🟨 在看 / ✅ 已看 / ❌ 弃了；
- **新板块**：右上角「+ 新建页面」，路径英文（如 `music/albums`）、标题中文，格式抄 `/templates/item`；
- **搜索**：顶栏搜索框支持中文全文搜索；
- **注意**：尽量别在 wiki 网页和 GitHub 上同时编辑同一个页面，避免同步冲突。

## 四、YouTube 频道刷新

Geography Now 和冒险雷探长的全集列表迁移自原本地 SQLite tracker（已退役）。频道出新视频后，在电脑上的仓库目录里：

```bash
git pull                          # 先拉回 wiki 上的最新标记
python scripts/sync_channels.py   # 依赖：pip install yt-dlp
git add -A && git commit -m "刷新频道视频" && git push
```

脚本只把新视频以 ⬜ 状态插到表格顶部并重算统计行，不会改动已有行，所以和网页上的标记互不冲突。想追踪新频道，在脚本的 `CHANNELS` 列表加一行即可。

## 端口分配备忘（fnOS）

| 端口 | 服务 |
|---|---|
| 3000 | homepage 导航页 |
| 8010 | ryot |
| 8020 | **wikijs（本项目）** |
| 8090 | watchlist（docsify 旧版清单站） |
