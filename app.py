import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 윈도우 설정
        self.title("E-Book to PDF")
        self.geometry("500x400")
        self.resizable(False, False)

        # 테마 설정 (dark, light, system)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # 모든 화면 프레임을 담을 컨테이너
        container = ctk.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # 각 화면 프레임들을 여기에 추가
        for F in (StartPage,): # MainPage, CoordsPage, KeyPressPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        """지정된 프레임을 화면에 표시합니다."""
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        label = ctk.CTkLabel(self, text="E-Book to PDF", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=40)

        dev_label = ctk.CTkLabel(self, text="Developed by pargamer & Gemini", font=ctk.CTkFont(size=14))
        dev_label.pack(pady=10)
        
        copyright_label = ctk.CTkLabel(self, text="© 2025. pargamer. All rights reserved.", font=ctk.CTkFont(size=12))
        copyright_label.pack(pady=5)

        start_button = ctk.CTkButton(self, text="시작", width=200, height=40)
        start_button.pack(pady=60)

if __name__ == "__main__":
    app = App()
    app.mainloop()
