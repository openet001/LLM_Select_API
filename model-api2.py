import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

CONFIG_FILE = "llm_model_settings.json"
MODEL_NAMES_FILE = "llm_model_names.json"

MODEL_CONFIGS = {
    '百智云': [
        {'label': 'API 地址', 'key': 'api_url', 'default': 'https://model-square.app.baizhi.cloud/v1'},
        {'label': 'API Key', 'key': 'api_secret', 'default': ''},
        {'label': '模型名称', 'key': 'model_name', 'default': '', 'type': 'combobox+entry', 'options': []},
    ],
    'DeepSeek': [
        {'label': 'API 地址', 'key': 'api_url', 'default': ''},
        {'label': 'API Key', 'key': 'api_key', 'default': ''},
        {'label': '模型名称', 'key': 'model_name', 'default': '', 'type': 'combobox+entry', 'options': []},
    ],
    '腾讯混元': [
        {'label': 'API 地址', 'key': 'api_url', 'default': ''},
        {'label': 'API Key', 'key': 'api_key', 'default': ''},
        {'label': '模型名称', 'key': 'model_name', 'default': '', 'type': 'combobox+entry', 'options': []},
    ],
    '阿里云百炼': [
        {'label': 'API 地址', 'key': 'api_url', 'default': ''},
        {'label': 'API Key', 'key': 'api_key', 'default': ''},
        {'label': '模型名称', 'key': 'model_name', 'default': '', 'type': 'combobox+entry', 'options': []},
    ],
    '火山引擎': [
        {'label': 'API 地址', 'key': 'api_url', 'default': ''},
        {'label': 'API Key', 'key': 'api_key', 'default': ''},
        {'label': '模型名称', 'key': 'model_name', 'default': '', 'type': 'combobox+entry', 'options': []},
    ],
    'OpenAI': [
        {'label': 'API 地址', 'key': 'api_url', 'default': 'https://api.openai.com/v1'},
        {'label': 'API Key', 'key': 'api_key', 'default': ''},
        {'label': '模型名称', 'key': 'model_name', 'default': '', 'type': 'combobox+entry', 'options': []},
    ],
    'Ollama': [
        {'label': 'API 地址', 'key': 'api_url', 'default': 'http://localhost:11434'},
        {'label': 'API Key', 'key': 'api_key', 'default': ''},
        {'label': '模型名称', 'key': 'model_name', 'default': '', 'type': 'combobox+entry', 'options': []},
    ],
    '硅基流动': [
        {'label': 'API 地址', 'key': 'api_url', 'default': ''},
        {'label': 'API Key', 'key': 'api_key', 'default': ''},
        {'label': '模型名称', 'key': 'model_name', 'default': '', 'type': 'combobox+entry', 'options': []},
    ],
    '月之暗面': [
        {'label': 'API 地址', 'key': 'api_url', 'default': ''},
        {'label': 'API Key', 'key': 'api_key', 'default': ''},
        {'label': '模型名称', 'key': 'model_name', 'default': '', 'type': 'combobox+entry', 'options': []},
    ],
    'Azure OpenAI': [
        {'label': 'API 地址', 'key': 'api_url', 'default': ''},
        {'label': 'API Key', 'key': 'api_key', 'default': ''},
        {'label': '模型名称', 'key': 'model_name', 'default': '', 'type': 'combobox+entry', 'options': []},
    ],
    '其他': [
        {'label': 'API 地址', 'key': 'api_url', 'default': ''},
        {'label': 'API Key', 'key': 'api_key', 'default': ''},
        {'label': '模型名称', 'key': 'model_name', 'default': '', 'type': 'combobox+entry', 'options': []},
    ],
}

