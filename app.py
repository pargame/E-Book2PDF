import customtkinter as ctk
import pyautogui
import threading
import time
import os
import sys
import subprocess
from PIL import Image


## 오버레이 방식 완전 제거

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("E-Book to PDF")
        self.geometry("500x450")
        self.resizable(False, False)

        # --- 해상도 스케일링 팩터 계산 (macOS Retina 대응) ---
        self.scale_factor = 1.0
        try:
            if sys.platform == "darwin":
                import re
                cmd = ["system_profiler", "SPDisplaysDataType"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                output = result.stdout
                physical_res_match = re.search(r"Resolution: (\d+) x \d+", output)
                logical_res_match = re.search(r"(?:UI Looks like|Looks like): (\d+) x \d+", output)
                if physical_res_match and logical_res_match:
                    physical_width = int(physical_res_match.group(1))
                    logical_width = int(logical_res_match.group(1))
                    if logical_width > 0:
                        self.scale_factor = physical_width / logical_width
        except Exception as e:
            print(f"macOS 스케일링 팩터 계산 실패: {e}")
            pass
        # -------------------------------------------------

        self.IMAGE_FOLDER = "screenshots"
        self.PDF_FOLDER = "PDFs"

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.top_left_coord = None
        self.bottom_right_coord = None
        self.page_turn_key = None
        self.page_turn_coord = None

        container = ctk.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, MainPage, CoordsPage, KeyPressPage):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

        self.status_bar = ctk.CTkLabel(self, text="준비", anchor="w")
        self.status_bar.pack(side="bottom", fill="x", padx=5, pady=2)

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        # *** 해결책 1: 이벤트 격리 ***
        # 페이지가 전환될 때 포커스를 명확히 설정하여, 이전 페이지의 이벤트 리스너가 동작하지 않도록 함
        frame.focus_set()
        frame.tkraise()

    def start_screenshot_task(self, settings):
        self.frames["MainPage"].set_ui_state("disabled")
        worker = ScreenshotWorker(self, settings)
        worker.start()

    def update_status(self, message):
        self.status_bar.configure(text=message)

    def on_task_done(self):
        self.frames["MainPage"].set_ui_state("normal")

class StartPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ctk.CTkLabel(self, text="E-Book to PDF", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=40)
        ctk.CTkLabel(self, text="Developed by pargamer & Gemini", font=ctk.CTkFont(size=14)).pack(pady=10)
        ctk.CTkLabel(self, text="© 2025. pargamer. All rights reserved.", font=ctk.CTkFont(size=12)).pack(pady=5)
        ctk.CTkButton(self, text="시작", width=200, height=40, command=lambda: controller.show_frame("MainPage")).pack(pady=60)

class MainPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text="메인 설정", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20, padx=10)

        self.coords_button = ctk.CTkButton(self, text="스크린샷 범위 설정", command=lambda: self.controller.show_frame("CoordsPage"))
        self.coords_button.pack(pady=10)

        page_frame = ctk.CTkFrame(self)
        page_frame.pack(pady=10)
        ctk.CTkLabel(page_frame, text="페이지 수:").pack(side="left", padx=5)
        self.page_entry = ctk.CTkEntry(page_frame, width=100)
        self.page_entry.pack(side="left")

        page_turn_frame = ctk.CTkFrame(self)
        page_turn_frame.pack(pady=10)
        self.page_turn_method_var = ctk.StringVar(value="key")
        self.key_radio = ctk.CTkRadioButton(page_turn_frame, text="키보드", variable=self.page_turn_method_var, value="key", command=self.on_turn_method_change)
        self.key_radio.pack(side="left", padx=5)
        self.set_key_button = ctk.CTkButton(page_turn_frame, text="키 설정", command=lambda: self.controller.show_frame("KeyPressPage"))
        self.key_label = ctk.CTkLabel(page_turn_frame, text="(미설정)")
        self.click_radio = ctk.CTkRadioButton(page_turn_frame, text="마우스 클릭", variable=self.page_turn_method_var, value="click", command=self.on_turn_method_change)
        self.click_radio.pack(side="left", padx=5)
        self.set_click_pos_button = ctk.CTkButton(page_turn_frame, text="클릭 위치 설정", command=self.set_click_position)
        self.click_pos_label = ctk.CTkLabel(page_turn_frame, text="")
        self.on_turn_method_change()

        delay_frame = ctk.CTkFrame(self)
        delay_frame.pack(pady=10)
        ctk.CTkLabel(delay_frame, text="스크린샷 딜레이(초):").pack(side="left", padx=5)
        self.delay_entry = ctk.CTkEntry(delay_frame, width=100)
        self.delay_entry.insert(0, "1.5")
        self.delay_entry.pack(side="left")

        self.start_button = ctk.CTkButton(self, text="프로그램 시작", width=200, height=40, command=self.start_process)
        self.start_button.pack(pady=40)

        self.ui_elements = [self.coords_button, self.page_entry, self.delay_entry, self.key_radio, self.click_radio, self.set_click_pos_button, self.set_key_button, self.start_button]

    def set_ui_state(self, state):
        for element in self.ui_elements:
            element.configure(state=state)

    def start_process(self):
        try:
            total_pages = int(self.page_entry.get())
            if total_pages <= 0: raise ValueError("페이지 수는 1 이상이어야 합니다.")
            delay = float(self.delay_entry.get())
            if not self.controller.top_left_coord or not self.controller.bottom_right_coord: raise ValueError("스크린샷 범위가 설정되지 않았습니다.")
            width = self.controller.bottom_right_coord[0] - self.controller.top_left_coord[0]
            height = self.controller.bottom_right_coord[1] - self.controller.top_left_coord[1]
            if width <= 0 or height <= 0: raise ValueError("잘못된 캡처 영역입니다.")
        except ValueError as e:
            self.controller.update_status(f"오류: {e}")
            return

        turn_method = self.page_turn_method_var.get()
        turn_details = self.controller.page_turn_key if turn_method == 'key' else self.controller.page_turn_coord
        if not turn_details:
            self.controller.update_status(f"오류: 페이지 넘김 {'키' if turn_method == 'key' else '클릭 위치'}가 설정되지 않았습니다.")
            return

        settings = {'total_pages': total_pages, 'delay': delay, 'region': (self.controller.top_left_coord[0], self.controller.top_left_coord[1], width, height), 'turn_method': turn_method, 'turn_details': turn_details, 'pdf_name': f"output_{int(time.time())}"}
        self.set_ui_state("disabled")
        self.start_countdown(5, settings)

    def start_countdown(self, count, settings):
        if count > 0:
            self.controller.update_status(f"작업을 {count}초 후에 시작합니다. 캡처할 창을 활성화하세요.")
            self.after(1000, lambda: self.start_countdown(count - 1, settings))
        else:
            self.controller.start_screenshot_task(settings)

    def on_turn_method_change(self):
        is_key_method = self.page_turn_method_var.get() == "key"
        self.set_key_button.pack(side="left", padx=5) if is_key_method else self.set_key_button.pack_forget()
        self.key_label.pack(side="left", padx=5) if is_key_method else self.key_label.pack_forget()
        self.set_click_pos_button.pack(side="left", padx=5) if not is_key_method else self.set_click_pos_button.pack_forget()
        self.click_pos_label.pack(side="left", padx=5) if not is_key_method else self.click_pos_label.pack_forget()
        key = self.controller.page_turn_key
        self.key_label.configure(text=f"({key})" if key else "(미설정)")

    def set_click_position(self):
        self._start_click_capture_countdown(5)

    def _start_click_capture_countdown(self, count):
        if count > 0:
            self.controller.update_status(f"{count}초 후 마우스 클릭 위치를 캡처합니다. 원하는 위치에 마우스를 올려두세요.")
            self.after(1000, lambda: self._start_click_capture_countdown(count - 1))
        else:
            self._capture_click_position()

    def _capture_click_position(self):
        try:
            x, y = pyautogui.position()
            self.controller.page_turn_coord = (x, y)
            self.click_pos_label.configure(text=f"위치: ({x}, {y})")
            self.controller.update_status("클릭 위치가 설정되었습니다.")
        except Exception as e:
            self.controller.update_status(f"마우스 위치 읽기 오류: {e}")

