# 异环兑换码搜集器 v2.0 🎮

> Neverness to Everness (异环) 兑换码实时追踪 + 有效性验证

## ✨ 功能

- ✅ **已验证有效码优先** — 默认展示社区亲测有效的兑换码，失效码自动排除
- 🔬 **验证体系** — 区分「已验证有效」和「来源未验证」，避免无效码误导
- 🎨 **暗色主题 GUI** — GitHub 风格深色界面，左侧卡片列表 + 右侧详情面板
- ✔️ **使用追踪** — 标记已使用/恢复，状态持久化到本地
- 🔍 **多维度筛选** — 已验证有效 / 未验证 / 已使用 / 失效过期 / 全部
- 📝 **一键复制** — 单个 + 批量复制全部已验证有效码
- 🔄 **联网验证** — 定期检查来源可访问性
- ⏰ **自动过期检测** — 限时码到期自动标记

## 📦 兑换码状态（截至 2026-05-03）

| 兑换码 | 状态 | 奖励 | 有效期 |
|--------|------|------|--------|
| YHNOWTOENJOY | ✅ 已验证 | 环石×100 + 材料 | ⚠️ 5/7 截止 |
| YHNANALLYGO | ✅ 已验证 | 环石×100 + 材料 | ⚠️ 5/7 截止 |
| YHOB0423 | ✅ 已验证 | 环石×100 + 材料 | ⚠️ 5/7 截止 |
| YHBILIBILI0423 | ✅ 已验证 | 头像框「电力满分」+ 材料 | 长期 |
| YHTAPTAP0423 | ✅ 已验证 | 头像框「发现未来」+ 材料 | 长期 |
| YHDOUYIN0423 | ✅ 已验证 | 材料 | 长期 |
| YHHAOYOU0423 | ✅ 已验证 | 头像框「爆米花猎手」+ 材料 | 长期 |
| YIHUAN0423 | ✅ 已验证 | 环石×50 + 材料 | 长期 |
| YH0423GIFT | ✅ 已验证 | 环石×50 + 方斯×2500 | 长期 |
| YHHONGMENG0423 | ❌ 失效 | 头像框「星河」+ 材料 | — |
| MIGUKUAIYOU0423 | ❌ 失效 | 材料 | — |

> ⚠️ `YHHONGMENG0423` 和 `MIGUKUAIYOU0423` 经多人反馈无效，5/3 社区列表已移除。

## 🚀 快速开始

### 方式一：源码运行

```bash
pip install requests beautifulsoup4
python app.py
```

### 方式二：自行打包 exe

```bash
pip install pyinstaller requests beautifulsoup4
python build.py
# exe 输出在 dist/ 目录
```

## 📁 文件说明

```
yihuan-redeem/
├── app.py              # 主程序 GUI (v2.0)
├── build.py            # PyInstaller 打包脚本
├── codes_data.json     # 兑换码数据（含验证状态）
└── .gitignore
```

## 📝 使用说明

1. 运行 `python app.py` 或双击打包好的 exe
2. 默认显示「已验证有效」的兑换码（已排除失效码）
3. 点击卡片查看详情，点击「标记已使用」追踪
4. 顶部筛选栏切换视图
5. 「复制全部有效码」批量导出到剪贴板
6. 「联网验证」检查数据来源是否可达

## 📊 数据来源

- [TapTap 2026/5/3 有效码列表](https://www.taptap.cn/moment/799665250738635968) ⭐
- [TapTap 原始公测帖](https://www.taptap.cn/moment/796436572193949454)
- [游侠网](https://gl.ali213.net/html/2026-4/1766087.html)
- [游民星空](https://www.gamersky.com/handbook/202604/2130594.shtml)
- [B站 4.31 更新](https://www.bilibili.com/video/BV14t9eB6E7C/)
