# Gemini E-Book2PDF (GUI Edition) 프로젝트 메모

### 프로젝트 개요
이 프로젝트는 사용자가 전자책 화면을 캡처하여 PDF로 변환할 수 있도록 돕는 GUI 애플리케이션이다. 기존 CLI 버전에서 CustomTkinter를 사용한 완전한 GUI 앱으로 재구축되었다.

### 핵심 규칙
**절대 `git push` 하지 말 것.** 이 프로젝트는 로컬 환경에서만 관리한다.

### 아키텍처 및 핵심 로직

1.  **GUI (CustomTkinter)**:
    - `app.py`가 메인 진입점이며, 모든 GUI 요소와 로직을 포함한다.
    - `App` 클래스가 메인 윈도우이며, 화면 전환을 관리하는 컨테이너 역할을 한다.
    - 각 화면(`StartPage`, `MainPage` 등)은 `ctk.CTkFrame`을 상속받는 클래스로 구현되어 프레임 전환 방식으로 동작한다.

2.  **좌표 선택 (`CoordinateSelector`)**:
    - `ctk.CTkToplevel`을 상속받아 전체 화면을 덮는 반투명 오버레이 창을 생성한다.
    - `cursor="crosshair"`로 십자 포인터를 구현했다.
    - 사용자가 화면을 클릭하면, `pyautogui.position()`으로 좌표를 얻고, 콜백(callback) 함수를 통해 메인 앱에 좌표를 전달한 후 스스로 파괴된다. 5초 딜레이 방식보다 훨씬 직관적이다.

3.  **백그라운드 작업 (Threading)**:
    - **가장 중요한 부분.** 스크린샷/PDF 변환 같은 시간이 걸리는 작업은 `ScreenshotWorker` 클래스(`threading.Thread` 상속)에서 처리한다. **이것이 없으면 GUI가 100% 멈춘다.**
    - `App` 클래스는 `start_screenshot_task` 메소드를 통해 작업자 스레드를 생성하고 시작시킨다.
    - 작업 중 모든 UI 위젯은 비활성화(`disabled`)되어 사용자의 추가 입력을 막는다.

4.  **스레드-GUI 통신**:
    - **Worker -> GUI**: 작업 진행 상황(예: "5/100 페이지 캡처 중...")은 `status_callback` 함수를 통해 메인 스레드로 전달된다. `App` 클래스의 `update_status` 메소드가 이 메시지를 받아 상태바 레이블의 텍스트를 변경한다.
    - **작업 완료**: 작업이 모두 끝나면 `done_callback` 함수가 호출되어, `App`의 `on_task_done` 메소드가 비활성화했던 UI를 다시 활성화(`normal`)시킨다.

### 향후 유지보수 가이드
- **UI 수정**: 모든 UI 요소는 각 페이지 프레임 클래스(`StartPage`, `MainPage` 등)의 `__init__` 메소드 안에 정의되어 있다. 레이아웃이나 위젯을 수정하려면 이 부분을 확인하면 된다.
- **스와이프 기능 추가**: 현재 페이지 넘김 방식은 '키보드'와 '마우스 클릭'만 구현되어 있다. 스와이프 기능을 추가하려면 `pyautogui.dragTo()` 함수를 사용해야 한다. `MainPage`에 라디오 버튼을 추가하고, `ScreenshotWorker`의 `run` 메소드에 분기 처리를 추가하면 된다. 시작/끝 좌표를 받아야 하므로 UI가 복잡해질 수 있다.
- **패키징 (`PyInstaller`)**: 만약 이 앱을 실행 파일로 배포해야 한다면, `PyInstaller`를 사용한다. `pyinstaller app.py --onefile --windowed` 와 같은 명령어를 사용하게 될 것이다. 이때 `customtkinter`나 `pynput` 같은 라이브러리의 숨겨진 의존성 때문에 빌드가 실패할 수 있으며, `.spec` 파일을 수정해야 할 수도 있다.
- **오류 처리**: 현재는 기본적인 오류만 상태바에 표시한다. 더 상세한 오류 로깅이나 팝업창을 원한다면 `ScreenshotWorker`의 `try...except` 블록을 수정해야 한다.

이 메모가 미래의 유지보수 작업을 더 쉽게 만들어주길 바란다.