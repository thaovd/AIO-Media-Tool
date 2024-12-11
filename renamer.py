import os
from tkinter import Tk, Frame, Label, Entry, Button, ttk, StringVar, filedialog, messagebox

class FileRenamerGUI(Frame):
    def __init__(self, master, parent):
        super().__init__(master)
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        # Directory selection
        directory_label = Label(self, text="Chọn thư mục cần đổi tên file:")
        directory_label.pack(pady=10)

        directory_button = Button(self, text="Tìm thư mục", command=self.select_directory)
        directory_button.pack(pady=5)

        self.directory_entry = Entry(self, width=40, state="readonly")
        self.directory_entry.pack(pady=5)

        # Character modification
        character_label = Label(self, text="Nhập ký tự cần sửa đổi:")
        character_label.pack(pady=10)

        self.character_entry = Entry(self)
        self.character_entry.pack(pady=5)

        # Modify mode selection
        modify_mode_label = Label(self, text="Lựa chọn chế độ sửa đổi:")
        modify_mode_label.pack(pady=10)

        self.modify_mode = StringVar(value="Thêm vào đầu tên file")
        self.modify_mode_dropdown = ttk.Combobox(self, textvariable=self.modify_mode, values=["Thêm vào đầu tên file", "Thêm vào cuối tên file", "Xoá ký tự trong tên file"], state="readonly")
        self.modify_mode_dropdown.pack(pady=10)
        self.modify_mode_dropdown.current(0)

        # Process button
        process_button = Button(self, text="Chạy", command=self.process_files)
        process_button.pack(pady=10)

    def select_directory(self):
        self.directory_path = filedialog.askdirectory()
        self.directory_entry.config(state="normal")
        self.directory_entry.delete(0, "end")
        self.directory_entry.insert(0, self.directory_path)
        self.directory_entry.config(state="readonly")

    def process_files(self):
        self.character_to_modify = self.character_entry.get()
        modify_mode = self.modify_mode.get()
        if modify_mode == "Thêm vào đầu tên file":
            add_character_to_beginning(self.directory_path, self.character_to_modify)
        elif modify_mode == "Thêm vào cuối tên file":
            add_character_to_end(self.directory_path, self.character_to_modify)
        elif modify_mode == "Xoá ký tự trong tên file":
            delete_character_from_filename(self.directory_path, self.character_to_modify)
        else:
            print(f"Chưa chọn chế độ chỉnh sửa: {modify_mode}")
        messagebox.showinfo("Tệp đã được đổi tên", "Hoàn thành quá trình đổi tên tệp.")
        self.parent.update_status_bar("Hoàn thành quá trình đổi tên tệp.")

def add_character_to_beginning(directory, character_to_add):
    for filename in os.listdir(directory):
        base, ext = os.path.splitext(filename)
        new_filename = character_to_add + base + ext
        os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))

def add_character_to_end(directory, character_to_add):
    for filename in os.listdir(directory):
        base, ext = os.path.splitext(filename)
        new_filename = base + character_to_add + ext
        os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))

def delete_character_from_filename(directory, character_to_delete):
    for filename in os.listdir(directory):
        base, ext = os.path.splitext(filename)
        new_filename = base.replace(character_to_delete, "") + ext
        os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
