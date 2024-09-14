from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import pandas as pd 
import numpy as np
import cv2
from score import *




class toolCV:
    def __init__(self, root):
        self.root = root 
        self.root.title('Chấm điểm bài thi trắc nghiệm THPTQG tự động')
        self.root.geometry('800x1000')
        self.create_widget()
        self.image = None 
        self.res_image = None

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                self.image = cv2.imread(file_path)
                self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                self.clear_widgets()
                self.show_result()
            except:
                print('error')




    def create_widget(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=20, pady=20)
        self.title_label = tk.Label(self.main_frame, text="Upload Image", font=("Arial", 20, "bold"))
        self.title_label.pack(padx=80, pady=(400,0))

        self.button = tk.Button(self.main_frame, text='Upload', command=self.upload_image, font=("Arial", 14))
        self.button.pack(padx=130, pady=20)



    
    def clear_widgets(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()




    def show_result(self):
        self.sbd = sbd(self.image)
        self.made = made(self.image)
        self.score = score(self.image)[1]
        self.res_image = score(self.image)[0]
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import pandas as pd 
import numpy as np
import cv2
from score import *




class toolCV:
    def __init__(self, root):
        self.root = root 
        self.root.title('Chấm điểm bài thi trắc nghiệm THPTQG tự động')
        self.root.geometry('800x1000')
        self.create_widget()
        self.image = None 
        self.res_image = None

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                self.image = cv2.imread(file_path)
                self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                self.clear_widgets()
                self.show_result()
            except:
                print('error')




    def create_widget(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=20, pady=20)
        self.title_label = tk.Label(self.main_frame, text="Upload Image", font=("Arial", 20, "bold"))
        self.title_label.pack(padx=80, pady=(400,0))

        self.button = tk.Button(self.main_frame, text='Upload', command=self.upload_image, font=("Arial", 14))
        self.button.pack(padx=130, pady=20)



    
    def clear_widgets(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()




    def show_result(self):
        self.sbd = sbd(self.image)
        self.made = made(self.image)
        self.score = score(self.image)[1]
        self.res_image = score(self.image)[0]

         # Tạo một Label để hiển thị ảnh
        self.image_label = tk.Label(self.main_frame)
        self.image_label.pack()

        # Chuyển đổi ảnh từ OpenCV sang định dạng PIL
        pil_image = Image.fromarray(self.res_image)
        width, height = pil_image.size 
        scale_percent = 50  # Bạn có thể thay đổi giá trị phần trăm tại đây
        new_width = int(width * scale_percent / 100)
        new_height = int(height * scale_percent / 100)

        # Thay đổii kích thước ảnh dựa trên phần trăm
        pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Chuyển từ PIL image sang ImageTk để hiển thị trong tkinter
        tk_image = ImageTk.PhotoImage(pil_image)

        # Gắn ảnh vào Label
        self.image_label.config(image=tk_image)
        self.image_label.image = tk_image
        
        self.sbd_label1 = tk.Label(self.main_frame, text='Số báo danh: ', font=("Arial", 14))
        self.sbd_label2 = tk.Label(self.main_frame, text=self.sbd, font=("Arial", 14))
        self.sbd_label1.pack(padx=0, pady=10)
        self.sbd_label2.pack(padx=0, pady=10)

        
        self.made_label1 = tk.Label(self.main_frame, text='Mã đề: ', font=("Arial", 14))
        self.made_label2 = tk.Label(self.main_frame, text=self.made, font=("Arial", 14))
        self.made_label1.pack(padx=0, pady=10)
        self.made_label2.pack(padx=0, pady=10)


        
        self.score_label1 = tk.Label(self.main_frame, text='Điểm: ', font=("Arial", 14))
        self.score_label2 = tk.Label(self.main_frame, text=self.score, font=("Arial", 14))
        self.score_label1.pack(padx=200, pady=10)
        self.score_label2.pack(padx=0, pady=10)






if __name__ == '__main__':
    root = tk.Tk()
    app = toolCV(root)
    root.mainloop()
