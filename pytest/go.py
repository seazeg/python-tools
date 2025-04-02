import tkinter as tk
from tkinter import messagebox

class SimpleGUI:
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("简单GUI示例")
        self.root.geometry("300x200")

        # 创建标签
        self.label = tk.Label(self.root, text="欢迎使用GUI程序!", font=("Arial", 12))
        self.label.pack(pady=20)

        # 创建按钮
        self.button = tk.Button(self.root, text="点击我", command=self.show_message)
        self.button.pack(pady=10)

        # 创建输入框
        self.entry = tk.Entry(self.root)
        self.entry.pack(pady=10)

    def show_message(self):
        # 获取输入框的内容
        text = self.entry.get()
        if text:
            messagebox.showinfo("消息", f"你输入的内容是: {text}")
        else:
            messagebox.showinfo("消息", "你好！这是一个消息框。")

    def run(self):
        # 运行主循环
        self.root.mainloop()

if __name__ == "__main__":
    app = SimpleGUI()
    app.run()
