#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多游戏兑换码搜集器 v3.0 - Multi-Game Redeem Code Collector
支持: 异环、造梦西游OL — 搜集、验证、追踪兑换码
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
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

status_labels = {"active": "有效", "used": "已使用", "expired": "已过期", "invalid": "已失效"}

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"games": {}, "last_update": ""}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_user_state():
    try:
        with open(USER_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"used_codes": {}}

def save_user_state(state):
    with open(USER_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# ============ Colors (GitHub dark) ============
C = {
    "bg": "#0d1117", "card": "#161b22", "card_border": "#30363d",
    "header_bg": "#010409", "tab_active": "#1f6feb", "tab_bg": "#161b22",
    "fg": "#c9d1d9", "muted": "#8b949e", "accent": "#58a6ff",
    "green": "#3fb950", "orange": "#d2991d", "red": "#f85149",
    "purple": "#a371f7", "cyan": "#39d2c0", "used": "#484f58",
    "code_fg": "#79c0ff", "badge_active": "#1a3a1a", "badge_used": "#2a2a2a",
    "badge_expired": "#3a1a1a", "badge_invalid": "#3a2a1a",
    "badge_unverified": "#2a2a1a", "btn_primary": "#238636",
    "btn_primary_hover": "#2ea043", "btn_secondary": "#21262d",
    "btn_secondary_hover": "#30363d", "btn_danger": "#6e7681",
    "btn_danger_hover": "#8b949e", "divider": "#21262d", "scrollbar": "#30363d",
}

STATUS_ICONS = {"active": "\u2705", "used": "\u2714\ufe0f", "expired": "\u23f0", "invalid": "\u274c"}
STATUS_COLORS = {"active": C["green"], "used": C["used"], "expired": C["red"], "invalid": C["orange"]}

class MultiGameRedeemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("\u6e38\u620f\u5151\u6362\u7801\u641c\u96c6\u5668 v3.0")
        self.root.geometry("1100x780")
        self.root.minsize(950, 620)
        self.root.configure(bg=C["bg"])

        self.data = load_data()
        self.user_state = load_user_state()
        self._current_code_index = None
        self._current_game = None
        self._filter_mode = "valid"
        self._game_keys = list(self.data.get("games", {}).keys())

        if not self._game_keys:
            messagebox.showerror("\u9519\u8bef", "\u6ca1\u6709\u627e\u5230\u4efb\u4f55\u6e38\u620f\u6570\u636e\uff01")
            root.destroy()
            return

        self._current_game = self._game_keys[0]
        self._build_ui()
        self._refresh_code_list()

    def _get_code_status(self, code):
        code_str = code["code"]
        game_key = self._current_game
        state_key = f"{game_key}:{code_str}"
        if state_key in self.user_state.get("used_codes", {}):
            return "used"
        if code.get("status") == "invalid":
            return "invalid"
        expires = code.get("expires", "")
        if "\u957f\u671f\u6709\u6548" not in expires and expires:
            try:
                exp_date = datetime.strptime(expires.split(" ")[0], "%Y-%m-%d")
                if datetime.now() > exp_date:
                    return "expired"
            except:
                pass
        return "active"

    def _get_game_data(self):
        return self.data.get("games", {}).get(self._current_game, {})

    # ============ UI ============
    def _build_ui(self):
        import tkinter as tk
        from tkinter import ttk
        
        header = tk.Frame(self.root, bg=C["header_bg"], height=75)
        header.pack(fill="x")
        header.pack_propagate(False)

        tf = tk.Frame(header, bg=C["header_bg"])
        tf.pack(side="left", padx=24, pady=10)
        tk.Label(tf, text="\U0001f381 \u591a\u6e38\u620f\u5151\u6362\u7801\u641c\u96c6\u5668 v3.0",
                bg=C["header_bg"], fg="white", font=("Microsoft YaHei", 16, "bold")).pack(anchor="w")
        tk.Label(tf, text="\u5f02\u73af \u00b7 \u9020\u68a6\u897f\u6e38OL \u2014 \u641c\u96c6 \u00b7 \u9a8c\u8bc1 \u00b7 \u8ffd\u8e2a",
                bg=C["header_bg"], fg=C["muted"], font=("Microsoft YaHei", 8)).pack(anchor="w")

        sf = tk.Frame(header, bg=C["header_bg"])
        sf.pack(side="right", padx=24, pady=10)
        self.lbl_total = tk.Label(sf, text="\u603b\u8ba1: 0", bg=C["header_bg"], fg=C["muted"], font=("Consolas", 10))
        self.lbl_total.pack(side="left", padx=(0, 12))
        self.lbl_verified = tk.Label(sf, text="\u2705 \u5df2\u9a8c\u8bc1: 0", bg=C["header_bg"], fg=C["green"], font=("Consolas", 10))
        self.lbl_verified.pack(side="left", padx=(0, 12))
        self.lbl_invalid = tk.Label(sf, text="\u274c \u5931\u6548: 0", bg=C["header_bg"], fg=C["red"], font=("Consolas", 10))
        self.lbl_invalid.pack(side="left")

        # Tabs
        tabs_frame = tk.Frame(self.root, bg=C["tab_bg"])
        tabs_frame.pack(fill="x", padx=20, pady=(10, 0))
        self.tab_buttons = {}
        for gk in self._game_keys:
            gd = self.data["games"][gk]
            btn = tk.Button(tabs_frame, text=f" {gd.get('icon','')} {gd['name']} ",
                           bg=C["tab_bg"], fg=C["fg"], font=("Microsoft YaHei", 10, "bold"),
                           borderwidth=0, padx=16, pady=8, cursor="hand2", relief="flat",
                           activebackground=C["tab_bg"],
                           command=lambda k=gk: self._switch_game(k))
            btn.pack(side="left", padx=(0, 2))
            self.tab_buttons[gk] = btn

        self.btn_add_game = tk.Button(tabs_frame, text="+ \u6dfb\u52a0\u6e38\u620f", bg=C["btn_secondary"],
                                      fg=C["accent"], font=("Microsoft YaHei", 9), borderwidth=0,
                                      padx=12, pady=8, cursor="hand2",
                                      activebackground=C["btn_secondary_hover"],
                                      command=self._add_game_dialog)
        self.btn_add_game.pack(side="left", padx=(4, 0))
        self._update_tab_highlight()

        # Toolbar
        toolbar = tk.Frame(self.root, bg=C["bg"])
        toolbar.pack(fill="x", padx=20, pady=(6, 0))
        bs = {"font": ("Microsoft YaHei", 9), "borderwidth": 0, "padx": 12, "pady": 5,
              "cursor": "hand2", "relief": "flat"}

        self.toolbar_btns = {
            "all": tk.Button(toolbar, text="\u5168\u90e8", bg=C["btn_secondary"], fg=C["fg"],
                            activebackground=C["btn_secondary_hover"], activeforeground="white",
                            command=lambda: self._set_filter("all"), **bs),
            "valid": tk.Button(toolbar, text="\u2705 \u5df2\u9a8c\u8bc1\u6709\u6548", bg=C["btn_primary"], fg="white",
                              activebackground=C["btn_primary_hover"], activeforeground="white",
                              command=lambda: self._set_filter("valid"), **bs),
            "active": tk.Button(toolbar, text="\U0001f7e1 \u5f85\u9a8c\u8bc1", bg=C["btn_secondary"], fg=C["fg"],
                               activebackground=C["btn_secondary_hover"], activeforeground="white",
                               command=lambda: self._set_filter("active"), **bs),
            "used": tk.Button(toolbar, text="\u2714\ufe0f \u5df2\u4f7f\u7528", bg=C["btn_secondary"], fg=C["fg"],
                             activebackground=C["btn_secondary_hover"], activeforeground="white",
                             command=lambda: self._set_filter("used"), **bs),
            "invalid": tk.Button(toolbar, text="\u274c \u5931\u6548/\u8fc7\u671f", bg=C["btn_secondary"], fg=C["fg"],
                               activebackground=C["btn_secondary_hover"], activeforeground="white",
                               command=lambda: self._set_filter("invalid"), **bs),
        }
        for btn in self.toolbar_btns.values():
            btn.pack(side="left", padx=(0, 3))

        self.btn_add_code = tk.Button(toolbar, text="\u2795 \u6dfb\u52a0\u5151\u6362\u7801", bg=C["btn_primary"],
                                      fg="white", activebackground=C["btn_primary_hover"],
                                      activeforeground="white", command=self._add_code_dialog, **bs)
        self.btn_add_code.pack(side="right", padx=(3, 0))
        self.btn_copy_all = tk.Button(toolbar, text="\U0001f4cb \u590d\u5236\u5168\u90e8\u6709\u6548\u7801",
                                      bg=C["btn_primary"], fg="white",
                                      activebackground=C["btn_primary_hover"], activeforeground="white",
                                      command=self._copy_all_valid, **bs)
        self.btn_copy_all.pack(side="right")

        tk.Frame(self.root, bg=C["divider"], height=1).pack(fill="x", padx=20, pady=(6, 0))

        hint = self._get_game_data().get("redeem_hint", "")
        self.lbl_hint = tk.Label(self.root, text=f"\U0001f4a1 \u5151\u6362\u65b9\u6cd5: {hint}" if hint else "",
                                 bg=C["bg"], fg=C["muted"], font=("Microsoft YaHei", 8), anchor="w", padx=20)
        self.lbl_hint.pack(fill="x", pady=(4, 0))

        # Main content
        main = tk.Frame(self.root, bg=C["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=(4, 0))

        left_w = tk.Frame(main, bg=C["bg"])
        left_w.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.filter_label = tk.Label(left_w, text="\u5f53\u524d\u663e\u793a: \u5df2\u9a8c\u8bc1\u6709\u6548",
                                     bg=C["bg"], fg=C["muted"], font=("Microsoft YaHei", 9), anchor="w")
        self.filter_label.pack(fill="x", pady=(0, 4))

        self.canvas = tk.Canvas(left_w, bg=C["bg"], highlightthickness=0)
        sbar = tk.Scrollbar(left_w, orient="vertical", command=self.canvas.yview,
                           bg=C["scrollbar"], troughcolor=C["bg"])
        self.codes_frame = tk.Frame(self.canvas, bg=C["bg"])
        def _on_fc(e): self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.codes_frame.bind("<Configure>", _on_fc)
        self.canvas_window = self.canvas.create_window((0,0), window=self.codes_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=sbar.set)
        def _on_cc(e): self.canvas.itemconfig(self.canvas_window, width=e.width)
        self.canvas.bind("<Configure>", _on_cc)
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.canvas.pack(side="left", fill="both", expand=True)
        sbar.pack(side="right", fill="y")

        # Detail panel (continued in chunk2)

        right = tk.Frame(main, bg=C["card"], width=310, relief="solid", bd=1,
                        highlightbackground=C["card_border"])
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        dh = tk.Frame(right, bg=C["header_bg"], height=36)
        dh.pack(fill="x")
        dh.pack_propagate(False)
        tk.Label(dh, text="\U0001f50d \u5151\u6362\u7801\u8be6\u60c5", bg=C["header_bg"], fg="white",
                font=("Microsoft YaHei", 11, "bold")).pack(side="left", padx=14, pady=6)

        db = tk.Frame(right, bg=C["card"])
        db.pack(fill="both", expand=True, padx=12, pady=8)

        self.lbl_code = tk.Label(db, text="\u70b9\u51fb\u5de6\u4fa7\u5361\u7247\u67e5\u770b\u8be6\u60c5",
                                 bg=C["card"], fg=C["muted"], font=("Consolas", 12, "bold"),
                                 wraplength=270, justify="center")
        self.lbl_code.pack(pady=(16, 6))
        self.lbl_status = tk.Label(db, text="", bg=C["card"], fg=C["fg"],
                                    font=("Microsoft YaHei", 10, "bold"))
        self.lbl_status.pack(pady=2)
        self.lbl_rewards = tk.Label(db, text="", bg=C["card"], fg=C["fg"],
                                     font=("Microsoft YaHei", 9), wraplength=270, justify="left")
        self.lbl_rewards.pack(pady=3)
        self.lbl_source = tk.Label(db, text="", bg=C["card"], fg=C["muted"], font=("Microsoft YaHei", 9))
        self.lbl_source.pack(pady=1)
        self.lbl_expires = tk.Label(db, text="", bg=C["card"], fg=C["muted"], font=("Microsoft YaHei", 9))
        self.lbl_expires.pack(pady=1)
        self.lbl_note = tk.Label(db, text="", bg=C["card"], fg=C["orange"],
                                  font=("Microsoft YaHei", 9), wraplength=270, justify="left")
        self.lbl_note.pack(pady=1)

        tk.Frame(db, bg=C["divider"], height=1).pack(fill="x", pady=(10, 6))

        br = tk.Frame(db, bg=C["card"])
        br.pack(fill="x")
        self.btn_use = tk.Button(br, text="\u2705 \u6807\u8bb0\u5df2\u4f7f\u7528", bg=C["btn_primary"], fg="white",
                                 font=("Microsoft YaHei", 9), borderwidth=0, padx=12, pady=5,
                                 cursor="hand2", command=self._mark_current_used,
                                 activebackground=C["btn_primary_hover"])
        self.btn_use.pack(side="left", padx=(0, 4))
        self.btn_unuse = tk.Button(br, text="\U0001f504 \u6062\u590d", bg=C["btn_danger"], fg="white",
                                   font=("Microsoft YaHei", 9), borderwidth=0, padx=12, pady=5,
                                   cursor="hand2", command=self._mark_current_unused,
                                   activebackground=C["btn_danger_hover"])
        self.btn_unuse.pack(side="left")

        self.btn_copy_detail = tk.Button(db, text="\U0001f4cb \u590d\u5236\u6b64\u7801", bg=C["btn_secondary"],
                                         fg=C["accent"], font=("Microsoft YaHei", 9), borderwidth=0,
                                         padx=12, pady=5, cursor="hand2", command=self._copy_current_code,
                                         activebackground=C["btn_secondary_hover"])
        self.btn_copy_detail.pack(fill="x", pady=(4, 0))
        self.btn_edit_code = tk.Button(db, text="\u270f\ufe0f \u7f16\u8f91\u6b64\u7801", bg=C["btn_secondary"],
                                       fg=C["accent"], font=("Microsoft YaHei", 9), borderwidth=0,
                                       padx=12, pady=5, cursor="hand2", command=self._edit_code_dialog,
                                       activebackground=C["btn_secondary_hover"])
        self.btn_edit_code.pack(fill="x", pady=(4, 0))
        self.btn_del_code = tk.Button(db, text="\U0001f5d1\ufe0f \u5220\u9664\u6b64\u7801", bg=C["btn_danger"],
                                      fg=C["red"], font=("Microsoft YaHei", 9), borderwidth=0,
                                      padx=12, pady=5, cursor="hand2", command=self._delete_code_dialog,
                                      activebackground=C["btn_danger_hover"])
        self.btn_del_code.pack(fill="x", pady=(4, 0))

        summ = tk.Frame(right, bg=C["card"])
        summ.pack(fill="x", side="bottom", padx=12, pady=(0, 10))
        tk.Frame(summ, bg=C["divider"], height=1).pack(fill="x", pady=(0, 6))
        self.lbl_used_count = tk.Label(summ, text="\u5df2\u4f7f\u7528: 0", bg=C["card"], fg=C["muted"],
                                        font=("Consolas", 10))
        self.lbl_used_count.pack(side="left")
        self.lbl_remain = tk.Label(summ, text="\u6709\u6548\u5269\u4f59: 0", bg=C["card"], fg=C["green"],
                                    font=("Consolas", 10))
        self.lbl_remain.pack(side="right")

        self.status_bar = tk.Label(self.root, text="\u5c31\u7eea", bg=C["header_bg"], fg=C["muted"],
                                   font=("Consolas", 9), anchor="w", padx=14, pady=3)
        self.status_bar.pack(side="bottom", fill="x")
        self._disable_detail_buttons()

    def _switch_game(self, game_key):
        self._current_game = game_key
        self._current_code_index = None
        self._filter_mode = "valid"
        self._update_tab_highlight()
        self._refresh_code_list()
        self._clear_detail()
        hint = self._get_game_data().get("redeem_hint", "")
        self.lbl_hint.config(text=f"\U0001f4a1 \u5151\u6362\u65b9\u6cd5: {hint}" if hint else "")
        for k, btn in self.toolbar_btns.items():
            if k == "valid":
                btn.config(bg=C["btn_primary"], fg="white", activebackground=C["btn_primary_hover"])
            else:
                btn.config(bg=C["btn_secondary"], fg=C["fg"], activebackground=C["btn_secondary_hover"])
        self.filter_label.config(text="\u5f53\u524d\u663e\u793a: \u5df2\u9a8c\u8bc1\u6709\u6548")

    def _update_tab_highlight(self):
        for gk in self._game_keys:
            btn = self.tab_buttons[gk]
            if gk == self._current_game:
                btn.config(bg=C["tab_active"], fg="white", activebackground=C["tab_active"])
            else:
                btn.config(bg=C["tab_bg"], fg=C["fg"], activebackground=C["tab_bg"])

    def _set_filter(self, mode):
        self._filter_mode = mode
        for key, btn in self.toolbar_btns.items():
            if key == mode:
                btn.config(bg=C["btn_primary"], fg="white", activebackground=C["btn_primary_hover"])
            else:
                btn.config(bg=C["btn_secondary"], fg=C["fg"], activebackground=C["btn_secondary_hover"])
        labels = {"all": "\u5168\u90e8", "valid": "\u5df2\u9a8c\u8bc1\u6709\u6548",
                  "active": "\u5f85\u9a8c\u8bc1", "used": "\u5df2\u4f7f\u7528",
                  "invalid": "\u5931\u6548/\u8fc7\u671f"}
        self.filter_label.config(text=f"\u5f53\u524d\u663e\u793a: {labels.get(mode, mode)}")
        self._refresh_code_list()

    def _refresh_code_list(self):
        for widget in self.codes_frame.winfo_children():
            widget.destroy()
        gd = self._get_game_data()
        codes = gd.get("codes", [])
        display = []
        for idx, code in enumerate(codes):
            status = self._get_code_status(code)
            is_verified = code.get("verified", False)
            if self._filter_mode == "valid":
                if not (is_verified and status == "active"):
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
            display.append((idx, code, status, is_verified))

        if not display:
            tk.Label(self.codes_frame, text="\u6ca1\u6709\u5339\u914d\u7684\u5151\u6362\u7801",
                    bg=C["bg"], fg=C["muted"], font=("Microsoft YaHei", 11), pady=40).pack()

        for idx, code, status, is_verified in display:
            self._create_code_card(idx, code, status, is_verified, self.codes_frame)

        verified_active = sum(1 for c in codes if self._get_code_status(c) == "active" and c.get("verified"))
        invalid_count = sum(1 for c in codes if self._get_code_status(c) in ("invalid", "expired"))
        used_count = sum(1 for c in codes if self._get_code_status(c) == "used")
        unverified = sum(1 for c in codes if self._get_code_status(c) == "active" and not c.get("verified"))

        self.lbl_total.config(text=f"\u603b\u8ba1: {len(codes)}")
        self.lbl_verified.config(text=f"\u2705 \u5df2\u9a8c\u8bc1: {verified_active}  \U0001f7e1 \u5f85\u9a8c\u8bc1: {unverified}")
        self.lbl_invalid.config(text=f"\u274c \u5931\u6548: {invalid_count}")
        self.lbl_used_count.config(text=f"\u5df2\u4f7f\u7528: {used_count}")
        self.lbl_remain.config(text=f"\u6709\u6548\u5269\u4f59: {verified_active - used_count}")

    def _create_code_card(self, idx, code, status, is_verified, parent):
        import tkinter as tk
        card = tk.Frame(parent, bg=C["card"], relief="solid", bd=1,
                        highlightbackground=C["card_border"], highlightthickness=1)
        card.pack(fill="x", pady=2)
        inner = tk.Frame(card, bg=C["card"])
        inner.pack(fill="x", padx=12, pady=8)

        top = tk.Frame(inner, bg=C["card"])
        top.pack(fill="x")
        code_fg = C["code_fg"] if status == "active" else C["muted"]
        lbl = tk.Label(top, text=code["code"], bg=C["card"], fg=code_fg,
                      font=("Consolas", 12, "bold"), anchor="w", cursor="hand2")
        lbl.pack(side="left")
        lbl.bind("<Button-1>", lambda e, i=idx: self._show_detail(i))

        badges = tk.Frame(top, bg=C["card"])
        badges.pack(side="right")

        if is_verified:
            tk.Label(badges, text="\u2705 \u5df2\u9a8c\u8bc1", bg=C["badge_active"], fg=C["green"],
                    font=("Microsoft YaHei", 7, "bold"), padx=5, pady=1).pack(side="right", padx=(3, 0))
        elif status == "active":
            tk.Label(badges, text="\U0001f7e1 \u5f85\u9a8c\u8bc1", bg=C["badge_unverified"], fg=C["orange"],
                    font=("Microsoft YaHei", 7, "bold"), padx=5, pady=1).pack(side="right", padx=(3, 0))

        icon = STATUS_ICONS.get(status, "")
        clr = STATUS_COLORS.get(status, C["muted"])
        bg_clr = {"active": C["badge_active"], "used": C["badge_used"],
                  "expired": C["badge_expired"], "invalid": C["badge_invalid"]}.get(status, C["card"])
        tk.Label(badges, text=f"{icon} {status_labels.get(status, status)}", bg=bg_clr, fg=clr,
                font=("Microsoft YaHei", 7, "bold"), padx=5, pady=1).pack(side="right", padx=(3, 0))

        rw = code.get("rewards", "")
        if len(rw) > 58:
            rw = rw[:55] + "..."
        tk.Label(inner, text=rw, bg=C["card"], fg=C["fg"],
                font=("Microsoft YaHei", 8), anchor="w").pack(fill="x", pady=(3, 0))

        info = tk.Frame(inner, bg=C["card"])
        info.pack(fill="x", pady=(1, 0))
        tk.Label(info, text=f"{code.get('source', '')}", bg=C["card"], fg=C["muted"],
                font=("Microsoft YaHei", 7)).pack(side="left")
        tk.Label(info, text=f"\u23f0 {code.get('expires', '')}", bg=C["card"], fg=C["muted"],
                font=("Microsoft YaHei", 7)).pack(side="right")

        note = code.get("note", "")
        if note and status in ("invalid", "expired"):
            tk.Label(inner, text=f"\U0001f4a1 {note}", bg=C["card"], fg=C["orange"],
                    font=("Microsoft YaHei", 7), anchor="w", wraplength=500).pack(fill="x", pady=(1, 0))

        actions = tk.Frame(inner, bg=C["card"])
        actions.pack(fill="x", pady=(5, 0))

        if status == "active":
            tk.Button(actions, text="\u6807\u8bb0\u5df2\u4f7f\u7528", bg=C["btn_primary"], fg="white",
                     font=("Microsoft YaHei", 7), borderwidth=0, padx=8, pady=2, cursor="hand2",
                     activebackground=C["btn_primary_hover"],
                     command=lambda c=code["code"]: self._mark_used(c)).pack(side="left", padx=(0, 3))
            if not is_verified:
                tk.Button(actions, text="\u6807\u8bb0\u5df2\u9a8c\u8bc1", bg=C["btn_secondary"], fg=C["green"],
                         font=("Microsoft YaHei", 7), borderwidth=0, padx=8, pady=2, cursor="hand2",
                         activebackground=C["btn_secondary_hover"],
                         command=lambda c=code["code"]: self._verify_code(c)).pack(side="left", padx=(0, 3))
            tk.Button(actions, text="\u590d\u5236", bg=C["btn_secondary"], fg=C["accent"],
                     font=("Microsoft YaHei", 7), borderwidth=0, padx=8, pady=2, cursor="hand2",
                     command=lambda c=code["code"]: self._copy_code(c)).pack(side="left")
        elif status == "used":
            tk.Button(actions, text="\u6062\u590d", bg=C["btn_danger"], fg="white",
                     font=("Microsoft YaHei", 7), borderwidth=0, padx=8, pady=2, cursor="hand2",
                     activebackground=C["btn_danger_hover"],
                     command=lambda c=code["code"]: self._mark_unused(c)).pack(side="left", padx=(0, 3))
            tk.Button(actions, text="\u590d\u5236", bg=C["btn_secondary"], fg=C["accent"],
                     font=("Microsoft YaHei", 7), borderwidth=0, padx=8, pady=2, cursor="hand2",
                     command=lambda c=code["code"]: self._copy_code(c)).pack(side="left")
        else:
            tk.Button(actions, text="\u590d\u5236", bg=C["btn_secondary"], fg=C["muted"],
                     font=("Microsoft YaHei", 7), borderwidth=0, padx=8, pady=2, cursor="hand2",
                     command=lambda c=code["code"]: self._copy_code(c)).pack(side="left")

        for w in [card, inner, top, info]:
            w.bind("<Button-1>", lambda e, i=idx: self._show_detail(i))

    def _show_detail(self, idx):
        codes = self._get_game_data().get("codes", [])
        if idx >= len(codes):
            return
        code = codes[idx]
        status = self._get_code_status(code)
        is_verified = code.get("verified", False)
        self._current_code_index = idx

        self.lbl_code.config(text=code["code"],
                            fg=C["code_fg"] if status == "active" else C["muted"],
                            justify="left", anchor="w")

        if status == "active" and is_verified:
            self.lbl_status.config(text="\u2705 \u5df2\u9a8c\u8bc1\u6709\u6548", fg=C["green"])
        elif status == "active":
            self.lbl_status.config(text="\U0001f7e1 \u6709\u6548\uff08\u5f85\u9a8c\u8bc1\uff09", fg=C["orange"])
        elif status == "used":
            self.lbl_status.config(text="\u2714\ufe0f \u5df2\u4f7f\u7528", fg=C["used"])
        elif status == "expired":
            self.lbl_status.config(text="\u23f0 \u5df2\u8fc7\u671f", fg=C["red"])
        else:
            self.lbl_status.config(text="\u274c \u5df2\u5931\u6548", fg=C["red"])

        rewards = code.get("rewards", "").replace("\u3001", "\n  \u2022 ")
        self.lbl_rewards.config(text=f"\U0001f381 \u5956\u52b1:\n  \u2022 {rewards}")
        self.lbl_source.config(text=f"\U0001f4e1 \u6765\u6e90: {code.get('source', '\u672a\u77e5')}")
        self.lbl_expires.config(text=f"\u23f0 \u6709\u6548\u671f: {code.get('expires', '\u672a\u77e5')}")
        note = code.get("note", "")
        self.lbl_note.config(text=f"\U0001f4a1 {note}" if note else "")

        self.btn_use.config(state="normal" if status == "active" else "disabled")
        self.btn_unuse.config(state="normal" if status == "used" else "disabled")
        for b in [self.btn_copy_detail, self.btn_edit_code, self.btn_del_code]:
            b.config(state="normal")

    def _clear_detail(self):
        self._current_code_index = None
        self.lbl_code.config(text="\u70b9\u51fb\u5de6\u4fa7\u5361\u7247\u67e5\u770b\u8be6\u60c5", fg=C["muted"], justify="center")
        for lbl in [self.lbl_status, self.lbl_rewards, self.lbl_source, self.lbl_expires, self.lbl_note]:
            lbl.config(text="")
        self._disable_detail_buttons()

    def _disable_detail_buttons(self):
        for btn in [self.btn_use, self.btn_unuse, self.btn_copy_detail, self.btn_edit_code, self.btn_del_code]:
            btn.config(state="disabled")

    # ============ Actions (continued in chunk3) ============

    def _mark_used(self, code_str):
        state_key = f"{self._current_game}:{code_str}"
        self.user_state.setdefault("used_codes", {})[state_key] = {
            "used_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_user_state(self.user_state)
        self._refresh_code_list()
        self.status_bar.config(text=f"\u2705 \u5df2\u6807\u8bb0 {code_str} \u4e3a\u5df2\u4f7f\u7528")

    def _mark_unused(self, code_str):
        state_key = f"{self._current_game}:{code_str}"
        if state_key in self.user_state.get("used_codes", {}):
            del self.user_state["used_codes"][state_key]
            save_user_state(self.user_state)
        self._refresh_code_list()
        self.status_bar.config(text=f"\U0001f504 \u5df2\u6062\u590d {code_str} \u4e3a\u672a\u4f7f\u7528")

    def _mark_current_used(self):
        if self._current_code_index is not None:
            codes = self._get_game_data().get("codes", [])
            if self._current_code_index < len(codes):
                self._mark_used(codes[self._current_code_index]["code"])

    def _mark_current_unused(self):
        if self._current_code_index is not None:
            codes = self._get_game_data().get("codes", [])
            if self._current_code_index < len(codes):
                self._mark_unused(codes[self._current_code_index]["code"])

    def _verify_code(self, code_str):
        codes = self._get_game_data().get("codes", [])
        for c in codes:
            if c["code"] == code_str:
                c["verified"] = True
                c["note"] = f"\u7528\u6237\u9a8c\u8bc1\u4e8e {datetime.now().strftime('%m/%d')}"
                break
        save_data(self.data)
        self._refresh_code_list()
        self.status_bar.config(text=f"\u2705 \u5df2\u5c06 {code_str} \u6807\u8bb0\u4e3a\u5df2\u9a8c\u8bc1")

    def _copy_code(self, code_str):
        self.root.clipboard_clear()
        self.root.clipboard_append(code_str)
        self.root.update()
        self.status_bar.config(text=f"\U0001f4cb \u5df2\u590d\u5236: {code_str}")

    def _copy_current_code(self):
        if self._current_code_index is not None:
            codes = self._get_game_data().get("codes", [])
            if self._current_code_index < len(codes):
                self._copy_code(codes[self._current_code_index]["code"])

    def _copy_all_valid(self):
        codes = self._get_game_data().get("codes", [])
        valid = [c["code"] for c in codes
                 if self._get_code_status(c) == "active" and c.get("verified", False)]
        if valid:
            text = "\n".join(valid)
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            self.status_bar.config(text=f"\U0001f4cb \u5df2\u590d\u5236 {len(valid)} \u4e2a\u5df2\u9a8c\u8bc1\u6709\u6548\u5151\u6362\u7801")
        else:
            messagebox.showinfo("\u63d0\u793a", "\u6ca1\u6709\u5df2\u9a8c\u8bc1\u7684\u6709\u6548\u5151\u6362\u7801")

    # ============ Dialogs ============
    def _add_code_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("\u6dfb\u52a0\u5151\u6362\u7801")
        dialog.geometry("420x420")
        dialog.configure(bg=C["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        fields = [
            ("\u5151\u6362\u7801 *", "code"),
            ("\u5956\u52b1\u5185\u5bb9", "rewards"),
            ("\u6765\u6e90", "source"),
            ("\u6709\u6548\u671f (\u5982: \u957f\u671f\u6709\u6548 \u6216 2026-06-01)", "expires"),
        ]

        entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(dialog, text=label, bg=C["bg"], fg=C["fg"],
                    font=("Microsoft YaHei", 9), anchor="w").pack(fill="x", padx=20, pady=(10 if i == 0 else 2, 0))
            e = tk.Entry(dialog, bg=C["card"], fg=C["fg"], insertbackground=C["fg"],
                        font=("Consolas", 10), relief="solid", bd=1)
            e.pack(fill="x", padx=20, ipady=3)
            entries[key] = e

        def do_add():
            code_str = entries["code"].get().strip()
            if not code_str:
                messagebox.showwarning("\u8b66\u544a", "\u8bf7\u8f93\u5165\u5151\u6362\u7801", parent=dialog)
                return
            # Check duplicate
            for c in self._get_game_data().get("codes", []):
                if c["code"] == code_str:
                    messagebox.showwarning("\u8b66\u544a", f"\u5151\u6362\u7801 {code_str} \u5df2\u5b58\u5728", parent=dialog)
                    return

            new_code = {
                "code": code_str,
                "rewards": entries["rewards"].get().strip() or "\u672a\u77e5",
                "source": entries["source"].get().strip() or "\u7528\u6237\u6dfb\u52a0",
                "expires": entries["expires"].get().strip() or "\u957f\u671f\u6709\u6548",
                "type": "\u6c38\u4e45" if "\u957f\u671f" in (entries["expires"].get().strip() or "\u957f\u671f") else "\u9650\u65f6",
                "status": "active",
                "verified": False,
                "found_date": datetime.now().strftime("%Y-%m-%d"),
                "note": "\u7528\u6237\u6dfb\u52a0"
            }
            self._get_game_data()["codes"].append(new_code)
            save_data(self.data)
            self._refresh_code_list()
            self.status_bar.config(text=f"\u2795 \u5df2\u6dfb\u52a0: {code_str}")
            dialog.destroy()

        tk.Button(dialog, text="\u2795 \u786e\u8ba4\u6dfb\u52a0", bg=C["btn_primary"], fg="white",
                 font=("Microsoft YaHei", 10), borderwidth=0, padx=16, pady=6, cursor="hand2",
                 activebackground=C["btn_primary_hover"], command=do_add).pack(pady=(16, 4))

    def _add_game_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("\u6dfb\u52a0\u6e38\u620f")
        dialog.geometry("380x280")
        dialog.configure(bg=C["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        fields = [("\u6e38\u620f\u540d\u79f0 *", "name"), ("\u82f1\u6587\u540d", "name_en"),
                  ("\u5151\u6362\u65b9\u6cd5\u63d0\u793a", "redeem_hint"), ("\u56fe\u6807 emoji", "icon")]

        entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(dialog, text=label, bg=C["bg"], fg=C["fg"],
                    font=("Microsoft YaHei", 9), anchor="w").pack(fill="x", padx=20, pady=(10 if i == 0 else 2, 0))
            e = tk.Entry(dialog, bg=C["card"], fg=C["fg"], insertbackground=C["fg"],
                        font=("Microsoft YaHei", 10), relief="solid", bd=1)
            e.pack(fill="x", padx=20, ipady=3)
            entries[key] = e

        def do_add():
            name = entries["name"].get().strip()
            if not name:
                messagebox.showwarning("\u8b66\u544a", "\u8bf7\u8f93\u5165\u6e38\u620f\u540d\u79f0", parent=dialog)
                return
            gk = name.lower().replace(" ", "_").replace("\u00b7", "")
            if gk in self.data.get("games", {}):
                messagebox.showwarning("\u8b66\u544a", "\u8be5\u6e38\u620f\u5df2\u5b58\u5728", parent=dialog)
                return

            self.data.setdefault("games", {})[gk] = {
                "name": name,
                "name_en": entries["name_en"].get().strip() or name,
                "icon": entries["icon"].get().strip() or "\U0001f3ae",
                "redeem_hint": entries["redeem_hint"].get().strip() or "",
                "codes": [],
                "last_update": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "update_sources": []
            }
            self._game_keys = list(self.data["games"].keys())
            save_data(self.data)

            # Rebuild tabs
            for w in self.tab_buttons.values():
                w.destroy()
            self.tab_buttons.clear()
            tabs_frame = self.btn_add_game.master
            self.btn_add_game.pack_forget()
            for gk2 in self._game_keys:
                gd2 = self.data["games"][gk2]
                btn = tk.Button(tabs_frame, text=f" {gd2.get('icon','')} {gd2['name']} ",
                               bg=C["tab_bg"] if gk2 != gk else C["tab_active"],
                               fg=C["fg"] if gk2 != gk else "white",
                               font=("Microsoft YaHei", 10, "bold"),
                               borderwidth=0, padx=16, pady=8, cursor="hand2", relief="flat",
                               activebackground=C["tab_bg"],
                               command=lambda k=gk2: self._switch_game(k))
                btn.pack(side="left", padx=(0, 2))
                self.tab_buttons[gk2] = btn
            self.btn_add_game.pack(side="left", padx=(4, 0))
            self._current_game = gk
            self._update_tab_highlight()
            self._refresh_code_list()
            self.status_bar.config(text=f"\u2795 \u5df2\u6dfb\u52a0\u6e38\u620f: {name}")
            dialog.destroy()

        tk.Button(dialog, text="\u2795 \u786e\u8ba4\u6dfb\u52a0", bg=C["btn_primary"], fg="white",
                 font=("Microsoft YaHei", 10), borderwidth=0, padx=16, pady=6, cursor="hand2",
                 activebackground=C["btn_primary_hover"], command=do_add).pack(pady=(16, 4))

    def _edit_code_dialog(self):
        if self._current_code_index is None:
            return
        codes = self._get_game_data().get("codes", [])
        if self._current_code_index >= len(codes):
            return
        code = codes[self._current_code_index]

        dialog = tk.Toplevel(self.root)
        dialog.title(f"\u7f16\u8f91: {code['code']}")
        dialog.geometry("420x420")
        dialog.configure(bg=C["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        fields = [
            ("\u5151\u6362\u7801", "code"),
            ("\u5956\u52b1\u5185\u5bb9", "rewards"),
            ("\u6765\u6e90", "source"),
            ("\u6709\u6548\u671f", "expires"),
            ("\u5907\u6ce8", "note"),
        ]

        entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(dialog, text=label, bg=C["bg"], fg=C["fg"],
                    font=("Microsoft YaHei", 9), anchor="w").pack(fill="x", padx=20, pady=(10 if i == 0 else 2, 0))
            e = tk.Entry(dialog, bg=C["card"], fg=C["fg"], insertbackground=C["fg"],
                        font=("Consolas", 10), relief="solid", bd=1)
            e.insert(0, code.get(key, ""))
            e.pack(fill="x", padx=20, ipady=3)
            entries[key] = e

        verified_var = tk.BooleanVar(value=code.get("verified", False))
        tk.Checkbutton(dialog, text="\u5df2\u9a8c\u8bc1\u6709\u6548", variable=verified_var,
                      bg=C["bg"], fg=C["green"], selectcolor=C["bg"],
                      font=("Microsoft YaHei", 9), activebackground=C["bg"],
                      activeforeground=C["green"]).pack(anchor="w", padx=20, pady=(8, 0))

        def do_save():
            code["code"] = entries["code"].get().strip() or code["code"]
            code["rewards"] = entries["rewards"].get().strip()
            code["source"] = entries["source"].get().strip()
            code["expires"] = entries["expires"].get().strip()
            code["note"] = entries["note"].get().strip()
            code["verified"] = verified_var.get()
            save_data(self.data)
            self._refresh_code_list()
            self._show_detail(self._current_code_index)
            dialog.destroy()
            self.status_bar.config(text="\u270f\ufe0f \u5df2\u66f4\u65b0\u5151\u6362\u7801\u4fe1\u606f")

        tk.Button(dialog, text="\u270f\ufe0f \u4fdd\u5b58\u4fee\u6539", bg=C["btn_primary"], fg="white",
                 font=("Microsoft YaHei", 10), borderwidth=0, padx=16, pady=6, cursor="hand2",
                 activebackground=C["btn_primary_hover"], command=do_save).pack(pady=(16, 4))

    def _delete_code_dialog(self):
        if self._current_code_index is None:
            return
        codes = self._get_game_data().get("codes", [])
        if self._current_code_index >= len(codes):
            return
        code = codes[self._current_code_index]

        if messagebox.askyesno("\u786e\u8ba4\u5220\u9664",
                               f"\u786e\u5b9a\u8981\u5220\u9664\u5151\u6362\u7801 {code['code']} \u5417\uff1f\n\n\u6b64\u64cd\u4f5c\u4e0d\u53ef\u64a4\u9500\u3002"):
            del codes[self._current_code_index]
            save_data(self.data)
            self._clear_detail()
            self._refresh_code_list()
            self.status_bar.config(text=f"\U0001f5d1\ufe0f \u5df2\u5220\u9664: {code['code']}")

    # ============ Online crawl ============
    def _online_crawl(self):
        self.status_bar.config(text="\U0001f504 \u6b63\u5728\u8054\u7f51\u68c0\u67e5...")
        self.root.update()
        def worker():
            try:
                import requests
                sources = self._get_game_data().get("update_sources", [])
                reachable = 0
                for url in sources[:3]:
                    try:
                        r = requests.get(url, timeout=8, headers={
                            "User-Agent": "Mozilla/5.0"})
                        if r.status_code == 200:
                            reachable += 1
                    except:
                        pass
                if reachable > 0:
                    msg = f"\u2705 \u5df2\u68c0\u67e5 {reachable}/{min(3,len(sources))} \u4e2a\u6765\u6e90\uff0c\u6570\u636e\u53ef\u8fbe"
                else:
                    msg = "\u26a0\ufe0f \u8054\u7f51\u5931\u8d25\uff0c\u4f7f\u7528\u672c\u5730\u7f13\u5b58\u6570\u636e"
            except:
                msg = "\u26a0\ufe0f \u7f51\u7edc\u6a21\u5757\u672a\u5b89\u88c5"
            self.root.after(0, self._crawl_done, msg)
        threading.Thread(target=worker, daemon=True).start()

    def _crawl_done(self, msg):
        gd = self._get_game_data()
        gd["last_update"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        save_data(self.data)
        self.status_bar.config(text=msg)


def main():
    root = tk.Tk()
    app = MultiGameRedeemApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
