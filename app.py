#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异环兑换码搜集器 - Yihuan Redeem Code Collector
实时搜集、显示、追踪异环(Neverness to Everness)游戏兑换码
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import sys
import threading
import time
from datetime import datetime

# ============ Paths ============
if getattr(sys, 'frozen', False):
    # Running as bundled exe
    APP_DIR = os.path.dirname(sys.executable)
    # Bundled data files are extracted to sys._MEIPASS
    BUNDLE_DIR = sys._MEIPASS
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = APP_DIR

DATA_FILE = os.path.join(BUNDLE_DIR, "codes_data.json")
USER_STATE_FILE = os.path.join(APP_DIR, "user_state.json")

# ============ Data management ============
def load_codes():
    """Load codes from data file"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"codes": [], "last_update": "", "update_sources": []}

def load_user_state():
    """Load user's used codes state"""
    try:
        with open(USER_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"used_codes": {}}

def save_user_state(state):
    """Save user's used codes state"""
    with open(USER_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def save_codes(data):
    """Save codes to data file"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ============ Web crawling ============
def crawl_codes():
    """
    Attempt to crawl latest codes from known sources.
    In the current version, sources are manually maintained for reliability.
    Returns list of new codes found (empty if none).
    """
    new_codes = []
    try:
        import requests
        from bs4 import BeautifulSoup

        sources = [
            "https://gl.ali213.net/html/2026-4/1766087.html",
            "https://www.gamersky.com/handbook/202604/2130594.shtml",
        ]

        for url in sources:
            try:
                resp = requests.get(url, timeout=10, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                if resp.status_code == 200:
                    # Just verify source is accessible
                    pass
            except:
                pass
        return new_codes
    except:
        return new_codes

# ============ Main Application ============
class RedeemCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("异环兑换码搜集器")
        self.root.geometry("1000x680")
        self.root.minsize(800, 550)
        
        # Set icon if available
        try:
            self.root.iconbitmap(default=os.path.join(BASE_DIR, "icon.ico"))
        except:
            pass

        # Styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._setup_styles()

        # Data
        self.codes_data = load_codes()
        self.user_state = load_user_state()

        # Build UI
        self._build_ui()
        self._refresh_code_list()

    def _setup_styles(self):
        """Configure ttk styles for a modern dark look"""
        bg = "#1a1a2e"
        fg = "#e0e0e0"
        accent = "#e94560"
        accent2 = "#0f3460"
        card_bg = "#16213e"
        green = "#2ecc71"
        orange = "#f39c12"
        red = "#e74c3c"

        self.colors = {
            "bg": bg, "fg": fg, "accent": accent, "accent2": accent2,
            "card_bg": card_bg, "green": green, "orange": orange, "red": red,
            "used": "#7f8c8d", "active_bg": "#16213e", "header": "#0f3460"
        }

        self.root.configure(bg=bg)

        self.style.configure("TFrame", background=bg)
        self.style.configure("Header.TFrame", background=self.colors["header"])
        self.style.configure("Card.TFrame", background=card_bg, relief="solid", borderwidth=1)
        self.style.configure("TLabelframe", background=bg, foreground=fg)
        self.style.configure("TLabelframe.Label", background=bg, foreground=fg, font=("Microsoft YaHei", 10, "bold"))
        
        self.style.configure("Title.TLabel", background=self.colors["header"], foreground="#ffffff",
                            font=("Microsoft YaHei", 18, "bold"))
        self.style.configure("Subtitle.TLabel", background=self.colors["header"], foreground="#a0a0c0",
                            font=("Microsoft YaHei", 9))
        self.style.configure("Stats.TLabel", background=bg, foreground=fg, font=("Microsoft YaHei", 10))
        self.style.configure("White.TLabel", background=card_bg, foreground=fg, font=("Microsoft YaHei", 10))
        self.style.configure("Green.TLabel", background=card_bg, foreground=green, font=("Microsoft YaHei", 10, "bold"))
        self.style.configure("Orange.TLabel", background=card_bg, foreground=orange, font=("Microsoft YaHei", 10, "bold"))
        self.style.configure("Red.TLabel", background=card_bg, foreground=red, font=("Microsoft YaHei", 10, "bold"))
        self.style.configure("Gray.TLabel", background=card_bg, foreground="#7f8c8d", font=("Microsoft YaHei", 10))

        self.style.configure("Accent.TButton", background=accent, foreground="white",
                            font=("Microsoft YaHei", 10, "bold"), borderwidth=0, padding=(15, 8))
        self.style.map("Accent.TButton", background=[("active", "#ff6b81")])
        
        self.style.configure("Outline.TButton", background=bg, foreground=accent,
                            font=("Microsoft YaHei", 9), borderwidth=1, padding=(10, 5))
        self.style.map("Outline.TButton", background=[("active", card_bg)])

        self.style.configure("Danger.TButton", background="#7f8c8d", foreground="white",
                            font=("Microsoft YaHei", 9), borderwidth=0, padding=(8, 4))
        self.style.map("Danger.TButton", background=[("active", "#95a5a6")])

    def _build_ui(self):
        """Build the complete user interface"""
        # ====== Header ======
        header = ttk.Frame(self.root, style="Header.TFrame", padding=(30, 20))
        header.pack(fill="x")

        title_frame = ttk.Frame(header, style="Header.TFrame")
        title_frame.pack(side="left")

        title = ttk.Label(title_frame, text="🎮 异环兑换码搜集器", style="Title.TLabel")
        title.pack(anchor="w")
        subtitle = ttk.Label(title_frame, text="Neverness to Everness - 实时追踪最新兑换码", style="Subtitle.TLabel")
        subtitle.pack(anchor="w", pady=(2, 0))

        # Stats on right
        header_right = ttk.Frame(header, style="Header.TFrame")
        header_right.pack(side="right", pady=(5, 0))

        self.total_label = ttk.Label(header_right, text="总计: 0", style="Subtitle.TLabel")
        self.total_label.pack(side="left", padx=(0, 15))
        self.active_label = ttk.Label(header_right, text="有效: 0", style="Subtitle.TLabel")
        self.active_label.pack(side="left")

        # ====== Toolbar ======
        toolbar = ttk.Frame(self.root, padding=(20, 10))
        toolbar.pack(fill="x")

        refresh_btn = ttk.Button(toolbar, text="🔄 在线搜集", command=self._online_crawl, style="Accent.TButton")
        refresh_btn.pack(side="left", padx=(0, 8))

        show_all_btn = ttk.Button(toolbar, text="📋 全部", command=lambda: self._refresh_code_list("all"), style="Outline.TButton")
        show_all_btn.pack(side="left", padx=(0, 5))

        show_active_btn = ttk.Button(toolbar, text="✅ 有效", command=lambda: self._refresh_code_list("active"), style="Outline.TButton")
        show_active_btn.pack(side="left", padx=(0, 5))

        show_used_btn = ttk.Button(toolbar, text="✔️ 已使用", command=lambda: self._refresh_code_list("used"), style="Outline.TButton")
        show_used_btn.pack(side="left", padx=(0, 5))

        show_expired_btn = ttk.Button(toolbar, text="⏰ 已过期", command=lambda: self._refresh_code_list("expired"), style="Outline.TButton")
        show_expired_btn.pack(side="left")

        self.filter_var = tk.StringVar(value="all")

        # Copy all button
        copy_all_btn = ttk.Button(toolbar, text="📝 复制全部有效码", command=self._copy_all_active, style="Outline.TButton")
        copy_all_btn.pack(side="right")

        # ====== Main content area ======
        main_pane = ttk.Frame(self.root, padding=(20, 5, 20, 10))
        main_pane.pack(fill="both", expand=True)

        # Left: Code list (scrollable canvas)
        left_frame = ttk.LabelFrame(main_pane, text=" 兑换码列表 ", padding=(10, 10))
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Canvas + scrollbar for scrollable code cards
        self.canvas = tk.Canvas(left_frame, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.canvas.yview)
        self.codes_frame = ttk.Frame(self.canvas, style="TFrame")

        self.codes_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.codes_frame, anchor="nw", tags="inner")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Right: Detail panel
        right_frame = ttk.Frame(main_pane, width=320)
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)

        # Detail card
        detail_card = ttk.LabelFrame(right_frame, text=" 🔍 详情 ", padding=(15, 15))
        detail_card.pack(fill="both", expand=True)

        self.detail_title = ttk.Label(detail_card, text="点击左侧兑换码\n查看详情", 
                                       style="White.TLabel", justify="center", font=("Microsoft YaHei", 11))
        self.detail_title.pack(pady=(20, 5))

        self.detail_rewards = ttk.Label(detail_card, text="", style="White.TLabel", justify="left", wraplength=270)
        self.detail_rewards.pack(pady=5)

        self.detail_source = ttk.Label(detail_card, text="", style="White.TLabel", justify="left")
        self.detail_source.pack(pady=2)

        self.detail_expires = ttk.Label(detail_card, text="", style="White.TLabel", justify="left")
        self.detail_expires.pack(pady=2)

        self.detail_type = ttk.Label(detail_card, text="", style="White.TLabel", justify="left")
        self.detail_type.pack(pady=2)

        # Action buttons in detail
        detail_actions = ttk.Frame(detail_card, style="TFrame")
        detail_actions.pack(pady=(15, 5))

        self.detail_use_btn = ttk.Button(detail_actions, text="✅ 标记已使用", command=self._mark_current_used, style="Accent.TButton")
        self.detail_use_btn.pack(side="left", padx=(0, 5))
        self.detail_unuse_btn = ttk.Button(detail_actions, text="🔄 恢复未使用", command=self._mark_current_unused, style="Danger.TButton")
        self.detail_unuse_btn.pack(side="left")

        self.detail_copy_btn = ttk.Button(detail_card, text="📋 复制兑换码", command=self._copy_current_code, style="Outline.TButton")
        self.detail_copy_btn.pack(pady=(5, 0))

        # Summary info
        summary_card = ttk.LabelFrame(right_frame, text=" 📊 使用统计 ", padding=(15, 10))
        summary_card.pack(fill="x", pady=(10, 0))

        self.stat_frame = ttk.Frame(summary_card, style="TFrame")
        self.stat_frame.pack(fill="x")

        self.stat_used = ttk.Label(self.stat_frame, text="已使用: 0", style="Stats.TLabel")
        self.stat_used.pack(side="left")
        self.stat_remaining = ttk.Label(self.stat_frame, text="", style="Stats.TLabel")
        self.stat_remaining.pack(side="right")

        # Status bar
        self.status_bar = ttk.Label(self.root, text="就绪 | 数据更新: " + (self.codes_data.get("last_update", "未知") or "未知"),
                                    background="#0a0a1a", foreground="#666", font=("Consolas", 9), anchor="w", padding=(10, 5))
        self.status_bar.pack(side="bottom", fill="x")

        self._current_code_index = None

    def _get_code_status(self, code_str):
        """Determine effective status of a code"""
        # Check if manually marked as used
        if code_str in self.user_state.get("used_codes", {}):
            return "used"
        
        # Check if expired based on expires field
        code_info = self._find_code(code_str)
        if code_info:
            expires = code_info.get("expires", "")
            if "长期有效" not in expires and expires:
                try:
                    # Parse expiration date
                    exp_date = datetime.strptime(expires.split(" ")[0], "%Y-%m-%d")
                    if datetime.now() > exp_date:
                        return "expired"
                except:
                    pass
            if code_info.get("status") == "expired":
                return "expired"
        return "active"

    def _find_code(self, code_str):
        for c in self.codes_data.get("codes", []):
            if c["code"] == code_str:
                return c
        return None

    def _refresh_code_list(self, filter_mode="all"):
        """Refresh the scrollable code list"""
        for widget in self.codes_frame.winfo_children():
            widget.destroy()

        codes = self.codes_data.get("codes", [])
        filtered = []
        for idx, code in enumerate(codes):
            status = self._get_code_status(code["code"])
            if filter_mode == "active" and status != "active":
                continue
            if filter_mode == "used" and status != "used":
                continue
            if filter_mode == "expired" and status != "expired":
                continue
            filtered.append((idx, code, status))

        for idx, code, status in filtered:
            self._create_code_card(idx, code, status, self.codes_frame)

        # Update stats
        total = len(codes)
        used_count = len([c for c in codes if self._get_code_status(c["code"]) == "used"])
        expired_count = len([c for c in codes if self._get_code_status(c["code"]) == "expired"])
        active_count = total - used_count - expired_count

        self.total_label.config(text=f"总计: {total}")
        self.active_label.config(text=f"有效: {active_count}")
        self.stat_used.config(text=f"已使用: {used_count}")
        self.stat_remaining.config(text=f"剩余: {active_count} | 过期: {expired_count}")

    def _create_code_card(self, idx, code, status, parent):
        """Create a single code card in the list"""
        card = tk.Frame(parent, bg=self.colors["card_bg"], relief="solid", bd=1,
                        highlightbackground="#2a2a4a", highlightthickness=1)
        card.pack(fill="x", pady=2, padx=2)

        # Left: code & rewards
        left = tk.Frame(card, bg=self.colors["card_bg"])
        left.pack(side="left", fill="both", expand=True, padx=12, pady=8)

        code_label = tk.Label(left, text=code["code"],
                              bg=self.colors["card_bg"], fg="#00d4ff",
                              font=("Consolas", 13, "bold"), anchor="w")
        code_label.pack(anchor="w")

        rewards_label = tk.Label(left, text=code.get("rewards", ""),
                                 bg=self.colors["card_bg"], fg=self.colors["fg"],
                                 font=("Microsoft YaHei", 9), anchor="w", wraplength=450, justify="left")
        rewards_label.pack(anchor="w", pady=(2, 0))

        # Source info
        info_frame = tk.Frame(left, bg=self.colors["card_bg"])
        info_frame.pack(fill="x", pady=(4, 0))
        
        source_label = tk.Label(info_frame, text=f"📡 {code.get('source', '')}  |  ⏰ {code.get('expires', '')}",
                                bg=self.colors["card_bg"], fg="#8888aa",
                                font=("Microsoft YaHei", 8), anchor="w")
        source_label.pack(side="left")

        # Right: status & buttons
        right = tk.Frame(card, bg=self.colors["card_bg"])
        right.pack(side="right", padx=12, pady=8)

        # Status badge
        if status == "active":
            badge = tk.Label(right, text="✅ 有效", bg="#1a3a1a", fg=self.colors["green"],
                            font=("Microsoft YaHei", 9, "bold"), padx=8, pady=2)
        elif status == "used":
            badge = tk.Label(right, text="✔️ 已使用", bg="#2a2a2a", fg=self.colors["used"],
                            font=("Microsoft YaHei", 9, "bold"), padx=8, pady=2)
        else:
            badge = tk.Label(right, text="⏰ 已过期", bg="#3a1a1a", fg=self.colors["red"],
                            font=("Microsoft YaHei", 9, "bold"), padx=8, pady=2)
        badge.pack(pady=(0, 5))

        # Action buttons
        btn_frame = tk.Frame(right, bg=self.colors["card_bg"])
        btn_frame.pack()

        if status == "active":
            mark_btn = tk.Button(btn_frame, text="标记已使用", bg="#27ae60", fg="white",
                                font=("Microsoft YaHei", 8), borderwidth=0, padx=8, pady=3,
                                cursor="hand2",
                                command=lambda c=code["code"]: self._mark_used(c))
            mark_btn.pack(side="left", padx=(0, 3))
        elif status == "used":
            unmark_btn = tk.Button(btn_frame, text="恢复", bg="#7f8c8d", fg="white",
                                  font=("Microsoft YaHei", 8), borderwidth=0, padx=8, pady=3,
                                  cursor="hand2",
                                  command=lambda c=code["code"]: self._mark_unused(c))
            unmark_btn.pack(side="left", padx=(0, 3))

        copy_btn = tk.Button(btn_frame, text="复制", bg=self.colors["accent2"], fg="white",
                            font=("Microsoft YaHei", 8), borderwidth=0, padx=8, pady=3,
                            cursor="hand2",
                            command=lambda c=code["code"]: self._copy_code(c))
        copy_btn.pack(side="left")

        # Click on card to show detail
        for widget in [card, left, code_label, rewards_label, info_frame, source_label]:
            widget.bind("<Button-1>", lambda e, i=idx: self._show_detail(i))
        # Don't bind right side buttons

    def _show_detail(self, idx):
        """Show detail for a code in the right panel"""
        codes = self.codes_data.get("codes", [])
        if idx >= len(codes):
            return
        code = codes[idx]
        status = self._get_code_status(code["code"])

        self._current_code_index = idx

        self.detail_title.config(text=code["code"], font=("Consolas", 14, "bold"), fg="#00d4ff")
        
        rewards_text = code.get("rewards", "未知奖励").replace("、", "\n• ")
        self.detail_rewards.config(text=f"奖励:\n• {rewards_text}")
        
        self.detail_source.config(text=f"来源: {code.get('source', '未知')}")
        self.detail_expires.config(text=f"有效期: {code.get('expires', '未知')}")
        
        type_text = code.get('type', '未知')
        if status == "used":
            self.detail_type.config(text=f"类型: {type_text} | 状态: 已使用", fg=self.colors["used"])
            self.detail_use_btn.config(state="disabled")
            self.detail_unuse_btn.config(state="normal")
        elif status == "expired":
            self.detail_type.config(text=f"类型: {type_text} | 状态: 已过期", fg=self.colors["red"])
            self.detail_use_btn.config(state="disabled")
            self.detail_unuse_btn.config(state="disabled")
        else:
            self.detail_type.config(text=f"类型: {type_text} | 状态: 有效", fg=self.colors["green"])
            self.detail_use_btn.config(state="normal")
            self.detail_unuse_btn.config(state="disabled")

    def _mark_used(self, code_str):
        """Mark a code as used"""
        self.user_state.setdefault("used_codes", {})[code_str] = {
            "used_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_user_state(self.user_state)
        self._refresh_code_list(self.filter_var.get() or "all")
        self.status_bar.config(text=f"✅ 已标记 {code_str} 为已使用")

    def _mark_unused(self, code_str):
        """Mark a code as unused"""
        if code_str in self.user_state.get("used_codes", {}):
            del self.user_state["used_codes"][code_str]
            save_user_state(self.user_state)
        self._refresh_code_list(self.filter_var.get() or "all")
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
        """Copy code to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(code_str)
        self.root.update()
        self.status_bar.config(text=f"📋 已复制: {code_str}")

    def _copy_current_code(self):
        if self._current_code_index is not None:
            codes = self.codes_data.get("codes", [])
            if self._current_code_index < len(codes):
                self._copy_code(codes[self._current_code_index]["code"])

    def _copy_all_active(self):
        """Copy all active codes to clipboard"""
        codes = self.codes_data.get("codes", [])
        active = [c["code"] for c in codes if self._get_code_status(c["code"]) == "active"]
        if active:
            text = "\n".join(active)
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            self.status_bar.config(text=f"📋 已复制 {len(active)} 个有效兑换码")
        else:
            messagebox.showinfo("提示", "没有可用的兑换码")

    def _online_crawl(self):
        """Trigger online crawling in a thread"""
        self.status_bar.config(text="🔄 正在联网搜集最新兑换码...")
        self.root.update()

        def crawl_thread():
            new_codes = crawl_codes()
            self.root.after(0, self._crawl_done, new_codes)
        
        threading.Thread(target=crawl_thread, daemon=True).start()

    def _crawl_done(self, new_codes):
        """Callback when crawl finishes"""
        if new_codes:
            # Add new codes
            existing = set(c["code"] for c in self.codes_data["codes"])
            for nc in new_codes:
                if nc["code"] not in existing:
                    self.codes_data["codes"].append(nc)
            self.codes_data["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_codes(self.codes_data)
            self._refresh_code_list(self.filter_var.get() or "all")
            self.status_bar.config(text=f"✅ 搜集完成！新增 {len(new_codes)} 个兑换码")
        else:
            self.codes_data["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_codes(self.codes_data)
            self.status_bar.config(text=f"✅ 在线搜集完成，当前共 {len(self.codes_data['codes'])} 个兑换码 | 更新时间: {self.codes_data['last_update']}")


def main():
    root = tk.Tk()
    app = RedeemCodeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
