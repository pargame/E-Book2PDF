import pyautogui
import time
import os
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener, Key
from PIL import Image

def get_click_coords(prompt):
    """마우스 클릭으로 좌표를 얻습니다."""
    print(prompt)
    coords = []
    def on_click(x, y, button, pressed):
        if pressed:
            coords.extend([int(x), int(y)])
            return False
    with MouseListener(on_click=on_click) as listener:
        listener.join()
    print(f"  -> 좌표 등록 완료: ({coords[0]}, {coords[1]})")
    return tuple(coords)

def get_key_press():
    """페이지 넘김에 사용할 키를 입력받습니다."""
    print("\n[3/3] 페이지를 넘기는 데 사용할 키를 누르세요 (예: 오른쪽 화살표 키)...")
    key_pressed = None
    def on_press(key):
        nonlocal key_pressed
        try:
            key_pressed = key.char
        except AttributeError:
            key_pressed = key.name
        return False
    with KeyboardListener(on_press=on_press) as listener:
        listener.join()
    print(f"  -> 키 등록 완료: '{key_pressed}'")
    return key_pressed

def get_user_input():
    """사용자로부터 모든 필요한 설정을 입력받습니다."""
    top_left = get_click_coords("\n[1/3] 캡처 영역의 좌측 상단(Top-Left)을 클릭하세요...")
    bottom_right = get_click_coords("\n[2/3] 캡처 영역의 우측 하단(Bottom-Right)을 클릭하세요...")
    
    total_pages = int(input("\n캡처할 총 페이지 수를 입력하세요: "))

    page_turn_method = None
    page_turn_details = None

    while page_turn_method is None:
        choice = input("\n페이지 넘김 방식을 선택하세요 (1: 마우스 클릭, 2: 키보드 입력): ").strip()
        if choice == '1':
            page_turn_method = 'click'
            page_turn_details = get_click_coords("\n[3/3] 페이지를 넘기기 위해 클릭할 위치를 클릭하세요...")
        elif choice == '2':
            page_turn_method = 'key'
            page_turn_details = get_key_press()
        else:
            print("오류: 1 또는 2를 입력해주세요.")
            
    return top_left, bottom_right, total_pages, page_turn_method, page_turn_details

def convert_images_to_pdf(image_folder, pdf_name):
    """이미지들을 PDF로 변환합니다."""
    images = sorted([img for img in os.listdir(image_folder) if img.endswith(".png")])
    if not images:
        print("PDF로 변환할 이미지가 없습니다.")
        return

    print(f"\n'{pdf_name}.pdf' 파일 생성을 시작합니다...")
    pil_images = [Image.open(os.path.join(image_folder, img)).convert('RGB') for img in images]
    
    pil_images[0].save(
        f"{pdf_name}.pdf", "PDF", resolution=100.0, save_all=True, append_images=pil_images[1:]
    )
    print(f"'{pdf_name}.pdf' 파일이 성공적으로 생성되었습니다.")

def main():
    """메인 자동화 로직을 수행합니다."""
    image_folder = "screenshots"
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    captured_pages = 0
    try:
        (tl_x, tl_y), (br_x, br_y), total_pages, page_turn_method, page_turn_details = get_user_input()
    except (ValueError, KeyboardInterrupt):
        print("\n오류: 잘못된 값을 입력했거나 사용자에 의해 프로그램이 중단되었습니다.")
        return

    width, height = br_x - tl_x, br_y - tl_y
    if width <= 0 or height <= 0:
        print(f"\n오류: 잘못된 캡처 영역입니다.")
        return
    region = (tl_x, tl_y, width, height)

    input("\n모든 설정이 완료되었습니다. E-Book 뷰어를 활성화하고, Enter 키를 누르면 캡처가 시작됩니다...")

    try:
        for i in range(total_pages):
            page_num = i + 1
            file_name = f"{image_folder}/page_{page_num:03d}.png"
            print(f"  - {page_num}/{total_pages} 페이지 캡처 중...")
            pyautogui.screenshot(file_name, region=region)
            captured_pages += 1

            if page_turn_method == 'click':
                pyautogui.click(page_turn_details)
            elif page_turn_method == 'key':
                pyautogui.press(page_turn_details)

            time.sleep(1.5)
            
    except KeyboardInterrupt:
        print("\n작업이 중단되었습니다.")
    except Exception as e:
        print(f"\n오류가 발생했습니다: {e}")
    finally:
        if captured_pages > 0:
            print(f"\n캡처 작업이 완료되었습니다. {captured_pages}개의 이미지가 '{image_folder}' 폴더에 저장되었습니다.")
            try:
                pdf_name = input("\n저장할 PDF 파일의 이름을 입력하세요 (기본값: output): ").strip() or "output"
                convert_images_to_pdf(image_folder, pdf_name)
            except KeyboardInterrupt:
                print("\nPDF 변환이 취소되었습니다.")
        else:
            print("\n캡처된 이미지가 없어 작업을 종료합니다.")

if __name__ == "__main__":
    main()