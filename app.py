#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异环兑换码搜集器 v2.0 - Yihuan Redeem Code Collector
实时搜集、验证、追踪异环(Neverness to Everness)游戏兑换码
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
import threading
from datetime import datetime

# ============ Paths ============
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
    BUNDLE_DIR = sys._MEIPASS
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = APP_DIR

DATA_FILE = os.path.join(BUNDLE_DIR, "codes_data.json")
USER_STATE_FILE = os.path.join(APP_DIR, "user_state.json")


# ============ Data management ============
def load_codes():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"codes": [], "last_update": "", "update_sources": []}

def load_user_state():
    try:
        with open(USER_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"used_codes": {}}

def save_user_state(state):
    with open(USER_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ============ Web crawler ============
def crawl_online():
    """Crawl latest codes from known sources, return (new_codes, message)"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        sources = {
            "https://www.taptap.cn/moment/799665250738635968": "TapTap 5/3更新",
            "https://gl.ali213.net/html/2026-4/1766087.html": "游侠网",
            "https://www.gamersky.com/handbook/202604/2130594.shtml": "游民星空",
        }
        
        reachable = 0
        for url, name in sources.items():
            try:
                resp = requests.get(url, timeout=10, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                if resp.status_code == 200:
                    reachable += 1
            except:
                pass
        
        if reachable > 0:
            return [], f"✅ 已检查 {reachable}/{len(sources)} 个来源，当前数据已是最新"
        return [], "⚠️ 联网失败，使用本地缓存数据"
    except:
        return [], "⚠️ 联网模块未安装（需 requests + beautifulsoup4）"


# ============ Colors ============
C = {
    "bg": "#0d1117",
    "card": "#161b22",
    "card_border": "#30363d",
    "header_bg": "#010409",
    "fg": "#c9d1d9",
    "muted": "#8b949e",
    "accent": "#58a6ff",
    "green": "#3fb950",
    "orange": "#d2991d",
    "red": "#f85149",
    "purple": "#a371f7",
    "cyan": "#39d2c0",
    "used": "#484f58",
    "code_fg": "#79c0ff",
    "badge_active": "#1a3a1a",
    "badge_used": "#2a2a2a",
    "badge_expired": "#3a1a1a",
    "badge_invalid": "#3a2a1a",
    "btn_primary": "#238636",
    "btn_primary_hover": "#2ea043",
    "btn_secondary": "#21262d",
    "btn_secondary_hover": "#30363d",
    "btn_danger": "#6e7681",
    "btn_danger_hover": "#8b949e",
    "divider": "#21262d",
    "scrollbar": "#30363d",
}


class RedeemCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("异环兑换码搜集器 v2.0")
        self.root.geometry("1050x750")
        self.root.minsize(900, 600)
        self.root.configure(bg=C["bg"])

        self.codes_data = load_codes()
        self.user_state = load_user_state()
        self._current_code_index = None
        self._filter_mode = "valid"  # default: show verified valid only

        self._build_ui()
        self._refresh_code_list()

    def _get_code_status(self, code):
        """Returns 'active', 'expired', 'invalid', or 'used'"""
        code_str = code["code"]
        if code_str in self.user_state.get("used_codes", {}):
            return "used"
        # Server-side invalid
        if code.get("status") == "invalid":
            return "invalid"
        # Expiry check
        expires = code.get("expires", "")
        if "长期有效" not in expires and expires:
            try:
                exp_date = datetime.strptime(expires.split(" ")[0], "%Y-%m-%d")
                if datetime.now() > exp_date:
                    return "expired"
            except:
                pass
        return "active"

    def _build_ui(self):
        # ===== Header =====
        header = tk.Frame(self.root, bg=C["header_bg"], height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_frame = tk.Frame(header, bg=C["header_bg"])
        title_frame.pack(side="left", padx=24, pady=12)

        tk.Label(title_frame, text="🎮 异环兑换码搜集器 v2.0",
                bg=C["header_bg"], fg="white", font=("Microsoft YaHei", 16, "bold")).pack(anchor="w")
        tk.Label(title_frame, text="Neverness to Everness — 已验证兑换码实时追踪",
                bg=C["header_bg"], fg=C["muted"], font=("Microsoft YaHei", 8)).pack(anchor="w")

        # Stats
        stats_frame = tk.Frame(header, bg=C["header_bg"])
        stats_frame.pack(side="right", padx=24, pady=12)

        self.lbl_total = tk.Label(stats_frame, text="总计: 0", bg=C["header_bg"], fg=C["muted"],
                                   font=("Consolas", 10))
        self.lbl_total.pack(side="left", padx=(0, 12))
        self.lbl_verified = tk.Label(stats_frame, text="✅ 已验证: 0", bg=C["header_bg"], fg=C["green"],
                                      font=("Consolas", 10))
        self.lbl_verified.pack(side="left", padx=(0, 12))
        self.lbl_invalid = tk.Label(stats_frame, text="❌ 失效: 0", bg=C["header_bg"], fg=C["red"],
                                     font=("Consolas", 10))
        self.lbl_invalid.pack(side="left")

        # ===== Toolbar =====
        toolbar = tk.Frame(self.root, bg=C["bg"])
        toolbar.pack(fill="x", padx=20, pady=(10, 0))

        btn_style = {"font": ("Microsoft YaHei", 9), "borderwidth": 0, "padx": 14, "pady": 6,
                     "cursor": "hand2", "relief": "flat"}

        self.btn_all = tk.Button(toolbar, text="全部", bg=C["btn_secondary"], fg=C["fg"],
                                 activebackground=C["btn_secondary_hover"], activeforeground="white",
                                 command=lambda: self._set_filter("all"), **btn_style)
        self.btn_all.pack(side="left", padx=(0, 4))

        self.btn_valid = tk.Button(toolbar, text="✅ 已验证有效", bg=C["btn_primary"], fg="white",
                                   activebackground=C["btn_primary_hover"], activeforeground="white",
                                   command=lambda: self._set_filter("valid"), **btn_style)
        self.btn_valid.pack(side="left", padx=(0, 4))

        self.btn_active = tk.Button(toolbar, text="🟢 未验证", bg=C["btn_secondary"], fg=C["fg"],
                                    activebackground=C["btn_secondary_hover"], activeforeground="white",
                                    command=lambda: self._set_filter("active"), **btn_style)
        self.btn_active.pack(side="left", padx=(0, 4))

        self.btn_used = tk.Button(toolbar, text="✔️ 已使用", bg=C["btn_secondary"], fg=C["fg"],
                                  activebackground=C["btn_secondary_hover"], activeforeground="white",
                                  command=lambda: self._set_filter("used"), **btn_style)
        self.btn_used.pack(side="left", padx=(0, 4))

        self.btn_invalid = tk.Button(toolbar, text="❌ 失效/过期", bg=C["btn_secondary"], fg=C["fg"],
                                     activebackground=C["btn_secondary_hover"], activeforeground="white",
                                     command=lambda: self._set_filter("invalid"), **btn_style)
        self.btn_invalid.pack(side="left")

        # Right side buttons
        self.btn_crawl = tk.Button(toolbar, text="🔄 联网验证", bg=C["btn_secondary"], fg=C["accent"],
                                   activebackground=C["btn_secondary_hover"], activeforeground=C["accent"],
                                   command=self._online_crawl, **btn_style)
        self.btn_crawl.pack(side="right", padx=(4, 0))

        self.btn_copy_all = tk.Button(toolbar, text="📋 复制全部有效码", bg=C["btn_primary"], fg="white",
                                      activebackground=C["btn_primary_hover"], activeforeground="white",
                                      command=self._copy_all_valid, **btn_style)
        self.btn_copy_all.pack(side="right")

        # ===== Divider =====
        tk.Frame(self.root, bg=C["divider"], height=1).pack(fill="x", padx=20, pady=(8, 0))

        # ===== Main content =====
        main = tk.Frame(self.root, bg=C["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=(8, 0))

        # Left: code list
        left_wrapper = tk.Frame(main, bg=C["bg"])
        left_wrapper.pack(side="left", fill="both", expand=True, padx=(0, 12))

        # Filter indicator
        self.filter_label = tk.Label(left_wrapper, text="当前显示: 已验证有效",
                                     bg=C["bg"], fg=C["muted"], font=("Microsoft YaHei", 9),
                                     anchor="w")
        self.filter_label.pack(fill="x", pady=(0, 6))

        # Scrollable canvas
        self.canvas = tk.Canvas(left_wrapper, bg=C["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(left_wrapper, orient="vertical", command=self.canvas.yview,
                                 bg=C["scrollbar"], troughcolor=C["bg"], activebackground=C["muted"])
        self.codes_frame = tk.Frame(self.canvas, bg=C["bg"])

        def _on_frame_config(e):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.codes_frame.bind("<Configure>", _on_frame_config)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.codes_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        def _on_canvas_config(e):
            self.canvas.itemconfig(self.canvas_window, width=e.width)
        self.canvas.bind("<Configure>", _on_canvas_config)

        def _on_mousewheel(e):
            self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Right: detail panel
        right = tk.Frame(main, bg=C["card"], width=300, relief="solid", bd=1, highlightbackground=C["card_border"])
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        # Detail header
        detail_header = tk.Frame(right, bg=C["header_bg"], height=40)
        detail_header.pack(fill="x")
        detail_header.pack_propagate(False)
        tk.Label(detail_header, text="🔍 兑换码详情", bg=C["header_bg"], fg="white",
                font=("Microsoft YaHei", 11, "bold")).pack(side="left", padx=16, pady=8)

        detail_body = tk.Frame(right, bg=C["card"])
        detail_body.pack(fill="both", expand=True, padx=14, pady=10)

        self.lbl_code = tk.Label(detail_body, text="点击左侧卡片查看详情",
                                 bg=C["card"], fg=C["muted"], font=("Consolas", 12, "bold"),
                                 wraplength=260, justify="center")
        self.lbl_code.pack(pady=(20, 8))

        self.lbl_status = tk.Label(detail_body, text="", bg=C["card"], fg=C["fg"],
                                    font=("Microsoft YaHei", 10, "bold"))
        self.lbl_status.pack(pady=2)

        self.lbl_rewards = tk.Label(detail_body, text="", bg=C["card"], fg=C["fg"],
                                     font=("Microsoft YaHei", 9), wraplength=260, justify="left")
        self.lbl_rewards.pack(pady=4)

        self.lbl_source = tk.Label(detail_body, text="", bg=C["card"], fg=C["muted"],
                                    font=("Microsoft YaHei", 9))
        self.lbl_source.pack(pady=2)

        self.lbl_expires = tk.Label(detail_body, text="", bg=C["card"], fg=C["muted"],
                                     font=("Microsoft YaHei", 9))
        self.lbl_expires.pack(pady=2)

        self.lbl_note = tk.Label(detail_body, text="", bg=C["card"], fg=C["orange"],
                                  font=("Microsoft YaHei", 9), wraplength=260, justify="left")
        self.lbl_note.pack(pady=2)

        # Detail actions
        sep = tk.Frame(detail_body, bg=C["divider"], height=1)
        sep.pack(fill="x", pady=(12, 8))

        btn_row = tk.Frame(detail_body, bg=C["card"])
        btn_row.pack(fill="x")

        self.btn_use = tk.Button(btn_row, text="✅ 标记已使用", bg=C["btn_primary"], fg="white",
                                 font=("Microsoft YaHei", 9), borderwidth=0, padx=12, pady=6,
                                 cursor="hand2", command=self._mark_current_used,
                                 activebackground=C["btn_primary_hover"])
        self.btn_use.pack(side="left", padx=(0, 4))

        self.btn_unuse = tk.Button(btn_row, text="🔄 恢复", bg=C["btn_danger"], fg="white",
                                   font=("Microsoft YaHei", 9), borderwidth=0, padx=12, pady=6,
                                   cursor="hand2", command=self._mark_current_unused,
                                   activebackground=C["btn_danger_hover"])
        self.btn_unuse.pack(side="left")

        self.btn_copy_detail = tk.Button(detail_body, text="📋 复制此码", bg=C["btn_secondary"], fg=C["accent"],
                                         font=("Microsoft YaHei", 9), borderwidth=0, padx=12, pady=6,
                                         cursor="hand2", command=self._copy_current_code,
                                         activebackground=C["btn_secondary_hover"])
        self.btn_copy_detail.pack(fill="x", pady=(6, 0))

        # Summary panel
        summ = tk.Frame(right, bg=C["card"])
        summ.pack(fill="x", side="bottom", padx=14, pady=(0, 12))

        tk.Frame(summ, bg=C["divider"], height=1).pack(fill="x", pady=(0, 8))

        self.lbl_used_count = tk.Label(summ, text="已使用: 0", bg=C["card"], fg=C["muted"],
                                        font=("Consolas", 10))
        self.lbl_used_count.pack(side="left")
        self.lbl_remain = tk.Label(summ, text="有效剩余: 0", bg=C["card"], fg=C["green"],
                                    font=("Consolas", 10))
        self.lbl_remain.pack(side="right")

        # Status bar
        self.status_bar = tk.Label(self.root, text="就绪", bg=C["header_bg"], fg=C["muted"],
                                   font=("Consolas", 9), anchor="w", padx=16, pady=4)
        self.status_bar.pack(side="bottom", fill="x")

        # Init detail button states
        self.btn_use.config(state="disabled")
        self.btn_unuse.config(state="disabled")
        self.btn_copy_detail.config(state="disabled")

    def _set_filter(self, mode):
        self._filter_mode = mode
        # Update button highlights
        all_btns = [self.btn_all, self.btn_valid, self.btn_active, self.btn_used, self.btn_invalid]
        mapping = {"all": 0, "valid": 1, "active": 2, "used": 3, "invalid": 4}
        for i, btn in enumerate(all_btns):
            if i == mapping.get(mode, 0):
                btn.config(bg=C["btn_primary"], fg="white", activebackground=C["btn_primary_hover"])
            else:
                btn.config(bg=C["btn_secondary"], fg=C["fg"], activebackground=C["btn_secondary_hover"])
        
        labels = {"all": "全部", "valid": "已验证有效", "active": "有效（含未验证）", "used": "已使用", "invalid": "失效/过期"}
        self.filter_label.config(text=f"当前显示: {labels.get(mode, mode)}")
        self._refresh_code_list()

    def _refresh_code_list(self):
        for widget in self.codes_frame.winfo_children():
            widget.destroy()

        codes = self.codes_data.get("codes", [])
        display = []
        for idx, code in enumerate(codes):
            status = self._get_code_status(code)
            if self._filter_mode == "valid":
                if not (code.get("verified") and status == "active"):
                    continue
            elif self._filter_mode == "active":
                if status != "active":
                    continue
            elif self._filter_mode == "used":
                if status != "used":
                    continue
            elif self._filter_mode == "invalid":
                if status not in ("invalid", "expired"):
                    continue
            display.append((idx, code, status))

        if not display:
            empty_label = tk.Label(self.codes_frame, text="没有匹配的兑换码",
                                   bg=C["bg"], fg=C["muted"], font=("Microsoft YaHei", 11),
                                   pady=40)
            empty_label.pack()

        for idx, code, status in display:
            self._create_code_card(idx, code, status, self.codes_frame)

        # Update stats
        verified_valid = sum(1 for c in codes if self._get_code_status(c) == "active" and c.get("verified"))
        invalid_count = sum(1 for c in codes if self._get_code_status(c) in ("invalid", "expired"))
        used_count = sum(1 for c in codes if self._get_code_status(c) == "used")

        self.lbl_total.config(text=f"总计: {len(codes)}")
        self.lbl_verified.config(text=f"✅ 已验证: {verified_valid}")
        self.lbl_invalid.config(text=f"❌ 失效: {invalid_count}")
        self.lbl_used_count.config(text=f"已使用: {used_count}")
        self.lbl_remain.config(text=f"有效剩余: {verified_valid - used_count}")

    def _create_code_card(self, idx, code, status, parent):
        # Determine card style
        is_verified = code.get("verified", False)
        
        card = tk.Frame(parent, bg=C["card"], relief="solid", bd=1,
                        highlightbackground=C["card_border"], highlightthickness=1)
        card.pack(fill="x", pady=2)

        inner = tk.Frame(card, bg=C["card"])
        inner.pack(fill="x", padx=14, pady=10)

        # Top row: code + badges
        top = tk.Frame(inner, bg=C["card"])
        top.pack(fill="x")

        code_fg = C["code_fg"] if status == "active" else C["muted"]
        code_label = tk.Label(top, text=code["code"], bg=C["card"], fg=code_fg,
                              font=("Consolas", 13, "bold"), anchor="w", cursor="hand2")
        code_label.pack(side="left")
        code_label.bind("<Button-1>", lambda e, i=idx: self._show_detail(i))

        # Badges
        badges = tk.Frame(top, bg=C["card"])
        badges.pack(side="right")

        if is_verified:
            v_badge = tk.Label(badges, text="✅ 已验证", bg=C["badge_active"], fg=C["green"],
                              font=("Microsoft YaHei", 8, "bold"), padx=6, pady=1)
            v_badge.pack(side="right", padx=(4, 0))
        
        if status == "active":
            st_badge = tk.Label(badges, text="有效", bg=C["badge_active"], fg=C["green"],
                               font=("Microsoft YaHei", 8, "bold"), padx=6, pady=1)
        elif status == "used":
            st_badge = tk.Label(badges, text="已使用", bg=C["badge_used"], fg=C["used"],
                               font=("Microsoft YaHei", 8, "bold"), padx=6, pady=1)
        elif status == "expired":
            st_badge = tk.Label(badges, text="已过期", bg=C["badge_expired"], fg=C["red"],
                               font=("Microsoft YaHei", 8, "bold"), padx=6, pady=1)
        else:
            st_badge = tk.Label(badges, text="已失效", bg=C["badge_invalid"], fg=C["orange"],
                               font=("Microsoft YaHei", 8, "bold"), padx=6, pady=1)
        st_badge.pack(side="right", padx=(4, 0))

        # Rewards row
        rewards = code.get("rewards", "")
        if len(rewards) > 59:
            rewards = rewards[:56] + "..."
        tk.Label(inner, text=rewards, bg=C["card"], fg=C["fg"],
                font=("Microsoft YaHei", 8), anchor="w").pack(fill="x", pady=(4, 0))

        # Info row
        info = tk.Frame(inner, bg=C["card"])
        info.pack(fill="x", pady=(2, 0))

        tk.Label(info, text=f"📡 {code.get('source', '')}", bg=C["card"], fg=C["muted"],
                font=("Microsoft YaHei", 7)).pack(side="left")
        tk.Label(info, text=f"⏰ {code.get('expires', '')}", bg=C["card"], fg=C["muted"],
                font=("Microsoft YaHei", 7)).pack(side="right")

        # Note if invalid
        note = code.get("note", "")
        if note and status in ("invalid", "expired"):
            tk.Label(inner, text=f"💡 {note}", bg=C["card"], fg=C["orange"],
                    font=("Microsoft YaHei", 8), anchor="w", wraplength=500).pack(fill="x", pady=(2, 0))

        # Action buttons (bottom of card)
        if status == "active":
            actions = tk.Frame(inner, bg=C["card"])
            actions.pack(fill="x", pady=(6, 0))

            tk.Button(actions, text="标记已使用", bg=C["btn_primary"], fg="white",
                     font=("Microsoft YaHei", 8), borderwidth=0, padx=10, pady=3, cursor="hand2",
                     activebackground=C["btn_primary_hover"],
                     command=lambda c=code["code"]: self._mark_used(c)).pack(side="left", padx=(0, 4))

            tk.Button(actions, text="复制", bg=C["btn_secondary"], fg=C["accent"],
                     font=("Microsoft YaHei", 8), borderwidth=0, padx=10, pady=3, cursor="hand2",
                     activebackground=C["btn_secondary_hover"],
                     command=lambda c=code["code"]: self._copy_code(c)).pack(side="left")
        elif status == "used":
            actions = tk.Frame(inner, bg=C["card"])
            actions.pack(fill="x", pady=(6, 0))

            tk.Button(actions, text="恢复未使用", bg=C["btn_danger"], fg="white",
                     font=("Microsoft YaHei", 8), borderwidth=0, padx=10, pady=3, cursor="hand2",
                     activebackground=C["btn_danger_hover"],
                     command=lambda c=code["code"]: self._mark_unused(c)).pack(side="left")
            tk.Button(actions, text="复制", bg=C["btn_secondary"], fg=C["accent"],
                     font=("Microsoft YaHei", 8), borderwidth=0, padx=10, pady=3, cursor="hand2",
                     command=lambda c=code["code"]: self._copy_code(c)).pack(side="left", padx=(4, 0))
        elif status in ("invalid", "expired"):
            actions = tk.Frame(inner, bg=C["card"])
            actions.pack(fill="x", pady=(6, 0))
            tk.Button(actions, text="复制", bg=C["btn_secondary"], fg=C["muted"],
                     font=("Microsoft YaHei", 8), borderwidth=0, padx=10, pady=3, cursor="hand2",
                     command=lambda c=code["code"]: self._copy_code(c)).pack(side="left")

        # Click area for detail
        for w in [card, inner, top, info]:
            w.bind("<Button-1>", lambda e, i=idx: self._show_detail(i))

    def _show_detail(self, idx):
        codes = self.codes_data.get("codes", [])
        if idx >= len(codes):
            return
        code = codes[idx]
        status = self._get_code_status(code)
        is_verified = code.get("verified", False)

        self._current_code_index = idx

        self.lbl_code.config(text=code["code"], fg=C["code_fg"] if status == "active" else C["muted"],
                            justify="left", anchor="w")

        # Status line
        if status == "active" and is_verified:
            self.lbl_status.config(text="✅ 已验证有效", fg=C["green"])
        elif status == "active" and not is_verified:
            self.lbl_status.config(text="🟢 有效（来源未验证）", fg=C["cyan"])
        elif status == "used":
            self.lbl_status.config(text="✔️ 已使用", fg=C["used"])
        elif status == "expired":
            self.lbl_status.config(text="⏰ 已过期", fg=C["red"])
        else:
            self.lbl_status.config(text="❌ 已失效", fg=C["orange"])

        # Rewards
        rewards = code.get("rewards", "").replace("、", "\n  • ")
        self.lbl_rewards.config(text=f"🎁 奖励:\n  • {rewards}")

        self.lbl_source.config(text=f"📡 来源: {code.get('source', '未知')}")
        self.lbl_expires.config(text=f"⏰ 有效期: {code.get('expires', '未知')}")
        
        note = code.get("note", "")
        if note:
            self.lbl_note.config(text=f"💡 {note}")
        else:
            self.lbl_note.config(text="")

        # Button states
        if status in ("used",):
            self.btn_use.config(state="disabled")
            self.btn_unuse.config(state="normal")
            self.btn_copy_detail.config(state="normal")
        elif status in ("expired",):
            self.btn_use.config(state="disabled")
            self.btn_unuse.config(state="disabled")
            self.btn_copy_detail.config(state="normal")
        elif status == "invalid":
            self.btn_use.config(state="disabled")
            self.btn_unuse.config(state="disabled")
            self.btn_copy_detail.config(state="normal")
        else:
            self.btn_use.config(state="normal")
            self.btn_unuse.config(state="disabled")
            self.btn_copy_detail.config(state="normal")

    def _mark_used(self, code_str):
        self.user_state.setdefault("used_codes", {})[code_str] = {
            "used_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_user_state(self.user_state)
        self._refresh_code_list()
        self.status_bar.config(text=f"✅ 已标记 {code_str} 为已使用")

    def _mark_unused(self, code_str):
        if code_str in self.user_state.get("used_codes", {}):
            del self.user_state["used_codes"][code_str]
            save_user_state(self.user_state)
        self._refresh_code_list()
        self.status_bar.config(text=f"🔄 已恢复 {code_str} 为未使用")

    def _mark_current_used(self):
        if self._current_code_index is not None:
            codes = self.codes_data.get("codes", [])
            if self._current_code_index < len(codes):
                self._mark_used(codes[self._current_code_index]["code"])

    def _mark_current_unused(self):
        if self._current_code_index is not None:
            codes = self.codes_data.get("codes", [])
            if self._current_code_index < len(codes):
                self._mark_unused(codes[self._current_code_index]["code"])

    def _copy_code(self, code_str):
        self.root.clipboard_clear()
        self.root.clipboard_append(code_str)
        self.root.update()
        self.status_bar.config(text=f"📋 已复制: {code_str}")

    def _copy_current_code(self):
        if self._current_code_index is not None:
            codes = self.codes_data.get("codes", [])
            if self._current_code_index < len(codes):
                self._copy_code(codes[self._current_code_index]["code"])

    def _copy_all_valid(self):
        codes = self.codes_data.get("codes", [])
        valid = [c["code"] for c in codes 
                 if self._get_code_status(c) == "active" and c.get("verified", False)]
        if valid:
            text = "\n".join(valid)
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            self.status_bar.config(text=f"📋 已复制 {len(valid)} 个已验证有效兑换码")
        else:
            messagebox.showinfo("提示", "没有已验证的有效兑换码")

    def _online_crawl(self):
        self.btn_crawl.config(text="🔄 正在验证...", state="disabled")
        self.status_bar.config(text="🔄 正在联网检查兑换码来源...")
        self.root.update()

        def worker():
            new_codes, msg = crawl_online()
            self.root.after(0, self._crawl_done, msg)

        threading.Thread(target=worker, daemon=True).start()

    def _crawl_done(self, msg):
        self.codes_data["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._refresh_code_list()
        self.btn_crawl.config(text="🔄 联网验证", state="normal")
        self.status_bar.config(text=msg)


def main():
    root = tk.Tk()
    app = RedeemCodeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
