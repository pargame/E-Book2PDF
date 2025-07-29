import customtkinter as ctk
import pyautogui

class CoordinateSelector(ctk.CTkToplevel):
    """화면 전체를 덮는 투명 창을 만들어 좌표를 선택하게 하는 클래스"""
    def __init__(self, master, callback):
        super().__init__(master)
        self.callback = callback

        # 윈도우 설정
        self.attributes('-fullscreen', True)  # 전체 화면
        self.attributes('-alpha', 0.1)       # 투명도 (0.0 ~ 1.0)
        self.deiconify()                      # 창을 즉시 표시
        self.lift()                           # 다른 모든 창 위로 올림
        self.focus_force()                    # 포커스 강제
        self.grab_set()                       # 모든 이벤트를 이 창으로 한정

        # 커서 모양 변경
        self.configure(cursor="crosshair")

        # 마우스 클릭 이벤트 바인딩
        self.bind("<Button-1>", self.on_click)
        self.bind("<Escape>", lambda e: self.destroy()) # ESC로 취소

    def on_click(self, event):
        """마우스 클릭 시 좌표를 캡처하고 창을 닫습니다."""
        x, y = pyautogui.position()
        self.destroy()
        self.callback((x, y))

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("E-Book to PDF")
        self.geometry("500x450")
        self.resizable(False, False)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # 설정값을 저장할 변수
        self.top_left_coord = None
        self.bottom_right_coord = None
        self.page_turn_key = None

        container = ctk.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, MainPage, CoordsPage, KeyPressPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def open_coord_selector(self, callback):
        """좌표 선택기를 엽니다."""
        selector = CoordinateSelector(self, callback)

class StartPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = ctk.CTkLabel(self, text="E-Book to PDF", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=40)
        dev_label = ctk.CTkLabel(self, text="Developed by pargamer & Gemini", font=ctk.CTkFont(size=14))
        dev_label.pack(pady=10)
        copyright_label = ctk.CTkLabel(self, text="© 2025. pargamer. All rights reserved.", font=ctk.CTkFont(size=12))
        copyright_label.pack(pady=5)
        start_button = ctk.CTkButton(self, text="시작", width=200, height=40, command=lambda: controller.show_frame(MainPage))
        start_button.pack(pady=60)

class MainPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = ctk.CTkLabel(self, text="메인 설정", font=ctk.CTkFont(size=18, weight="bold"))
        label.pack(pady=20, padx=10)

        # 스크린샷 범위 설정
        coords_button = ctk.CTkButton(self, text="스크린샷 범위 설정", command=lambda: controller.show_frame(CoordsPage))
        coords_button.pack(pady=10)

        # 페이지 수 입력
        page_frame = ctk.CTkFrame(self)
        page_frame.pack(pady=10)
        ctk.CTkLabel(page_frame, text="페이지 수:").pack(side="left", padx=5)
        self.page_entry = ctk.CTkEntry(page_frame, width=100)
        self.page_entry.pack(side="left")

        # 페이지 넘김 방식
        self.page_turn_method_var = ctk.StringVar(value="key")
        
        key_radio = ctk.CTkRadioButton(page_turn_frame, text="키보드", variable=self.page_turn_method_var, value="key", command=self.on_turn_method_change)
        key_radio.pack(side="left", padx=5)
        click_radio = ctk.CTkRadioButton(page_turn_frame, text="마우스 클릭", variable=self.page_turn_method_var, value="click", command=self.on_turn_method_change)
        click_radio.pack(side="left", padx=5)
        
        self.set_click_pos_button = ctk.CTkButton(page_turn_frame, text="클릭 위치 설정", command=self.set_click_position)
        self.click_pos_label = ctk.CTkLabel(page_turn_frame, text="")
        
        # 초기 상태 업데이트
        self.on_turn_method_change()

        # 스크린샷 딜레이
        delay_frame = ctk.CTkFrame(self)
        delay_frame.pack(pady=10)
        ctk.CTkLabel(delay_frame, text="스크린샷 딜레이(초):").pack(side="left", padx=5)
        self.delay_entry = ctk.CTkEntry(delay_frame, width=100)
        self.delay_entry.insert(0, "1.5")
        self.delay_entry.pack(side="left")

        # 프로그램 시작 버튼
        start_button = ctk.CTkButton(self, text="프로그램 시작", width=200, height=40)
        start_button.pack(pady=40)

    def on_turn_method_change(self):
        """페이지 넘김 방식 라디오 버튼 선택 시 UI를 업데이트합니다."""
        if self.turn_method_var.get() == "click":
            self.set_click_pos_button.pack(side="left", padx=5)
            self.click_pos_label.pack(side="left", padx=5)
            # 키보드 선택 페이지로 넘어가는 동작 방지
            self.master.master.frames[KeyPressPage].stop_listening(None)
        else: # key
            self.set_click_pos_button.pack_forget()
            self.click_pos_label.pack_forget()
            # 키보드 선택 시 해당 설정 페이지로 이동
            self.master.master.show_frame(KeyPressPage)

    def set_click_position(self):
        """클릭 위치 좌표 선택기를 엽니다."""
        self.master.master.open_coord_selector(self.update_click_position)

    def update_click_position(self, coords):
        """선택된 클릭 좌표를 저장하고 레이블을 업데이트합니다."""
        self.master.master.page_turn_coord = coords
        self.click_pos_label.configure(text=f"위치: {coords}")

class CoordsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = ctk.CTkLabel(self, text="스크린샷 범위 설정", font=ctk.CTkFont(size=18, weight="bold"))
        label.pack(pady=20, padx=10)

        top_left_button = ctk.CTkButton(self, text="왼쪽 상단 좌표 설정", command=self.set_top_left)
        top_left_button.pack(pady=10)
        self.top_left_label = ctk.CTkLabel(self, text="좌표: (미설정)")
        self.top_left_label.pack()

        bottom_right_button = ctk.CTkButton(self, text="오른쪽 하단 좌표 설정", command=self.set_bottom_right)
        bottom_right_button.pack(pady=10)
        self.bottom_right_label = ctk.CTkLabel(self, text="좌표: (미설정)")
        self.bottom_right_label.pack()

        done_button = ctk.CTkButton(self, text="완료", command=lambda: controller.show_frame(MainPage))
        done_button.pack(pady=40)

    def set_top_left(self):
        self.controller.open_coord_selector(self.update_top_left)

    def update_top_left(self, coords):
        self.controller.top_left_coord = coords
        self.top_left_label.configure(text=f"좌표: {coords}")

    def set_bottom_right(self):
        self.controller.open_coord_selector(self.update_bottom_right)

    def update_bottom_right(self, coords):
        self.controller.bottom_right_coord = coords
        self.bottom_right_label.configure(text=f"좌표: {coords}")

class KeyPressPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 이 프레임이 화면에 표시될 때 키 입력을 받도록 설정
        self.bind("<Map>", self.start_listening)
        # 다른 프레임으로 전환될 때 리스너 중지
        self.bind("<Unmap>", self.stop_listening)

        label = ctk.CTkLabel(self, text="페이지를 넘기는 데 사용할 키를 누르세요...", font=ctk.CTkFont(size=18))
        label.pack(pady=40, padx=10)
        
        self.key_label = ctk.CTkLabel(self, text="(입력 대기 중)", font=ctk.CTkFont(size=24, weight="bold"))
        self.key_label.pack(pady=20)

    def start_listening(self, event):
        """키 입력 감지를 시작합니다."""
        self.controller.bind("<KeyPress>", self.on_key_press)
        self.key_label.configure(text="(입력 대기 중)")

    def stop_listening(self, event):
        """키 입력 감지를 중지합니다."""
        self.controller.unbind("<KeyPress>")

    def on_key_press(self, event):
        """키가 눌렸을 때 호출됩니다."""
        # keysym을 사용하여 'Right', 'space' 같은 특수키 이름도 얻음
        key_name = event.keysym
        self.controller.page_turn_key = key_name
        self.key_label.configure(text=f"선택된 키: '{key_name}'")
        
        # 키 선택 후 0.5초 뒤에 메인 화면으로 자동 복귀
        self.controller.after(500, lambda: self.controller.show_frame(MainPage))


if __name__ == "__main__":
    app = App()
    app.mainloop()