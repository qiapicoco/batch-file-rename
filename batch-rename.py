import os


def batch_rename_files(directory, old_extension, new_extension, prefix=""):
    try:
        for filename in os.listdir(directory):
            if filename.endswith(old_extension):
                base_name = os.path.splitext(filename)[0]
                new_filename = f"{prefix}{base_name}{new_extension}"
                old_file_path = os.path.join(directory, filename)
                new_file_path = os.path.join(directory, new_filename)
                os.rename(old_file_path, new_file_path)
                print(f"Renamed {old_file_path} to {new_file_path}")
    except FileNotFoundError:
        print(f"错误: 目录 {directory} 未找到!")
    except PermissionError:
        print(f"错误: 没有权限修改目录 {directory} 中的文件!")
    except Exception as e:
        print(f"错误: 发生了一个未知错误: {e}")


if __name__ == "__main__":
    directory = '.'  # 要修改的文件所在的目录，这里是当前目录
    old_extension = '.txt'  # 要修改的旧扩展名
    new_extension = '.csv'  # 要修改成的新扩展名
    prefix = "new_"  # 可选的文件名前缀
    batch_rename_files(directory, old_extension, new_extension, prefix)
