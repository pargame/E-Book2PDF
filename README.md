# E-Book to PDF (GUI Edition)

전자책 뷰어의 특정 영역을 자동으로 스크린샷하고, 페이지를 넘기며, 캡처된 이미지들을 하나의 PDF 파일로 합치는 GUI 애플리케이션입니다.

![GUI Screenshot](https://user-images.githubusercontent.com/12345/67890.png) 
*(스크린샷 예시: 여기에 실제 앱 스크린샷 이미지가 들어갈 수 있습니다.)*

## 주요 기능
- **직관적인 GUI**: 모든 설정을 그래픽 인터페이스를 통해 간편하게 할 수 있습니다.
- **정확한 좌표 설정**: 십자(+) 포인터가 표시되는 전체 화면 오버레이를 통해 캡처 영역을 정확하게 지정할 수 있습니다.
- **다양한 페이지 넘김**: 마우스 클릭 또는 키보드 키 누름 방식을 선택하여 페이지를 넘길 수 있습니다.
- **실시간 진행 상황**: 앱 하단의 상태바를 통해 현재 작업 진행 상황을 실시간으로 확인할 수 있습니다.
- **안전한 작업 실행**: 스크린샷 작업 중에는 모든 설정이 비활성화되어 오작동을 방지합니다.

## 설치 및 실행

### 1. 프로젝트 준비
```bash
git clone https://github.com/pargamer/E-Book2PDF.git
cd E-Book2PDF
```

### 2. 가상 환경 설정 및 라이브러리 설치
독립된 가상 환경에서 프로젝트에 필요한 라이브러리들을 설치합니다.
```bash
# 가상 환경 생성 (최초 1회)
python3 -m venv venv

# 가상 환경 활성화
source venv/bin/activate

# 필수 라이브러리 설치
pip install -r requirements.txt
```

### 3. 애플리케이션 실행
아래 명령어로 GUI 애플리케이션을 실행합니다.
```bash
python3 app.py
```

## 사용 방법

1.  **시작**: 첫 화면에서 '시작' 버튼을 클릭합니다.
2.  **스크린샷 범위 설정**:
    - '스크린샷 범위 설정' 버튼을 클릭합니다.
    - '왼쪽 상단 좌표 설정' 버튼을 누르면 화면이 반투명해지며 십자 커서가 나타납니다. 원하는 지점을 클릭하세요.
    - '오른쪽 하단 좌표 설정'도 동일하게 진행합니다.
    - 설정이 끝나면 '완료' 버튼을 누릅니다.
3.  **페이지 수 입력**: 캡처할 총 페이지 수를 입력합니다.
4.  **페이지 넘김 방식 선택**:
    - **키보드**: 라디오 버튼 선택 시, 키 입력 화면으로 이동합니다. 페이지 넘김에 사용할 키(예: 오른쪽 화살표)를 누르면 자동으로 메인 화면으로 돌아옵니다.
    - **마우스 클릭**: 라디오 버튼 선택 후, '클릭 위치 설정' 버튼을 눌러 나타나는 십자 커서로 페이지 넘김 영역을 클릭합니다.
5.  **딜레이 설정**: 페이지 넘김 후 다음 캡처까지의 대기 시간(초)을 설정합니다. (기본값 1.5초)
6.  **프로그램 시작**: 모든 설정이 완료되면 '프로그램 시작' 버튼을 누르세요. 작업이 진행되는 동안 상태바에 진행 상황이 표시됩니다.
7.  **완료**: 작업이 끝나면 "작업 완료!" 메시지가 표시되고, `PDFs` 폴더 안에 결과물이 저장됩니다. 스크린샷 이미지들은 자동으로 삭제됩니다.

## 주의사항
- 스크린샷 작업이 시작되면 완료될 때까지 컴퓨터 사용을 중단하는 것이 좋습니다.
- `PDFs` 폴더는 프로그램이 자동으로 생성합니다.

## 실행 파일 빌드 및 배포 (개발자용)

이 프로젝트를 다른 사용자들이 쉽게 사용할 수 있도록 각 운영체제에 맞는 실행 파일로 만들어 배포할 수 있습니다.

### 1. 빌드 환경 준비
- **macOS**: Xcode Command Line Tools가 설치되어 있어야 합니다.
- **Windows**: Python 공식 설치 프로그램으로 Python을 설치해야 합니다.
- 각 OS에서 프로젝트를 `git clone`하고, 아래 명령어로 가상 환경 설정 및 라이브러리 설치를 완료하세요.
  ```bash
  # 가상 환경 생성 및 활성화
  python3 -m venv venv
  source venv/bin/activate  # macOS/Linux
  # venv\Scripts\activate   # Windows

  # 라이브러리 설치 (PyInstaller 포함)
  python3 -m pip install -r requirements.txt
  python3 -m pip install pyinstaller
  ```

### 2. OS별 빌드 실행
각 운영체제 환경에서 아래의 해당 명령어를 실행하면 `dist` 폴더에 실행 파일이 생성됩니다.

- **macOS (.app)**
  ```bash
  venv/bin/pyinstaller app.py --name "E-Book to PDF" --windowed --onefile --noconfirm
  ```
- **Windows (.exe)**
  ```bash
  venv\Scripts\pyinstaller app.py --name "E-Book to PDF" --windowed --onefile --noconfirm
  ```

### 3. GitHub Releases를 통한 배포 방법
**중요**: 빌드된 실행 파일은 Git 저장소에 직접 커밋하지 마세요. 아래 절차에 따라 GitHub Releases에 업로드해야 합니다.

1.  **결과물 압축**:
    -   macOS: `dist` 폴더에 생성된 `E-Book to PDF.app`을 마우스 오른쪽 버튼으로 클릭하여 **"E-Book to PDF" 압축**을 선택해 `.zip` 파일로 만듭니다.
    -   Windows: `dist` 폴더의 `E-Book to PDF.exe` 파일을 그대로 사용하거나 `.zip`으로 압축합니다.

2.  **GitHub 저장소에서 릴리스 생성**:
    -   브라우저에서 당신의 GitHub 저장소 페이지로 이동합니다.
    -   오른쪽 사이드바에서 **"Releases"**를 클릭합니다.
    -   **"Create a new release"** 또는 **"Draft a new release"** 버튼을 클릭합니다.

3.  **릴리스 정보 입력**:
    -   **"Choose a tag"**: 버전 태그를 입력하고 만듭니다. (예: `v1.0.0`)
    -   **"Release title"**: 릴리스 제목을 입력합니다. (예: `v1.0.0 - First Release`)
    -   **"Describe this release"**: 이 버전의 주요 변경 사항이나 새로운 기능을 간략히 설명합니다.

4.  **파일 첨부**:
    -   **"Attach binaries by dropping them here or selecting them."** 박스 안에, 1단계에서 준비한 OS별 압축 파일들(`E-Book to PDF.app.zip`, `E-Book to PDF.exe` 등)을 끌어다 놓거나 선택하여 업로드합니다.

5.  **릴리스 발행**:
    -   **"Publish release"** 버튼을 클릭하여 릴리스를 최종 발행합니다.

이제 사용자들은 당신의 GitHub Releases 페이지에서 자신의 OS에 맞는 실행 파일을 직접 다운로드할 수 있습니다.
