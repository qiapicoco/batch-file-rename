import os
import tkinter as tk
from tkinter import messagebox, filedialog, StringVar
import tkinter.ttk as ttk


def batch_rename_files(selected_items):
    try:
        for item in selected_items:
            base_name = os.path.basename(item)
            new_file_path = os.path.join(os.path.dirname(item), base_name)
            os.rename(item, new_file_path)
            print(f"Renamed {item} to {new_file_path}")
        messagebox.showinfo("成功", "文件重命名完成！")
    except FileNotFoundError:
        messagebox.showerror("错误", f"文件未找到！")
    except PermissionError:
        messagebox.showerror("错误", f"没有权限修改文件！")
    except Exception as e:
        messagebox.showerror("错误", f"发生了一个未知错误: {e}")


def browse_folder():
    directory = filedialog.askdirectory()
    if directory:
        entry_directory.delete(0, tk.END)
        entry_directory.insert(0, directory)
        list_files(directory)
        # 更新路径显示标签
        path_label.config(text=directory)


def handle_enter(event):
    directory = entry_directory.get()
    if os.path.isdir(directory):
        list_files(directory)
        path_label.config(text=directory)
    else:
        messagebox.showerror("错误", f"输入的路径 {directory} 不是有效的目录！")


def list_files(directory):
    global all_files_data
    try:
        all_items = os.listdir(directory)
        folders = []
        files = {}
        for item in all_items:
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                folders.append(item)
            else:
                ext = os.path.splitext(item)[1].lower()
                if ext not in files:
                    files[ext] = []
                files[ext].append(item)

        folders.sort()
        for ext in files:
            files[ext].sort()

        all_files_data = []
        for folder in folders:
            all_files_data.append(("文件夹", folder))

        for ext in sorted(files.keys()):
            for file in files[ext]:
                all_files_data.append((ext, file))

        # 获取所有扩展名
        extensions = ["所有"] + sorted(set([data[0] for data in all_files_data if data[0] != "文件夹"]))
        extension_combobox['values'] = extensions
        extension_combobox.set("所有")

        filter_files("所有")

    except FileNotFoundError:
        messagebox.showerror("错误", f"目录 {directory} 未找到！")


def filter_files(selected_extension):
    for item in tree.get_children():
        tree.delete(item)

    if selected_extension == "所有":
        for ext, name in all_files_data:
            tree.insert("", "end", values=(ext, name))
    else:
        for ext, name in all_files_data:
            if ext == selected_extension:
                tree.insert("", "end", values=(ext, name))

    # 固定“扩展名”列宽
    tree.column("扩展名", width=100, anchor=tk.CENTER)


def on_rename_click():
    selected_items = []
    for item in tree.selection():
        values = tree.item(item, "values")
        path = os.path.join(entry_directory.get(), values[1])
        selected_items.append(path)
    if not selected_items:
        messagebox.showwarning("警告", "请选择要重命名的文件或文件夹！")
        return
    batch_rename_files(selected_items)


# 创建主窗口
root = tk.Tk()
root.title("批量文件重命名")
root.option_add("*Font", "微软雅黑 10")
root.geometry("800x600")
root.configure(bg="#f0f0f0")

# 功能区
frame_function = ttk.Frame(root, padding="20")
frame_function.grid(row=0, column=0, sticky=(tk.W, tk.E))
tk.Label(frame_function, text="选择文件目录:").grid(row=0, column=0, sticky=tk.W)
entry_directory = ttk.Entry(frame_function, width=30)
entry_directory.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
entry_directory.insert(0, '.')
# 绑定回车事件
entry_directory.bind("<Return>", handle_enter)

button_browse = ttk.Button(frame_function, text="浏览", command=browse_folder)
button_browse.grid(row=0, column=2, padx=5)

# 显示完整路径的标签
path_label = tk.Label(frame_function, text="", wraplength=700, anchor=tk.W, font=("微软雅黑", 9, "italic"), fg="#808080")
path_label.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=2)

# 扩展名筛选下拉框
tk.Label(frame_function, text="筛选扩展名:").grid(row=2, column=0, sticky=tk.W)
extension_var = StringVar()
extension_combobox = ttk.Combobox(frame_function, textvariable=extension_var, state="readonly")
extension_combobox.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
extension_combobox.bind("<<ComboboxSelected>>", lambda event: filter_files(extension_var.get()))

# 文件显示区
frame_tree = ttk.Frame(root, padding="20")
frame_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)

columns = ("扩展名", "文件名")
# 创建 Treeview 时使用 style
style = ttk.Style()
style.configure("Custom.Treeview.Heading", background="#e0e0e0", foreground="black", font=("微软雅黑", 11))
style.configure("Custom.Treeview", font=("微软雅黑", 10), rowheight=int(10 * 1.8))

tree = ttk.Treeview(frame_tree, columns=columns, show="headings", selectmode="extended", style="Custom.Treeview")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)
    if col == "扩展名":
        tree.column(col, anchor=tk.CENTER)

tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
frame_tree.rowconfigure(0, weight=1)
frame_tree.columnconfigure(0, weight=1)

# “确认修改”按钮放在窗口右下角
button_rename = ttk.Button(root, text="确认修改", command=on_rename_click)
button_rename.grid(row=2, column=0, sticky=tk.SE, padx=20, pady=20)

all_files_data = []

# 运行主循环
root.mainloop()