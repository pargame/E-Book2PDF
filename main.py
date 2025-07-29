import pyautogui
import time
import os
from pynput.mouse import Listener
from PIL import Image

def get_click_coords(prompt):
    """
    사용자에게 프롬프트를 표시하고, 마우스 클릭을 기다린 후
    클릭된 지점의 좌표 (x, y)를 반환합니다.
    """
    print(prompt)
    
    coords = []

    # on_click 함수를 내부에서 정의하여 coords 리스트에 접근
    def on_click(x, y, button, pressed):
        if pressed:
            coords.append(int(x))
            coords.append(int(y))
            # 리스너 중지
            return False

    # 리스너 시작
    with Listener(on_click=on_click) as listener:
        listener.join()
    
    print(f"  -> 좌표 등록 완료: ({coords[0]}, {coords[1]})")
    return tuple(coords)

def get_user_input():
    """사용자로부터 필요한 정보를 입력받습니다."""
    
    top_left = get_click_coords("\n[1/3] 캡처 영역의 좌측 상단(Top-Left)을 클릭하세요...")
    bottom_right = get_click_coords("\n[2/3] 캡처 영역의 우측 하단(Bottom-Right)을 클릭하세요...")
    
    total_pages = int(input("\n캡처할 총 페이지 수를 입력하세요: "))
    
    click_point = get_click_coords("\n[3/3] 페이지를 넘기기 위해 클릭할 위치를 클릭하세요...")
    
    return top_left, bottom_right, total_pages, click_point

def convert_images_to_pdf(image_folder, pdf_name):
    """지정된 폴더의 이미지들을 PDF 파일로 변환합니다."""
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    
    if not images:
        print("PDF로 변환할 이미지가 없습니다.")
        return

    # 파일 이름순으로 정렬
    images.sort()

    print(f"\n'{pdf_name}.pdf' 파일 생성을 시작합니다...")

    # 이미지 열기
    pil_images = []
    for img_file in images:
        path = os.path.join(image_folder, img_file)
        # PDF 저장 시 발생할 수 있는 오류를 방지하기 위해 'RGB' 모드로 변환
        pil_img = Image.open(path).convert('RGB')
        pil_images.append(pil_img)

    # 첫 번째 이미지를 기준으로 나머지 이미지를 추가하여 PDF 저장
    pil_images[0].save(
        f"{pdf_name}.pdf", "PDF" ,resolution=100.0, save_all=True, append_images=pil_images[1:]
    )
    
    print(f"'{pdf_name}.pdf' 파일이 성공적으로 생성되었습니다.")


def main():
    """메인 자동화 로직을 수행합니다."""
    image_folder = "screenshots"
    # 스크린샷 저장 폴더 생성
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    captured_pages = 0
    try:
        (tl_x, tl_y), (br_x, br_y), total_pages, (click_x, click_y) = get_user_input()
    except ValueError:
        print("\n오류: 잘못된 값을 입력했습니다. 페이지 수에는 숫자를 입력해주세요.")
        return
    except KeyboardInterrupt:
        print("\n사용자에 의해 프로그램이 중단되었습니다.")
        return

    # 캡처 영역 계산
    width = br_x - tl_x
    height = br_y - tl_y
    
    # 너비나 높이가 0보다 작거나 같으면 오류 처리
    if width <= 0 or height <= 0:
        print(f"\n오류: 잘못된 캡처 영역입니다. 좌측 상단 좌표 ({tl_x}, {tl_y})가 우측 하단 좌표 ({br_x}, {br_y})보다 앞에 있어야 합니다.")
        return
        
    region = (tl_x, tl_y, width, height)

    print("\n자동 캡처를 시작합니다. 5초 후에 시작됩니다...")
    print("중지하려면 터미널에서 Ctrl+C를 누르세요.")
    time.sleep(5)

    try:
        for i in range(total_pages):
            page_num = i + 1
            file_name = f"{image_folder}/page_{page_num:03d}.png"
            
            print(f"  - {page_num}/{total_pages} 페이지 캡처 중...")

            # 스크린샷 캡처
            pyautogui.screenshot(file_name, region=region)
            captured_pages += 1

            # 페이지 넘김
            pyautogui.click(click_x, click_y)

            # 페이지 넘김 대기
            time.sleep(1.5)
            
    except KeyboardInterrupt:
        print("\n작업이 중단되었습니다.")
    except Exception as e:
        print(f"\n오류가 발생했습니다: {e}")
    finally:
        if captured_pages > 0:
            print(f"\n캡처 작업이 완료되었습니다.")
            print(f"{captured_pages}개의 이미지가 '{image_folder}' 폴더에 저장되었습니다.")
            
            try:
                pdf_name = input("\n저장할 PDF 파일의 이름을 입력하세요 (확장자 제외): ").strip()
                if not pdf_name:
                    pdf_name = "output"
                convert_images_to_pdf(image_folder, pdf_name)
            except KeyboardInterrupt:
                print("\nPDF 변환이 취소되었습니다.")
        else:
            print("\n캡처된 이미지가 없어 작업을 종료합니다.")


if __name__ == "__main__":
    main()