class ModelConfigApp:
    def __init__(self, root):
        self.root = root
        self.root.title("主流大模型 API 配置界面")
        self.root.geometry("950x460")
        self.model_vars = {}
        self.current_model = None
        self.saved_settings = self.load_settings()
        self.model_names_dict = self.load_model_names()
        # 左侧模型列表
        left_frame = ttk.Frame(root)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=12, pady=12)
        ttk.Label(left_frame, text="模型供应商", font=('微软雅黑', 13, 'bold')).pack(anchor='w', pady=(0, 8))
        self.model_listbox = tk.Listbox(left_frame, height=len(MODEL_CONFIGS), font=('微软雅黑', 11))
        for m in MODEL_CONFIGS.keys():
            self.model_listbox.insert(tk.END, m)
        self.model_listbox.pack(anchor='w', pady=2, fill=tk.Y)
        self.model_listbox.bind("<<ListboxSelect>>", self.on_model_select)
        self.model_listbox.selection_set(0)
        # 右侧参数区
        self.form_frame = ttk.Frame(root)
        self.form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=18, pady=12)
        self.form_title = ttk.Label(self.form_frame, text="模型配置", font=('微软雅黑', 13, 'bold'))
        self.form_title.grid(row=0, column=0, sticky="w", pady=(0, 8), columnspan=2)
        self.param_widgets = []
        self.save_btn = ttk.Button(self.form_frame, text="保存配置", command=self.save_config)
        self.save_btn.grid(row=99, column=0, pady=18, sticky="w")
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.form_frame, textvariable=self.status_var, font=('微软雅黑', 10), foreground="green")
        self.status_label.grid(row=100, column=0, columnspan=2, sticky="w")
        self.show_model_form('百智云')

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_settings(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.saved_settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("保存失败", f"保存配置文件失败: {e}")

    def load_model_names(self):
        if os.path.exists(MODEL_NAMES_FILE):
            try:
                with open(MODEL_NAMES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_model_names(self):
        try:
            with open(MODEL_NAMES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.model_names_dict, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("保存失败", f"保存模型名称文件失败: {e}")

    def on_model_select(self, event):
        selection = self.model_listbox.curselection()
        if not selection:
            return
        model = self.model_listbox.get(selection[0])
        self.show_model_form(model)

    def show_model_form(self, model):
        for w in self.param_widgets:
            w.destroy()
        self.param_widgets.clear()
        self.current_model = model
        self.form_title.config(text=f"{model} 配置")
        params = MODEL_CONFIGS[model]
        self.model_vars[model] = {}
        saved = self.saved_settings.get(model, {})
        saved_names = self.model_names_dict.get(model, [])
        row_idx = 1
        for param in params:
            ttk.Label(self.form_frame, text=param['label'] + ":", font=('微软雅黑', 11)).grid(row=row_idx, column=0, sticky="e", pady=6)
            if param.get('type') == 'combobox+entry':
                # 下拉+手工输入
                var = tk.StringVar(value=saved.get(param['key'], param.get('default', '')))
                cb = ttk.Combobox(self.form_frame, textvariable=var, width=40, state="readonly")
                cb['values'] = saved_names if saved_names else ['']
                cb.grid(row=row_idx, column=1, sticky="w", pady=6)
                self.param_widgets.append(cb)
                # 增加手工录入框
                entry_var = tk.StringVar()
                entry = ttk.Entry(self.form_frame, textvariable=entry_var, width=32)
                entry.grid(row=row_idx, column=2, sticky="w", padx=4)
                add_btn = ttk.Button(self.form_frame, text="添加/批量（;号分隔）", command=lambda v=var, ev=entry_var, cb=cb, m=model: self.add_model_names(v, ev, cb, m))
                add_btn.grid(row=row_idx, column=3, sticky="w")
                self.param_widgets.extend([entry, add_btn])
                self.model_vars[model][param['key']] = var
                self.model_vars[model][f"{param['key']}_entry"] = entry_var
            else:
                var = tk.StringVar(value=saved.get(param['key'], param.get('default', '')))
                entry = ttk.Entry(self.form_frame, textvariable=var, width=42)
                entry.grid(row=row_idx, column=1, sticky="w", pady=6)
                self.param_widgets.append(entry)
                self.model_vars[model][param['key']] = var
            row_idx += 1

    def add_model_names(self, combobox_var, entry_var, combobox_widget, model):
        names_str = entry_var.get()
        names = [n.strip() for n in names_str.split(";") if n.strip()]
        if not names:
            messagebox.showinfo("提示", "请输入模型名称，多个名称请用分号“;”分隔")
            return
        old_names = self.model_names_dict.get(model, [])
        new_names = []
        for n in names:
            if n not in old_names:
                old_names.append(n)
                new_names.append(n)
        self.model_names_dict[model] = old_names
        self.save_model_names()
        # 更新下拉列表
        combobox_widget['values'] = old_names
        if new_names:
            combobox_var.set(new_names[0])
        entry_var.set("")
        self.status_var.set(f"已添加模型名称: {';'.join(new_names)}")

    def save_config(self):
        if not self.current_model:
            return
        params = {}
        for key, var in self.model_vars[self.current_model].items():
            # 只保存combobox内容
            if key.endswith('_entry'):
                continue
            params[key] = var.get()
        self.saved_settings[self.current_model] = params
        self.save_settings()
        self.status_var.set(f"{self.current_model} 配置已保存到 {CONFIG_FILE}")

    @staticmethod
    def load_model_config(model_name):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                all_cfg = json.load(f)
            return all_cfg.get(model_name, {})
        return {}

if __name__ == "__main__":
    root = tk.Tk()
    app = ModelConfigApp(root)
    root.mainloop()