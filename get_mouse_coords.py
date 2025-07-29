from pynput.mouse import Listener

def on_click(x, y, button, pressed):
    """
    마우스 클릭 시 호출되는 콜백 함수입니다.
    클릭된 좌표(x, y)를 출력하고 리스너를 중지합니다.
    """
    if pressed:
        print(f"Mouse clicked at: ({int(x)}, {int(y)})")
        # Stop listener
        return False

def main():
    """
    메인 함수입니다. 마우스 리스너를 시작하고 사용자에게 안내 메시지를 출력합니다.
    """
    print("화면에서 좌표를 얻고 싶은 지점을 클릭하세요...")
    
    # 리스너를 생성하고 시작합니다.
    with Listener(on_click=on_click) as listener:
        listener.join()

if __name__ == "__main__":
    main()