class PreviewWindow(ctk.CTkToplevel):
    def __init__(self, master, image):
        super().__init__(master)
        self.grab_set()
        self.title("미리보기")
        self.attributes("-topmost", True)
        ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
        max_width, max_height = self.master.winfo_screenwidth() * 0.8, self.master.winfo_screenheight() * 0.8
        img_width, img_height = image.size
        if img_width > max_width or img_height > max_height:
            ratio = min(max_width / img_width, max_height / img_height)
            ctk_image.configure(size=(int(img_width * ratio), int(img_height * ratio)))
        ctk.CTkLabel(self, image=ctk_image, text="").pack(pady=10, padx=10)
        ctk.CTkButton(self, text="닫기", command=self.destroy).pack(pady=10)

class CoordsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text="스크린샷 범위 설정", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10, padx=10)
        
        # 전체화면 좌표 입력 버튼 추가
        calibrate_frame = ctk.CTkFrame(self)
        calibrate_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(calibrate_frame, text="전체화면 좌표 입력", 
                     command=self.calibrate_screen_scale).pack(pady=5)
        self.scale_label = ctk.CTkLabel(calibrate_frame, text="현재 스케일: 1.0")
        self.scale_label.pack(pady=5)

        coords_frame = ctk.CTkFrame(self)
        coords_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(coords_frame, text="왼쪽 상단 (X, Y):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.top_x_entry = ctk.CTkEntry(coords_frame, width=70)
        self.top_x_entry.grid(row=0, column=1, padx=5, pady=5)
        self.top_y_entry = ctk.CTkEntry(coords_frame, width=70)
        self.top_y_entry.grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkButton(coords_frame, text="캡처", width=60, command=lambda: self.capture_mouse_position("top_left")).grid(row=0, column=3, padx=5, pady=5)
        ctk.CTkLabel(coords_frame, text="오른쪽 하단 (X, Y):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.bottom_x_entry = ctk.CTkEntry(coords_frame, width=70)
        self.bottom_x_entry.grid(row=1, column=1, padx=5, pady=5)
        self.bottom_y_entry = ctk.CTkEntry(coords_frame, width=70)
        self.bottom_y_entry.grid(row=1, column=2, padx=5, pady=5)
        ctk.CTkButton(coords_frame, text="캡처", width=60, command=lambda: self.capture_mouse_position("bottom_right")).grid(row=1, column=3, padx=5, pady=5)

        action_frame = ctk.CTkFrame(self)
        action_frame.pack(pady=10)
        ctk.CTkButton(action_frame, text="미리보기 확인", command=self.show_preview).pack(side="left", padx=10)
        ctk.CTkButton(action_frame, text="완료", command=self.on_done).pack(side="left", padx=10)

        self.bind("<Map>", self.on_page_show)

    def show_preview(self):
        try:
            top_x, top_y = int(self.top_x_entry.get()), int(self.top_y_entry.get())
            bottom_x, bottom_y = int(self.bottom_x_entry.get()), int(self.bottom_y_entry.get())
            if (bottom_x - top_x) <= 0 or (bottom_y - top_y) <= 0: raise ValueError("잘못된 좌표 영역입니다.")
            
            self.controller.update_status("미리보기를 준비하는 중...")
            self.after(300, lambda: self._delayed_preview((top_x, top_y, bottom_x, bottom_y)))
        except (ValueError, TypeError) as e: self.controller.update_status(f"오류: {e}")
        except Exception as e: self.controller.update_status(f"미리보기 오류: {e}")

    def _delayed_preview(self, coords):
        try:
            top_x, top_y, bottom_x, bottom_y = coords
            full_screenshot = pyautogui.screenshot()
            scale = self.controller.scale_factor
            crop_box = (top_x * scale, top_y * scale, bottom_x * scale, bottom_y * scale)
            PreviewWindow(self, image=full_screenshot.crop(crop_box))
        except Exception as e:
            self.controller.update_status(f"미리보기 오류: {e}")

    def on_page_show(self, event):
        if self.controller.top_left_coord: self.update_entry("top_left", self.controller.top_left_coord)
        if self.controller.bottom_right_coord: self.update_entry("bottom_right", self.controller.bottom_right_coord)

    def on_done(self):
        try:
            self.controller.top_left_coord = (int(self.top_x_entry.get()), int(self.top_y_entry.get()))
            self.controller.bottom_right_coord = (int(self.bottom_x_entry.get()), int(self.bottom_y_entry.get()))
            self.controller.show_frame("MainPage")
        except (ValueError, TypeError): self.controller.update_status("오류: 모든 좌표는 숫자로 입력해야 합니다.")


    # 마우스 위치 캡처 기능
    def capture_mouse_position(self, target):
        self._start_capture_countdown(target, 5)

    def _start_capture_countdown(self, target, count):
        if count > 0:
            msg = "왼쪽 상단" if target == "top_left" else "오른쪽 하단"
            self.controller.update_status(f"{count}초 후 {msg} 좌표를 캡처합니다. 원하는 위치에 마우스를 올려두세요.")
            self.after(1000, lambda: self._start_capture_countdown(target, count - 1))
        else:
            self._set_mouse_position(target)

    def _set_mouse_position(self, target):
        try:
            x, y = pyautogui.position()
            self.update_entry(target, (x, y))
            if target == "top_left":
                self.controller.top_left_coord = (x, y)
                self.controller.update_status("왼쪽 상단 좌표가 설정되었습니다.")
            else:
                self.controller.bottom_right_coord = (x, y)
                self.controller.update_status("오른쪽 하단 좌표가 설정되었습니다.")
        except Exception as e:
            self.controller.update_status(f"마우스 위치 읽기 오류: {e}")

    def update_entry(self, target, coords):
        x_entry = self.top_x_entry if target == "top_left" else self.bottom_x_entry
        y_entry = self.top_y_entry if target == "top_left" else self.bottom_y_entry
        x_entry.delete(0, "end"); x_entry.insert(0, str(coords[0]))
        y_entry.delete(0, "end"); y_entry.insert(0, str(coords[1]))

    def calibrate_screen_scale(self):
        self._start_calibration_countdown(5)

    def _start_calibration_countdown(self, count):
        if count > 0:
            self.controller.update_status(f"{count}초 후 화면의 우측 하단 좌표를 캡처합니다. 마우스를 화면 제일 오른쪽 아래로 이동시켜주세요.")
            self.after(1000, lambda: self._start_calibration_countdown(count - 1))
        else:
            self._capture_screen_scale()

    def _capture_screen_scale(self):
        try:
            import subprocess
            import re
            # 실제 화면 해상도 얻기
            cmd = ["system_profiler", "SPDisplaysDataType"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = result.stdout
            physical_res_match = re.search(r"Resolution: (\d+) x (\d+)", output)
            
            if not physical_res_match:
                raise ValueError("화면 해상도를 가져올 수 없습니다.")
            
            physical_width = int(physical_res_match.group(1))
            physical_height = int(physical_res_match.group(2))
            
            # 현재 마우스 위치 (논리적 좌표)
            mouse_x, mouse_y = pyautogui.position()
            
            if mouse_x == 0 or mouse_y == 0:
                raise ValueError("마우스 위치를 가져올 수 없습니다.")
            
            # 스케일 계산
            width_scale = physical_width / mouse_x
            height_scale = physical_height / mouse_y
            
            # 평균 스케일 사용
            new_scale = (width_scale + height_scale) / 2
            self.controller.scale_factor = new_scale
            self.scale_label.configure(text=f"현재 스케일: {new_scale:.2f}")
            self.controller.update_status(f"화면 스케일이 {new_scale:.2f}로 보정되었습니다.")
            
        except Exception as e:
            self.controller.update_status(f"스케일 보정 오류: {e}")

    # update_top_left, update_bottom_right 제거 (불필요)

class KeyPressPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text="페이지를 넘기는 데 사용할 키를 누르세요...", font=ctk.CTkFont(size=18)).pack(pady=40, padx=10)
        self.key_label = ctk.CTkLabel(self, text="(입력 대기 중)", font=ctk.CTkFont(size=24, weight="bold"))
        self.key_label.pack(pady=20)

        # 키보드 이벤트를 컨트롤러에 바인딩
        self.bind("<Map>", self._on_map)
        self.bind("<Unmap>", self._on_unmap)

    def _on_map(self, event):
        self.key_label.configure(text="(입력 대기 중)")
        self.controller.bind("<KeyPress>", self.on_key_press)
        self.focus_set()  # 포커스 확보

    def _on_unmap(self, event):
        self.controller.unbind("<KeyPress>")

    def on_key_press(self, event):
        key_name = event.keysym
        self.controller.page_turn_key = key_name
        self.key_label.configure(text=f"선택된 키: '{key_name}'")
        self.controller.frames["MainPage"].key_label.configure(text=f"({key_name})")
        self.controller.after(500, lambda: self.controller.show_frame("MainPage"))

class ScreenshotWorker(threading.Thread):
    def __init__(self, app, settings):
        super().__init__()
        self.app = app
        self.settings = settings
        self.daemon = True

    def run(self):
        try:
            os.makedirs(self.app.IMAGE_FOLDER, exist_ok=True)
            region = self.settings['region']
            scale = self.app.scale_factor
            
            # 캡처 영역 계산 (스케일 팩터는 나중에 적용)
            capture_region = (
                region[0],
                region[1],
                region[0] + region[2],
                region[1] + region[3]
            )
            
            for i in range(self.settings['total_pages']):
                page_num = i + 1
                self.app.update_status(f"({page_num}/{self.settings['total_pages']}) 화면 캡처 중...")
                file_path = os.path.join(self.app.IMAGE_FOLDER, f"page_{page_num:03d}.png")
                
                # screencapture 명령어를 위한 영역 계산 (x,y,width,height)
                scale = self.app.scale_factor
                x = int(region[0] * scale)
                y = int(region[1] * scale)
                width = int(region[2] * scale)
                height = int(region[3] * scale)
                capture_rect = f"{x},{y},{width},{height}"

                # [변경] pyautogui -> screencapture 명령어로 교체
                subprocess.run(["screencapture", "-x", "-R", capture_rect, file_path], check=True)
                
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"{page_num}페이지 캡처 실패! 권한을 확인하세요.")
                
                if i < self.settings['total_pages'] - 1:
                    self.app.update_status(f"({page_num}/{self.settings['total_pages']}) 캡처 성공. 페이지 넘기는 중...")
                    turn_method = self.settings['turn_method']
                    turn_details = self.settings['turn_details']
                    
                    if turn_method == 'click':
                        x, y = turn_details
                        pyautogui.click(x=int(x), y=int(y))
                    else:
                        pyautogui.press(turn_details)
                        
                    time.sleep(self.settings['delay'])
            
            self.app.update_status("PDF 변환 중...")
            self.process_and_convert_to_pdf()
        except Exception as e:
            self.app.update_status(f"오류: {e}")
            import traceback
            print(traceback.format_exc())  # 디버깅을 위한 상세 오류 출력
        finally:
            self.app.after(0, self.app.on_task_done)

    def process_and_convert_to_pdf(self):
        image_files = sorted([f for f in os.listdir(self.app.IMAGE_FOLDER) if f.endswith(".png")])
        if not image_files:
            self.app.update_status("캡처된 이미지가 없어 PDF를 생성할 수 없습니다.")
            return

        os.makedirs(self.app.PDF_FOLDER, exist_ok=True)
        pdf_path = os.path.join(self.app.PDF_FOLDER, f"{self.settings['pdf_name']}.pdf")
        image_paths = [os.path.join(self.app.IMAGE_FOLDER, f) for f in image_files]

        try:
            first_image = None
            append_images = []
            for i, path in enumerate(image_paths):
                with Image.open(path) as img:
                    # 이미지는 이미 크롭되어 있으므로, RGB 변환만 수행
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')
                    if i == 0:
                        first_image = img
                    else:
                        append_images.append(img)
            
            if first_image:
                first_image.save(pdf_path, "PDF", resolution=100.0, save_all=True, append_images=append_images)
                self.app.update_status("작업 완료! 'PDFs' 폴더를 확인하세요.")
        except Exception as e:
            self.app.update_status(f"PDF 변환 오류: {e}")
        finally:
            for p in image_paths:
                try: os.remove(p)
                except OSError: pass

if __name__ == "__main__":
    app = App()
    app.mainloop()
