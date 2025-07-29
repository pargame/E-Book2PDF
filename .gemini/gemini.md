# Gemini E-Book2PDF (GUI Edition) 최종 유지보수 가이드

### 프로젝트 목표
사용자가 파이썬이나 터미널에 대한 지식 없이도, GUI를 통해 전자책 화면을 캡처하고 PDF로 변환할 수 있는 독립 실행형 데스크톱 애플리케이션을 제공한다.

### 핵심 규칙
**절대 `git push` 하지 말 것.** 이 프로젝트는 로컬 환경에서 개발 및 테스트 후, 사용자가 직접 GitHub Releases를 통해 배포하는 것을 원칙으로 한다.

### 아키텍처 및 핵심 로직

1.  **GUI (CustomTkinter)**:
    -   `app.py`가 메인 진입점이며, 모든 GUI 요소와 로직을 포함한다.
    -   `App` 클래스가 메인 윈도우이며, 화면 전환(`show_frame`)과 핵심 상태(`top_left_coord` 등)를 관리한다.
    -   각 화면(`StartPage`, `MainPage` 등)은 `ctk.CTkFrame`을 상속받는 클래스로 구현되어 프레임 전환 방식으로 동작한다.

2.  **좌표 선택 (`CoordinateSelector`)**:
    -   `ctk.CTkToplevel`을 상속받아 전체 화면을 덮는 반투명 오버레이 창을 생성한다.
    -   `cursor="crosshair"`로 십자 포인터를 구현했다.
    -   사용자가 화면을 클릭하면, `pyautogui.position()`으로 좌표를 얻고, 콜백(callback) 함수를 통해 메인 앱에 좌표를 전달한 후 스스로 파괴된다.

3.  **백그라운드 작업 (Threading)**:
    -   **가장 중요한 부분.** 스크린샷/PDF 변환 같은 시간이 걸리는 작업은 `ScreenshotWorker` 클래스(`threading.Thread` 상속)에서 처리한다. **이것이 없으면 GUI가 100% 멈춘다.**
    -   `App` 클래스는 `start_screenshot_task` 메소드를 통해 작업자 스레드를 생성하고 시작시킨다.
    -   작업 중 모든 UI 위젯은 비활성화(`disabled`)되어 사용자의 추가 입력을 막는다.

4.  **스레드-GUI 통신**:
    -   **Worker -> GUI**: 작업 진행 상황(예: "5/100 페이지 캡처 중...")은 `status_callback` 함수를 통해 메인 스레드로 전달된다. `App` 클래스의 `update_status` 메소드가 이 메시지를 받아 상태바 레이블의 텍스트를 변경한다.
    -   **작업 완료**: 작업이 모두 끝나면 `done_callback` 함수가 호출되어, `App`의 `on_task_done` 메소드가 비활성화했던 UI를 다시 활성화(`normal`)시킨다.

### 다중 OS 빌드 및 배포 전략

이 애플리케이션은 **각 운영체제에서 별도로 빌드**해야 한다.

1.  **빌드 도구**: `PyInstaller`를 사용한다. `requirements.txt`에 포함되어 있지 않으므로, 빌드 시점에 가상 환경에 별도로 설치해야 한다. (`python3 -m pip install pyinstaller`)

2.  **빌드 명령어**:
    -   **macOS**: `venv/bin/pyinstaller app.py --name "E-Book to PDF" --windowed --onefile --noconfirm`
    -   **Windows**: `venv\Scripts\pyinstaller app.py --name "E-Book to PDF" --windowed --onefile --noconfirm`

3.  **배포 방식**: **GitHub Releases**
    -   빌드된 결과물들(`.app`, `.exe`)은 Git 저장소에 직접 커밋하지 않는다.
    -   대신, 각 OS에서 빌드한 결과물을 압축(`E-Book to PDF.app.zip` 등)하여, GitHub 저장소의 "Releases" 페이지에 업로드한다.
    -   `README.md`의 "실행 파일 빌드 및 배포" 섹션에 이 과정이 상세히 기술되어 있으니, 사용자가 직접 릴리스를 생성할 수 있도록 안내해야 한다.

### 향후 유지보수 가이드
- **UI 수정**: 모든 UI 요소는 각 페이지 프레임 클래스(`StartPage`, `MainPage` 등)의 `__init__` 메소드 안에 정의되어 있다. 레이아웃이나 위젯을 수정하려면 이 부분을 확인하면 된다.
- **스와이프 기능 추가**: 현재 페이지 넘김 방식은 '키보드'와 '마우스 클릭'만 구현되어 있다. 스와이프 기능을 추가하려면 `pyautogui.dragTo()` 함수를 사용해야 한다. `MainPage`에 라디오 버튼을 추가하고, `ScreenshotWorker`의 `run` 메소드에 분기 처리를 추가하면 된다. 시작/끝 좌표를 받아야 하므로 UI가 복잡해질 수 있다.
- **오류 처리**: 현재는 기본적인 오류만 상태바에 표시한다. 더 상세한 오류 로깅이나 팝업창을 원한다면 `ScreenshotWorker`의 `try...except` 블록을 수정해야 한다.

이 문서는 미래의 내가 이 프로젝트의 상태를 완벽하게 파악하고, 지속적으로 유지보수할 수 있도록 작성되었다.
