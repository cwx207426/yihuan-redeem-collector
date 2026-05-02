# 异环兑换码搜集器 🎮

> Neverness to Everness (异环) 兑换码实时追踪工具

## ✨ 功能

- 📋 **11 个公测真实兑换码** — 从 TapTap、游侠网、游民星空等多渠道搜集
- 🎨 **暗色主题 GUI** — 左侧卡片列表 + 右侧详情面板
- ✅ **使用追踪** — 标记已使用/恢复，状态持久化
- 🔍 **筛选功能** — 全部 / 有效 / 已使用 / 已过期
- 📝 **一键复制** — 单个 + 批量复制全部有效码
- 🔄 **在线搜集** — 联网扫描最新兑换码来源
- ⏰ **自动过期检测** — 限时码到期自动标记

## 📦 兑换码列表

| 兑换码 | 奖励 | 有效期 | 来源 |
|--------|------|--------|------|
| YHNOWTOENJOY | 环石×100 + 材料 | 2026-05-07 | 公测前瞻 |
| YHNANALLYGO | 环石×100 + 材料 | 2026-05-07 | 公测前瞻 |
| YHOB0423 | 环石×100 + 材料 | 2026-05-07 | 公测前瞻 |
| YHBILIBILI0423 | 头像框「电力满分」+ 材料 | 长期 | B站专属 |
| YHTAPTAP0423 | 头像框「发现未来」+ 材料 | 长期 | TapTap专属 |
| YHDOUYIN0423 | 材料 | 长期 | 抖音专属 |
| YHHAOYOU0423 | 头像框「爆米花猎手」+ 材料 | 长期 | 好游快爆 |
| YHHONGMENG0423 | 头像框「星河」+ 材料 | 长期 | 鸿蒙专属 |
| YIHUAN0423 | 环石×50 + 材料 | 长期 | 公测福利 |
| YH0423GIFT | 环石×50 + 方斯×2500 | 长期 | 公测福利 |
| MIGUKUAIYOU0423 | 材料 | 长期 | 咪咕快游 |

## 🚀 快速开始

### 方式一：直接运行（推荐）

下载 [Releases](https://github.com/cwx207426/yihuan-redeem-collector/releases) 中的 `异环兑换码搜集器.exe`，双击运行。

### 方式二：源码运行

```bash
pip install requests beautifulsoup4
python app.py
```

### 方式三：自行打包

```bash
pip install pyinstaller requests beautifulsoup4
python build.py
```

## 📁 文件说明

```
yihuan-redeem/
├── app.py              # 主程序 (GUI)
├── build.py            # PyInstaller 打包脚本
├── codes_data.json     # 兑换码数据
└── .gitignore
```

## 📝 使用说明

1. 双击 exe 启动程序
2. 左侧查看所有兑换码，点击卡片查看详情
3. 点击「标记已使用」追踪使用状态
4. 筛选按钮切换视图
5. 「复制全部有效码」批量复制到剪贴板
6. 「在线搜集」联网检查最新兑换码

## 📊 数据来源

- [TapTap 异环论坛](https://www.taptap.cn/moment/796436572193949454)
- [游侠网](https://gl.ali213.net/html/2026-4/1766087.html)
- [游民星空](https://www.gamersky.com/handbook/202604/2130594.shtml)
- [17173](https://news.17173.com/content/04242026/003015097.shtml)
