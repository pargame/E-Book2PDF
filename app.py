import customtkinter as ctk
import pyautogui
import threading
import time
import os
import sys
import subprocess
from PIL import Image

class CoordinateSelector(ctk.CTkToplevel):
    """화면 전체를 덮는 투명 창을 만들어 좌표를 선택하게 하는 클래스"""
    def __init__(self, master, callback):
        super().__init__(master)
        self.callback = callback

        # 윈도우 설정
        self.attributes('-fullscreen', True)
        self.attributes('-alpha', 0.1)
        self.deiconify()
        self.lift()
        self.focus_force()

        # 커서 모양 변경
        self.configure(cursor="crosshair")

        # 마우스 클릭 이벤트 바인딩
        self.bind("<Button-1>", self.on_click)
        self.bind("<Escape>", lambda e: self.destroy())

    def on_click(self, event):
        """마우스 클릭 시 좌표를 캡처하고 창을 닫습니다."""
        x, y = event.x_root, event.y_root
        self.destroy()
        self.callback((x, y))

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("E-Book to PDF")
        self.geometry("500x450")
        self.resizable(False, False)

        # --- 상수 정의 ---
        self.IMAGE_FOLDER = "screenshots"
        self.PDF_FOLDER = "PDFs"
        # ----------------

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # 설정값을 저장할 변수
        self.top_left_coord = None
        self.bottom_right_coord = None
        self.page_turn_key = None
        self.page_turn_coord = None

        container = ctk.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, MainPage, CoordsPage, KeyPressPage): # PermissionsPage 제거
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage) # 앱 시작 시 바로 StartPage 표시

        # 상태바
        self.status_bar = ctk.CTkLabel(self, text="준비", anchor="w")
        self.status_bar.pack(side="bottom", fill="x", padx=5, pady=2)
        
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def open_coord_selector(self, callback):
        """좌표 선택기를 엽니다."""
        selector = CoordinateSelector(self, callback)

    def start_screenshot_task(self, settings):
        """작업자 스레드를 시작하고 UI를 비활성화합니다."""
        self.frames[MainPage].set_ui_state("disabled")
        worker = ScreenshotWorker(self, settings) # app 인스턴스를 직접 전달
        worker.start()

    def update_status(self, message):
        """스레드로부터 메시지를 받아 상태바를 업데이트합니다."""
        self.status_bar.configure(text=message)

    def on_task_done(self):
        """작업 완료 시 UI를 다시 활성화합니다."""
        self.frames[MainPage].set_ui_state("normal")

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
        self.controller = controller
        label = ctk.CTkLabel(self, text="메인 설정", font=ctk.CTkFont(size=18, weight="bold"))
        label.pack(pady=20, padx=10)

        # 스크린샷 범위 설정
        self.coords_button = ctk.CTkButton(self, text="스크린샷 범위 설정", command=lambda: self.controller.show_frame(CoordsPage))
        self.coords_button.pack(pady=10)

        # 페이지 수 입력
        page_frame = ctk.CTkFrame(self)
        page_frame.pack(pady=10)
        ctk.CTkLabel(page_frame, text="페이지 수:").pack(side="left", padx=5)
        self.page_entry = ctk.CTkEntry(page_frame, width=100)
        self.page_entry.pack(side="left")

        # 페이지 넘김 방식
        page_turn_frame = ctk.CTkFrame(self)
        page_turn_frame.pack(pady=10)
        self.page_turn_method_var = ctk.StringVar(value="key")
        
        self.key_radio = ctk.CTkRadioButton(page_turn_frame, text="키보드", variable=self.page_turn_method_var, value="key", command=self.on_turn_method_change)
        self.key_radio.pack(side="left", padx=5)
        self.click_radio = ctk.CTkRadioButton(page_turn_frame, text="마우스 클릭", variable=self.page_turn_method_var, value="click", command=self.on_turn_method_change)
        self.click_radio.pack(side="left", padx=5)
        
        self.set_click_pos_button = ctk.CTkButton(page_turn_frame, text="클릭 위치 설정", command=self.set_click_position)
        self.click_pos_label = ctk.CTkLabel(page_turn_frame, text="")
        
        # 초기 상태 설정
        self.set_click_pos_button.pack_forget()
        self.click_pos_label.pack_forget()

        # 스크린샷 딜레이
        delay_frame = ctk.CTkFrame(self)
        delay_frame.pack(pady=10)
        ctk.CTkLabel(delay_frame, text="스크린샷 딜레이(초):").pack(side="left", padx=5)
        self.delay_entry = ctk.CTkEntry(delay_frame, width=100)
        self.delay_entry.insert(0, "1.5")
        self.delay_entry.pack(side="left")

        # 프로그램 시작 버튼
        self.start_button = ctk.CTkButton(self, text="프로그램 시작", width=200, height=40, command=self.start_process)
        self.start_button.pack(pady=40)

        # UI 요소들을 리스트로 관리 (상태 변경을 위해)
        self.ui_elements = [self.coords_button, self.page_entry, self.delay_entry, 
                            self.key_radio, self.click_radio, self.set_click_pos_button, self.start_button]

    def set_ui_state(self, state):
        """모든 UI 요소의 상태를 변경합니다."""
        for element in self.ui_elements:
            element.configure(state=state)

    def start_process(self):
        """설정값을 검증하고 스크린샷 작업을 시작합니다."""
        try:
            total_pages = int(self.page_entry.get())
            delay = float(self.delay_entry.get())
        except ValueError:
            self.controller.update_status("오류: 페이지 수와 딜레이는 숫자여야 합니다.")
            return

        if not self.controller.top_left_coord or not self.controller.bottom_right_coord:
            self.controller.update_status("오류: 스크린샷 범위가 설정되지 않았습니다.")
            return
        
        width = self.controller.bottom_right_coord[0] - self.controller.top_left_coord[0]
        height = self.controller.bottom_right_coord[1] - self.controller.top_left_coord[1]
        if width <= 0 or height <= 0:
            self.controller.update_status("오류: 잘못된 캡처 영역입니다.")
            return

        turn_method = self.page_turn_method_var.get()
        turn_details = None
        if turn_method == 'key':
            turn_details = self.controller.page_turn_key
            if not turn_details:
                self.controller.update_status("오류: 페이지 넘김 키가 설정되지 않았습니다.")
                return
        else: # click
            turn_details = self.controller.page_turn_coord
            if not turn_details:
                self.controller.update_status("오류: 페이지 넘김 클릭 위치가 설정되지 않았습니다.")
                return

        settings = {
            'total_pages': total_pages,
            'delay': delay,
            'region': (self.controller.top_left_coord[0], self.controller.top_left_coord[1], width, height),
            'turn_method': turn_method,
            'turn_details': turn_details,
            'pdf_name': f"output_{int(time.time())}"
        }
        
        self.controller.start_screenshot_task(settings)

    def on_turn_method_change(self):
        """페이지 넘김 방식 라디오 버튼 선택 시 UI를 업데이트합니다."""
        if self.page_turn_method_var.get() == "click":
            self.set_click_pos_button.pack(side="left", padx=5)
            self.click_pos_label.pack(side="left", padx=5)
        else: # key
            self.set_click_pos_button.pack_forget()
            self.click_pos_label.pack_forget()
            self.controller.show_frame(KeyPressPage)

    def set_click_position(self):
        """클릭 위치 좌표 선택기를 엽니다."""
        self.controller.open_coord_selector(self.update_click_position)

    def update_click_position(self, coords):
        """선택된 클릭 좌표를 저장하고 레이블을 업데이트합니다."""
        self.controller.page_turn_coord = coords
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
        
        self.bind("<Map>", self.start_listening)
        self.bind("<Unmap>", self.stop_listening)

        label = ctk.CTkLabel(self, text="페이지를 넘기는 데 사용할 키를 누르세요...", font=ctk.CTkFont(size=18))
        label.pack(pady=40, padx=10)
        
        self.key_label = ctk.CTkLabel(self, text="(입력 대기 중)", font=ctk.CTkFont(size=24, weight="bold"))
        self.key_label.pack(pady=20)

    def start_listening(self, event):
        """키 입력 감지를 시작합니다."""
        self.controller.bind("<KeyPress>", self.on_key_press)
        self.key_label.configure(text="(입력 대기 중)")
        self.focus_set()

    def stop_listening(self, event):
        """키 입력 감지를 중지합니다."""
        self.controller.unbind("<KeyPress>")

    def on_key_press(self, event):
        """키가 눌렸을 때 호출됩니다."""
        key_name = event.keysym
        self.controller.page_turn_key = key_name
        self.key_label.configure(text=f"선택된 키: '{key_name}'")
        
        self.controller.after(500, lambda: self.controller.show_frame(MainPage))

