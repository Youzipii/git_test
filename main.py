import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class VideoMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("视频合并工具")
        self.root.geometry("500x400")

        self.setup_ui()

    def setup_ui(self):
        # Mode selection
        tk.Label(self.root, text="选择工作模式:").pack(pady=5)
        self.mode_var = tk.StringVar(value="1")
        tk.Radiobutton(self.root, text="单目录合并", variable=self.mode_var, value="1").pack()
        tk.Radiobutton(self.root, text="多目录合并", variable=self.mode_var, value="2").pack()

        # Source directory
        tk.Label(self.root, text="源目录:").pack(pady=5)
        self.source_frame = tk.Frame(self.root)
        self.source_frame.pack(fill=tk.X, padx=10)
        self.source_entry = tk.Entry(self.source_frame)
        self.source_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(self.source_frame, text="浏览...", command=self.browse_source).pack(side=tk.RIGHT)

        # Output directory
        tk.Label(self.root, text="输出目录:").pack(pady=5)
        self.output_frame = tk.Frame(self.root)
        self.output_frame.pack(fill=tk.X, padx=10)
        self.output_entry = tk.Entry(self.output_frame)
        self.output_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(self.output_frame, text="浏览...", command=self.browse_output).pack(side=tk.RIGHT)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, padx=10, pady=10)

        # Log area
        tk.Label(self.root, text="操作日志:").pack()
        self.log_text = tk.Text(self.root, height=8, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Action buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="开始合并", command=self.start_merging).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="退出", command=self.root.quit).pack(side=tk.RIGHT, padx=5)

    def browse_source(self):
        directory = filedialog.askdirectory()
        if directory:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, directory)

    def browse_output(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, directory)

    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def get_filelist(self, directory):
        """Return a list of numeric-named files and create a filelist.txt for FFmpeg."""
        os.chdir(directory)
        all_files = os.listdir()
        files = [file for file in all_files if file.split('.')[0].isdigit()]
        files.sort(key=lambda x: int(x.split('.')[0]))

        with open("filelist.txt", "w", encoding="utf-8") as f:
            for file in files:
                f.write(f"file '{file}'\n")

        return files

    def combine_files(self, input_dir, output_path):
        """Combine files listed in filelist.txt into a single video."""
        os.chdir(input_dir)
        command = f'ffmpeg -f concat -safe 0 -i filelist.txt -c copy "{output_path}"'
        self.log_message(f"执行命令: {command}")
        return os.system(command)

    def start_merging(self):
        mode = self.mode_var.get()
        source_dir = self.source_entry.get()
        output_dir = self.output_entry.get()

        if not source_dir or not output_dir:
            messagebox.showerror("错误", "请选择源目录和输出目录")
            return

        try:
            if mode == "1":
                # Single directory mode
                dir_name = os.path.basename(source_dir)
                output_path = os.path.join(output_dir, f"{dir_name}.mp4")

                self.log_message(f"开始处理目录: {source_dir}")
                files = self.get_filelist(source_dir)
                if not files:
                    messagebox.showwarning("警告", "没有找到可合并的文件")
                    return

                self.progress["value"] = 50
                self.root.update_idletasks()

                result = self.combine_files(source_dir, output_path)
                if result == 0:
                    self.log_message(f"成功合并到: {output_path}")
                    messagebox.showinfo("成功", "文件合并完成！")
                else:
                    self.log_message("合并失败，请检查FFmpeg是否安装正确")
                    messagebox.showerror("错误", "合并失败")

                self.progress["value"] = 100

            elif mode == "2":
                # Multiple directories mode
                total_dirs = sum(os.path.isdir(os.path.join(source_dir, d)) for d in os.listdir(source_dir))
                processed = 0

                for dir_name in os.listdir(source_dir):
                    dir_path = os.path.join(source_dir, dir_name)
                    if os.path.isdir(dir_path):
                        self.log_message(f"处理目录: {dir_name}")
                        files = self.get_filelist(dir_path)

                        if files:
                            output_path = os.path.join(output_dir, f"{dir_name}.mp4")
                            result = self.combine_files(dir_path, output_path)
                            if result == 0:
                                self.log_message(f"成功合并到: {output_path}")
                            else:
                                self.log_message(f"{dir_name} 合并失败")

                        processed += 1
                        progress = (processed / total_dirs) * 100
                        self.progress["value"] = progress
                        self.root.update_idletasks()

                messagebox.showinfo("完成", f"已完成 {processed} 个目录的合并")
                self.progress["value"] = 100

        except Exception as e:
            self.log_message(f"发生错误: {str(e)}")
            messagebox.showerror("错误", f"处理过程中发生错误:\n{str(e)}")
            self.progress["value"] = 0


def main():
    root = tk.Tk()
    app = VideoMergerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
