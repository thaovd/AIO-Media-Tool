import tkinter as tk
from tkinter import filedialog, ttk
import os
import os.path

class BatchFileRenamer:
    def __init__(self, master):
        self.master = master

        # Create the main frame
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(padx=20, pady=20)

        # Create the input frame
        self.input_frame = tk.Frame(self.main_frame)
        self.input_frame.pack(pady=10)

        # Create the input label and entry
        self.input_label = tk.Label(self.input_frame, text="Chọn thư mục:")
        self.input_label.pack(side=tk.LEFT)
        self.input_entry = tk.Entry(self.input_frame, width=40)
        self.input_entry.pack(side=tk.LEFT)
        self.input_button = tk.Button(self.input_frame, text="🔎 Tìm", command=self.select_directory)
        self.input_button.pack(side=tk.LEFT, padx=10)

        # Create the operation frame
        self.operation_frame = tk.Frame(self.main_frame)
        self.operation_frame.pack(pady=10)

        # Create the mode selection label and combobox
        self.mode_label = tk.Label(self.operation_frame, text="Chế độ:")
        self.mode_label.pack(side=tk.LEFT)
        self.mode_combobox = ttk.Combobox(self.operation_frame, width=25, state="readonly")
        self.mode_combobox["values"] = ("Xoá ký tự trong tên", "Thêm vào đầu tên", "Thêm vào cuối tên")
        self.mode_combobox.current(0)
        self.mode_combobox.pack(side=tk.LEFT, padx=10)

        # Create the character entry label and entry
        self.char_label = tk.Label(self.operation_frame, text="Ký tự yêu cầu:")
        self.char_label.pack(side=tk.LEFT)
        self.char_entry = tk.Entry(self.operation_frame, width=20)
        self.char_entry.pack(side=tk.LEFT, padx=10)
        self.char_entry.bind("<KeyRelease>", self.update_preview)  # Bind the KeyRelease event to the update_preview method

        # Create the rename button
        self.rename_button = tk.Button(self.main_frame, text="🚀 Chạy", command=self.rename_files)
        self.rename_button.pack(pady=10)

        # Create the preview frame
        self.preview_frame = tk.Frame(self.main_frame)
        self.preview_frame.pack(pady=10)

        # Create the preview label and listbox
        self.preview_label = tk.Label(self.preview_frame, text="Xem trước:")
        self.preview_label.pack(side=tk.LEFT)
        self.preview_listbox = tk.Listbox(self.preview_frame, width=50, height=20)
        self.preview_listbox.pack(side=tk.LEFT, padx=10)

        # Create the preview scrollbar
        self.preview_scrollbar = tk.Scrollbar(self.preview_frame, command=self.preview_listbox.yview)
        self.preview_scrollbar.pack(side=tk.LEFT, fill=tk.BOTH)
        self.preview_listbox.config(yscrollcommand=self.preview_scrollbar.set)

    def select_directory(self):
        directory = filedialog.askdirectory()
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, directory)
        self.update_preview()

    def update_preview(self, event=None):
        directory = self.input_entry.get()
        mode = self.mode_combobox.get()
        char = self.char_entry.get()

        self.preview_listbox.delete(0, tk.END)
        if os.path.isdir(directory):
            for filename in os.listdir(directory):
                if mode == "Xoá ký tự trong tên":
                    new_filename = filename.replace(char, "")
                elif mode == "Thêm vào đầu tên":
                    new_filename = char + filename
                else:  # "Thêm vào cuối tên"
                    base, ext = os.path.splitext(filename)
                    new_filename = base + char + ext
                self.preview_listbox.insert(tk.END, new_filename)

    def rename_files(self):
        directory = self.input_entry.get()
        mode = self.mode_combobox.get()
        char = self.char_entry.get()

        if not os.path.isdir(directory):
            tk.messagebox.showerror("Lỗi", "Vui lòng chọn folder cần đổi tên.")
            return

        for filename in os.listdir(directory):
            old_path = os.path.join(directory, filename)
            if mode == "Xoá ký tự trong tên":
                new_filename = filename.replace(char, "")
            elif mode == "Thêm vào đầu tên":
                new_filename = char + filename
            else:  # "Thêm vào cuối tên"
                base, ext = os.path.splitext(filename)
                new_filename = base + char + ext
            new_path = os.path.join(directory, new_filename)
            os.rename(old_path, new_path)

        self.update_preview()
        tk.messagebox.showinfo("Hoàn thành", "Tên file đã được đổi tên.")
