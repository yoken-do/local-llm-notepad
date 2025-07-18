from __future__ import annotations

import json
import os
import queue
import re
import threading
from typing import List, Tuple
import webbrowser
from config import load_settings, save_settings
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, simpledialog, ttk  # noqa: F401 – same imports kept

from llm_utils import respond  # ← the only new import compared with original

__all__ = ["ChatGUI", "run_app"]



class ChatGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("local-llm-notepad")
        root.configure(bg="white")

        # ─────────────────── State ───────────────────
        self.settings = load_settings()
        self.model_path = self.settings["model"]["path"]
        self.system_prompt = self.settings["model"]["prompt"]

        # ─────────────────── Menus ───────────────────
        menubar = tk.Menu(root)

        file_menu = tk.Menu(menubar, tearoff=0)
        # file_menu.add_command(label="Select Model...", command=self.select_model)
        file_menu.add_command(label="Save Chat...", command=self.save_chat)
        file_menu.add_command(label="Load Chat...", command=self.load_chat)
        # file_menu.add_separator()
        # file_menu.add_command(label="Exit", command=self.exit_root)
        menubar.add_cascade(label="File", menu=file_menu)
        root.protocol("WM_DELETE_WINDOW", self.exit_root)

        model_menu = tk.Menu(menubar, tearoff=0)
        model_menu.add_command(label="Select Model", command=self.select_model)
        model_menu.add_command(label="Edit System Prompt", accelerator=f"{self.settings["bindings"]['edit-system-prompt']}", command=self.edit_system_prompt)
        menubar.add_cascade(label="Model", menu=model_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Send", accelerator=f"{self.settings["bindings"]['send']}", command=self.on_send)
        edit_menu.add_command(label="Stop Generation", accelerator=f"{self.settings["bindings"]['stop-generation']}", command=self.on_stop)
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", accelerator=f"{self.settings["bindings"]['find']}", command=self.open_find)
        edit_menu.add_command(label="Clear", accelerator=f"{self.settings["bindings"]['clear']}", command=self.on_clear)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Zoom In", accelerator="Control +", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out", accelerator="Control -", command=self.zoom_out)
        menubar.add_cascade(label="View", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="License", command=self.show_license)
        menubar.add_cascade(label="About", menu=help_menu)
        root.config(menu=menubar)

        # ─────────────────── Layout ───────────────────
        style = ttk.Style()
        style.configure(
            "Plain.TPanedwindow",
            background="white",
            borderwidth=0,
            relief="flat",
            sashwidth=4,
        )
        panes = ttk.PanedWindow(root, orient="vertical", style="Plain.TPanedwindow")
        panes.pack(fill=tk.BOTH, expand=True)

        # History
        hist_frame = tk.Frame(root, bg="white")
        self.history_text = tk.Text(
            hist_frame,
            wrap=tk.WORD,
            state="disabled",
            bg="white",
            bd=0,
            highlightthickness=0,
            font=("Arial", 10),
        )

        self.assistant_segments: list[tuple[str, str]] = []

        self.bold_font = tkfont.Font(self.history_text, self.history_text.cget("font"))
        self.bold_font.configure(weight="bold")
        self.style_on = True
        self._apply_word_style()

        self.history_text.tag_config("find_highlight", background="yellow")
        self.history_text.tag_config("user_word", font=self.bold_font, underline=True)
        vscroll_hist = tk.Scrollbar(hist_frame, command=self.history_text.yview)
        self.history_text.configure(yscrollcommand=vscroll_hist.set)
        vscroll_hist.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        panes.add(hist_frame, weight=4)

        # Input
        inp_frame = tk.Frame(root, bg="white")
        self.input_text = tk.Text(
            inp_frame,
            height=4,
            wrap=tk.WORD,
            bg="white",
            bd=0,
            highlightthickness=0,
            font=("Arial", 10),
        )
        self.input_text.focus_set()
        vscroll_inp = tk.Scrollbar(inp_frame, command=self.input_text.yview)
        self.input_text.configure(yscrollcommand=vscroll_inp.set)
        vscroll_inp.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        panes.add(inp_frame, weight=1)

        # ─────────────────── Internals ───────────────────
        self.queue: queue.Queue[str | None] = queue.Queue()
        self.gen_thread: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.history_data: List[dict] = []
        self._table_pattern = re.compile(
            r"(\|[^\n]+\|\n\|[ \-:|]+\|\n(?:\|[^\n]+\|\n?)*)",
            re.MULTILINE,
        )
        self.search_start = "1.0"

        # Window for user prompts (created on first ctrl-click)
        self.user_prompts_win: tk.Toplevel | None = None
        self.user_prompts_text: tk.Text | None = None

        # ────────── NEW: remember next search start for each word ──────────
        self.next_pos: dict[str, str] = {}

        # ─────────────────── Bindings ───────────────────
        root.bind(f"<{self.settings["bindings"]['send']}>", lambda e: self.on_send())
        root.bind(f"<{self.settings["bindings"]['find']}>", lambda e: self.open_find())
        root.bind(f"<{self.settings["bindings"]['edit-system-prompt']}>", lambda e: self.edit_system_prompt())
        root.bind(f"<{self.settings["bindings"]['stop-generation']}>", lambda e: self.on_stop())
        root.bind(f"<{self.settings["bindings"]['clear']}>", lambda e: self.on_clear())
        root.bind("<Control-MouseWheel>", self._on_ctrl_mousewheel)


    def exit_root(self):
        save_settings(self.settings, self.model_path, self.system_prompt)
        self.root.quit()

    def save_chat(self):
        if not self.history_data:
            messagebox.showinfo("Save Chat", "Nothing to save yet.")
            return

        path = filedialog.asksaveasfilename(
            title="Save Chat",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Save Chat", f"Chat saved to:\n{path}")
        except Exception as ex:
            messagebox.showerror("Save Chat", f"Failed to save:\n{ex}")

    def load_chat(self):
        if self.gen_thread and self.gen_thread.is_alive():
            messagebox.showinfo("Please wait", "Cannot load while generating.")
            return

        path = filedialog.askopenfilename(
            title="Load Chat",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list) or not all(
                    isinstance(d, dict) and "user" in d and "assistant" in d for d in data
            ):
                raise ValueError("File does not contain valid chat history.")
        except Exception as ex:
            messagebox.showerror("Load Chat", f"Could not load chat:\n{ex}")
            return

        # wipe current session
        self.on_clear()

        self.history_data = data
        self.history_text.config(state="normal")

        for entry in self.history_data:
            user_msg, assist_msg = entry["user"], entry["assistant"]
            # User line
            self.history_text.insert(tk.END, f"User: {user_msg}\nAssistant: ")
            assist_start = self.history_text.index("end-1c")
            # Assistant line
            self.history_text.insert(tk.END, assist_msg)
            assist_end = self.history_text.index("end-1c")
            self.assistant_segments.append((assist_start, assist_end))
            self.history_text.insert(tk.END, "\n\n")
            # apply post-processing (tables, link stripping, highlights, …)
            self._post_process(assist_start, assist_end)

        self.history_text.config(state="disabled")
        self.history_text.see(tk.END)
        messagebox.showinfo("Load Chat", f"Loaded {len(self.history_data)} turns.")


    # ─────────────────── System Prompt Editor ───────────────────
    def edit_system_prompt(self):
        """Open a dialog to edit the system prompt."""
        def save_and_close():
            self.system_prompt = text.get("1.0", tk.END).strip() or "You are a helpful assistant."
            win.destroy()

        win = tk.Toplevel(self.root)
        win.title("Edit System Prompt")
        win.transient(self.root)
        win.grab_set()

        text = tk.Text(win, wrap=tk.WORD, height=6, width=60)
        text.insert("1.0", self.system_prompt)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=(0, 10))

        tk.Button(btn_frame, text="Save", command=save_and_close).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side=tk.LEFT, padx=5)

        self._center_window(win)
        text.focus_set()

    # ─────────────────── Find dialog ───────────────────
    def open_find(self):
        if hasattr(self, "find_window") and self.find_window.winfo_exists():
            return
        self.find_window = tk.Toplevel(self.root)
        self.find_window.protocol("WM_DELETE_WINDOW", self._close_find)
        self.find_window.title("Find")
        self.find_window.transient(self.root)

        tk.Label(self.find_window, text="Find:").pack(side=tk.LEFT, padx=(10, 0), pady=10)
        self.find_entry = tk.Entry(self.find_window)
        self.find_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=10)
        self.find_entry.bind("<Return>", lambda e: self.find_next())
        tk.Button(self.find_window, text="Next", command=self.find_next).pack(
            side=tk.LEFT, padx=(0, 10), pady=10
        )

        # Center dialog
        self.find_window.update_idletasks()
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        win_w = self.find_window.winfo_width()
        win_h = self.find_window.winfo_height()
        x = root_x + (root_w - win_w) // 2
        y = root_y + (root_h - win_h) // 2
        self.find_window.geometry(f"+{x}+{y}")

        self.find_entry.focus_set()
        self.search_start = "1.0"

    def find_next(self):
        pattern = self.find_entry.get()
        if not pattern:
            return
        idx = self.history_text.search(pattern, self.search_start, tk.END, nocase=True)
        if not idx:
            messagebox.showinfo("Find", f"'{pattern}' not found")
            self.search_start = "1.0"
            return
        end_idx = f"{idx}+{len(pattern)}c"
        self.history_text.tag_remove("find_highlight", "1.0", tk.END)
        self.history_text.tag_add("find_highlight", idx, end_idx)
        self.history_text.see(idx)
        self.search_start = end_idx

    def _close_find(self):
        """Remove highlight and destroy the Find window."""
        self.history_text.tag_remove("find_highlight", "1.0", tk.END)
        if hasattr(self, "find_window") and self.find_window.winfo_exists():
            self.find_window.destroy()

    # ─────────────────── Helpers ───────────────────
    def _on_ctrl_mousewheel(self, event):
        self.zoom_in() if event.delta > 0 else self.zoom_out()

    def select_model(self):
        path = filedialog.askopenfilename(
            title="Select Model",
            initialdir="models",
            filetypes=[("GGUF Model", "*.gguf"), ("All files", "*.*")],
        )
        if path:
            self.model_path = path
            messagebox.showinfo("Model Selected", f"Model set to:\n{path}")

    def zoom_in(self):
        for w in (self.input_text, self.history_text):
            f = tkfont.Font(font=w.cget("font"))
            f.configure(size=f.cget("size") + 1)
            w.config(font=f)
        self._refresh_bold_font()

    def zoom_out(self):
        for w in (self.input_text, self.history_text):
            f = tkfont.Font(font=w.cget("font"))
            s = f.cget("size")
            if s > 6:
                f.configure(size=s - 1)
                w.config(font=f)
        self._refresh_bold_font()

    def show_about(self):
        # Create a small About window
        win = tk.Toplevel(self.root)
        win.title("About")
        win.transient(self.root)
        win.resizable(False, False)

        # Main text
        text = (
            "local-llm-notepad\n"
            "fork of the 'Local LLM Notepad' project\n"
            "Version: 0.0.1\n"
            "Fork author: yo (Github: yoken-do)\n"
            "Built with tkinter and llama-cpp-python\n\n"
        )
        lbl = tk.Label(win, text=text, justify=tk.LEFT, bg="white")
        lbl.pack(padx=15, pady=(15, 5), anchor="w")      

        # OK button to close
        btn = tk.Button(win, text="OK", command=win.destroy)
        btn.pack(pady=(0, 15))

        # Center it over the main window
        self._center_window(win)

    def show_license(self):
        win = tk.Toplevel(self.root)
        win.title("License")
        win.transient(self.root)
        win.resizable(False, False)

        # Main text
        text = (
            "Local LLM Notepad (c) by Run Zhou Ye\n\n"
            "Licensed under a Creative Commons\n"
            "Attribution-NonCommercial 4.0 International License.\n\n"
            "You should have received a copy of the license\n"
            "along with this work. If not, see:"
        )
        lbl = tk.Label(win, text=text, justify=tk.LEFT, bg="white")
        lbl.pack(padx=15, pady=(15, 5), anchor="w")   

        link = "https://creativecommons.org/licenses/by-nc/4.0/"
        link_lbl = tk.Label(
            win,
            text=link,
            fg="blue",
            cursor="hand2",
            underline=True,
            bg="white",
        )
        link_lbl.pack(padx=15, pady=(0, 15), anchor="w")
        link_lbl.bind(
            "<Button-1>",
            lambda e, url=link: webbrowser.open_new(url)
        )   
        # OK button to close
        btn = tk.Button(win, text="OK", command=win.destroy)
        btn.pack(pady=(0, 15))

        # Center it over the main window
        self._center_window(win)

    # ─────────────────── Chat actions ───────────────────
    def on_send(self):
        if self.gen_thread and self.gen_thread.is_alive():
            messagebox.showinfo(
                "Please wait", "Generation in progress.\nPress Ctrl+Z to stop first."
            )
            return

        prompt = self.input_text.get("1.0", tk.END).strip()
        if not prompt:
            return

        self.history_data.append({"user": prompt, "assistant": ""})
        prev = [(d["user"], d["assistant"]) for d in self.history_data[:-1]]

        self.history_text.config(state="normal")
        self.history_text.insert(tk.END, f"User: {prompt}\nAssistant: ")
        self.assist_start = self.history_text.index("end-1c")
        self.history_text.config(state="disabled")

        self.input_text.delete("1.0", tk.END)
        self.history_text.see(tk.END)

        self.queue = queue.Queue()
        self.stop_event.clear()
        self.gen_thread = threading.Thread(
            target=self._worker_generate, args=(prompt, prev), daemon=True
        )
        self.gen_thread.start()
        self.history_text.after(50, self._process_queue)

    def on_stop(self):
        if self.gen_thread and self.gen_thread.is_alive():
            self.stop_event.set()

    def on_clear(self):
        if self.gen_thread and self.gen_thread.is_alive():
            messagebox.showinfo("Please wait", "Cannot clear while generating.")
            return
        self.history_data.clear()
        self.history_text.config(state="normal")
        self.history_text.delete("1.0", tk.END)
        self.history_text.config(state="disabled")
        self.input_text.delete("1.0", tk.END)
        self.assistant_segments.clear()

    # ─────────────────── Generation thread ───────────────────
    def _worker_generate(self, prompt: str, history: List[Tuple[str, str]]):
        last = ""
        try:
            for full in respond(
                prompt,
                history,
                model=self.model_path,
                system_message=self.system_prompt,
            ):
                if self.stop_event.is_set():
                    break
                delta = full[len(last) :]
                self.queue.put(delta)
                last = full
        except Exception as e:
            self.queue.put(f"[Error] {e}\n")
        finally:
            if self.history_data:
                self.history_data[-1]["assistant"] = last
            self.queue.put(None)

    def _process_queue(self):
        while True:
            try:
                item = self.queue.get_nowait()
            except queue.Empty:
                break
            if item is None:
                self.history_text.config(state="normal")
                self.history_text.insert(tk.END, "\n\n\n\n")
                end_pos = self.history_text.index("end-1c")
                self._post_process(self.assist_start, end_pos)
                self.history_text.config(state="disabled")
                return
            at_bot = float(self.history_text.yview()[1]) >= 0.99
            self.history_text.config(state="normal")
            self.history_text.insert(tk.END, item)
            self.history_text.config(state="disabled")
            if at_bot:
                self.history_text.see(tk.END)
        if self.gen_thread and self.gen_thread.is_alive():
            self.history_text.after(50, self._process_queue)

    # ─────────────────── Post-processing ───────────────────
    def _post_process(self, start: str, end: str):
        raw = self.history_text.get(start, end)
        clean = re.sub(r"\*\*(.*?)\*\*", r"\1", raw)
        clean = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1: \2", clean)
        clean = self._table_pattern.sub(lambda m: self._md_table_to_tsv(m.group(1)), clean)

        if clean != raw:
            self.history_text.delete(start, end)
            self.history_text.insert(start, clean)

        self.history_text.tag_remove("user_word", start, end)
        self._highlight_user_words(start, end)
        self.assistant_segments.append((start, end))

    def _highlight_user_words(self, start: str, end: str):
        """
        Bold-underline every token appearing in ANY user prompt, including:
          • plain words   → hello
          • numbers       → 45, 3.14
          • dims (NxM…)   → 2x5, 4x3x2
        """
        tokens: set[str] = set()

        word_re = re.compile(r"[A-Za-z']+")
        num_re = re.compile(r"\d+(?:\.\d+)?")
        dim_re = re.compile(r"\d+(?:x\d+)+", re.I)

        for entry in self.history_data:
            txt = entry["user"]
            tokens.update(m.group(0) for m in word_re.finditer(txt))
            tokens.update(m.group(0) for m in num_re.finditer(txt))
            tokens.update(m.group(0) for m in dim_re.finditer(txt))

        if not tokens:
            return

        for tok in tokens:
            pure_word = re.match(r"^\w+$", tok) is not None

            if pure_word:  # word → use \m..\M
                pattern = rf"\m{re.escape(tok)}\M"
                use_regex = True
            else:  # number / dim
                pattern = tok
                use_regex = False

            idx = start
            while True:
                idx = self.history_text.search(
                    pattern, idx, end, nocase=True, regexp=use_regex
                )
                if not idx:
                    break
                end_idx = f"{idx}+{len(tok)}c"
                self.history_text.tag_add("user_word", idx, end_idx)
                idx = end_idx

    # ─── apply current style to the tag ─────────────────────────────
    def _apply_word_style(self):
        if self.style_on:
            self.history_text.tag_config("user_word", font=self.bold_font, underline=True)
        else:  # plain
            self.history_text.tag_config(
                "user_word", font=self.history_text.cget("font"), underline=False
            )

    def _center_window(self, win: tk.Toplevel):
        """Position <win> in the center of the root window."""
        win.update_idletasks()  # make sure size is known
        root_x, root_y = self.root.winfo_x(), self.root.winfo_y()
        root_w, root_h = self.root.winfo_width(), self.root.winfo_height()
        win_w, win_h = win.winfo_width(), win.winfo_height()
        x = root_x + max((root_w - win_w) // 2, 0)
        y = root_y + max((root_h - win_h) // 2, 0)
        win.geometry(f"+{x}+{y}")

    # ─────────────────── Markdown utilities ───────────────────
    @staticmethod
    def _md_table_to_tsv(md: str) -> str:
        lines = md.strip().splitlines()
        header = [c.strip() for c in lines[0].strip("|").split("|")]
        rows = [[c.strip() for c in ln.strip("|").split("|")] for ln in lines[2:] if ln.startswith("|")]
        tsv = "\t".join(header) + "\n"
        tsv += "\n".join("\t".join(r) for r in rows) + "\n"
        return tsv


def run_app() -> None:
    """Create Tk root and start the main loop (used by main.py)."""
    root = tk.Tk()
    ChatGUI(root)
    root.mainloop()