class ScreenshotWorker(threading.Thread):
    def __init__(self, app, settings):
        super().__init__()
        self.app = app
        self.settings = settings
        self.daemon = True

    def run(self):
        try:
            # 폴더 생성
            if not os.path.exists(self.app.IMAGE_FOLDER):
                os.makedirs(self.app.IMAGE_FOLDER)

            # 스크린샷 루프
            for i in range(self.settings['total_pages']):
                page_num = i + 1
                self.app.update_status(f"{page_num}/{self.settings['total_pages']} 페이지 캡처 중...")
                
                file_name = f"{self.app.IMAGE_FOLDER}/page_{page_num:03d}.png"
                pyautogui.screenshot(file_name, region=self.settings['region'])

                # 페이지 넘김
                if self.settings['turn_method'] == 'click':
                    pyautogui.click(self.settings['turn_details'])
                else: # key
                    pyautogui.press(self.settings['turn_details'])
                
                time.sleep(self.settings['delay'])
            
            self.app.update_status("PDF 변환 중...")
            self.convert_to_pdf()
            self.app.update_status("작업 완료! 'PDFs' 폴더를 확인하세요.")

        except pyautogui.PyAutoGUIException as e:
            self.app.update_status(f"화면 제어 오류: {e}")
        except FileNotFoundError as e:
            self.app.update_status(f"파일 시스템 오류: {e}")
        except Exception as e:
            self.app.update_status(f"알 수 없는 오류 발생: {e}")
        finally:
            # 작업 완료 후 UI 활성화를 메인 스레드에서 실행
            self.app.after(0, self.app.on_task_done)

    def convert_to_pdf(self):
        image_files = sorted([f for f in os.listdir(self.app.IMAGE_FOLDER) if f.endswith(".png")])
        if not image_files:
            self.app.update_status("캡처된 이미지가 없어 PDF를 생성할 수 없습니다.")
            return

        # PDF 폴더 생성
        if not os.path.exists(self.app.PDF_FOLDER):
            os.makedirs(self.app.PDF_FOLDER)
        
        pdf_path = os.path.join(self.app.PDF_FOLDER, f"{self.settings['pdf_name']}.pdf")
        
        image_paths = [os.path.join(self.app.IMAGE_FOLDER, f) for f in image_files]

        try:
            # 이미지들을 PDF로 변환
            pil_images = [Image.open(p).convert('RGB') for p in image_paths]
            if pil_images:
                pil_images[0].save(
                    pdf_path, "PDF", resolution=100.0, save_all=True, append_images=pil_images[1:]
                )
        except Exception as e:
            self.app.update_status(f"PDF 변환 오류: {e}")
        finally:
            # 임시 이미지 파일 삭제
            for p in image_paths:
                try:
                    os.remove(p)
                except OSError as e:
                    self.app.update_status(f"이미지 파일 삭제 오류: {e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()