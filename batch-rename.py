import os
import tkinter as tk
from tkinter import messagebox, filedialog, StringVar, simpledialog
import tkinter.ttk as ttk
import webbrowser


def batch_rename_files(selected_items):
    try:
        for item in selected_items:
            base_name = os.path.basename(item)
            new_file_path = os.path.join(os.path.dirname(item), base_name)
            os.rename(item, new_file_path)
            print(f"Renamed {item} to {new_file_path}")
        messagebox.showinfo("成功", "文件重命名完成！")
        open_folder(entry_directory.get())
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
    global selected_items
    for item in tree.get_children():
        tree.delete(item)
    selected_items = []

    filtered_files = []
    if selected_extension == "所有":
        filtered_files = all_files_data
    else:
        for ext, name in all_files_data:
            if ext == selected_extension:
                filtered_files.append((ext, name))

    for index, (ext, name) in enumerate(filtered_files, start=1):
        add_item_to_tree(index, ext, name)

    # 固定“序号”列宽
    tree.column("序号", width=50, anchor=tk.CENTER)
    # 固定“扩展名”列宽
    tree.column("扩展名", width=100, anchor=tk.CENTER)


def add_item_to_tree(index, ext, name):
    item = tree.insert("", "end", values=(index, ext, name))
    tree.item(item, tags=(item,))


def get_selected_items():
    selected = []
    for item in tree.selection():
        values = tree.item(item, "values")
        path = os.path.join(entry_directory.get(), values[2])
        selected.append(path)
    return selected


def batch_change_extension():
    selected = get_selected_items()
    if not selected:
        messagebox.showwarning("警告", "请选择要修改扩展名的文件！")
        return
    folders_selected = [item for item in selected if os.path.isdir(item)]
    if folders_selected:
        folder_names = ", ".join([os.path.basename(folder) for folder in folders_selected])
        messagebox.showerror("错误", f"你选择了文件夹：{folder_names}，文件夹不允许修改扩展名，请重新选择文件。")
        return
    new_ext = simpledialog.askstring("输入新扩展名", "请输入新的文件扩展名（不包含点号）：")
    if new_ext:
        new_ext = "." + new_ext
        for item in selected:
            if os.path.isfile(item):  # 仅处理文件
                base_name, _ = os.path.splitext(os.path.basename(item))
                new_file_path = os.path.join(os.path.dirname(item), base_name + new_ext)
                try:
                    os.rename(item, new_file_path)
                    print(f"Renamed {item} to {new_file_path}")
                except FileNotFoundError:
                    messagebox.showerror("错误", f"文件 {item} 未找到！")
                except PermissionError:
                    messagebox.showerror("错误", f"没有权限修改文件 {item}！")
                except Exception as e:
                    messagebox.showerror("错误", f"发生了一个未知错误: {e}")
        messagebox.showinfo("成功", "文件扩展名修改完成！")
        open_folder(entry_directory.get())
        list_files(entry_directory.get())


def batch_rename_file_names():
    selected = get_selected_items()
    if not selected:
        messagebox.showwarning("警告", "请选择要重命名的文件！")
        return

    first_new_name = simpledialog.askstring("输入第一个新文件名", "请输入第一个新文件名（例如：图片_1）：")
    if not first_new_name:
        return

    try:
        prefix, start_num_str = first_new_name.rsplit("_", 1)
        start_num = int(start_num_str)
    except ValueError:
        messagebox.showerror("错误", "输入的文件名格式不正确，请使用类似 '图片_1' 的格式。")
        return

    ext_groups = {}
    for item in selected:
        if os.path.isfile(item):
            ext = os.path.splitext(item)[1]
            if ext not in ext_groups:
                ext_groups[ext] = []
            ext_groups[ext].append(item)

    for ext, files in ext_groups.items():
        num = start_num
        for file in files:
            new_name = f"{prefix}_{num}{ext}"
            new_file_path = os.path.join(os.path.dirname(file), new_name)
            try:
                os.rename(file, new_file_path)
                print(f"Renamed {file} to {new_file_path}")
                num += 1
            except FileNotFoundError:
                messagebox.showerror("错误", f"文件 {file} 未找到！")
            except PermissionError:
                messagebox.showerror("错误", f"没有权限修改文件 {file}！")
            except Exception as e:
                messagebox.showerror("错误", f"发生了一个未知错误: {e}")

    messagebox.showinfo("成功", "文件名重命名完成！")
    open_folder(entry_directory.get())
    list_files(entry_directory.get())


def open_folder(folder_path):
    if os.path.exists(folder_path):
        webbrowser.open(f'file:///{folder_path}')


def select_all():
    all_items = tree.get_children()
    tree.selection_set(all_items)


def invert_selection():
    all_items = set(tree.get_children())
    selected = set(tree.selection())
    non_selected = all_items - selected
    non_selected_list = list(non_selected)
    tree.selection_set(non_selected_list)


def clear_selection():
    tree.selection_set()


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
path_label = tk.Label(frame_function, text="", wraplength=700, anchor=tk.W, font=("微软雅黑", 9, "italic"),
                      fg="#808080")
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

columns = ("序号", "扩展名", "文件名")
# 创建 Treeview 时使用 style
style = ttk.Style()
style.configure("Custom.Treeview.Heading", background="#e0e0e0", foreground="black", font=("微软雅黑", 11))
style.configure("Custom.Treeview", font=("微软雅黑", 10), rowheight=int(10 * 1.8))

tree = ttk.Treeview(frame_tree, columns=columns, show="headings", selectmode="extended", style="Custom.Treeview")

for col in columns:
    tree.heading(col, text=col)
    if col == "序号":
        tree.column(col, width=50, anchor=tk.CENTER)
    elif col == "扩展名":
        tree.column(col, width=100, anchor=tk.CENTER)
    else:
        tree.column(col, width=150)

tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
frame_tree.rowconfigure(0, weight=1)
frame_tree.columnconfigure(0, weight=1)

# 选择操作按钮区
frame_selection_buttons = ttk.Frame(root, padding="10")
frame_selection_buttons.grid(row=2, column=0, sticky=(tk.W, tk.E))
button_select_all = ttk.Button(frame_selection_buttons, text="全选", command=select_all)
button_select_all.pack(side=tk.LEFT, padx=5)
button_invert_selection = ttk.Button(frame_selection_buttons, text="反选", command=invert_selection)
button_invert_selection.pack(side=tk.LEFT, padx=5)
button_clear_selection = ttk.Button(frame_selection_buttons, text="清空", command=clear_selection)
button_clear_selection.pack(side=tk.LEFT, padx=5)

# 批量操作按钮区
frame_buttons = ttk.Frame(root, padding="20")
frame_buttons.grid(row=3, column=0, pady=10, sticky=tk.S)
button_change_extension = ttk.Button(frame_buttons, text="批量修改扩展名", command=batch_change_extension)
button_change_extension.pack(side=tk.LEFT, padx=5)
button_rename_file_names = ttk.Button(frame_buttons, text="批量修改文件名", command=batch_rename_file_names)
button_rename_file_names.pack(side=tk.LEFT, padx=5)

all_files_data = []
selected_items = []

# 运行主循环
root.mainloop()
