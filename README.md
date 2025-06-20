# html 이미지 추출기

## 소개

`html 이미지 추출기`는 사용자가 지정한 폴더 내 HTML 파일에서 특정 태그와 클래스명을 가진 영역 내 이미지들을 추출하여  
새 폴더로 이동시키고, 필요 시 원본 이미지 폴더와 HTML 파일을 삭제하는 GUI 기반 편리한 프로그램입니다.

---

## 주요 기능

- 사용자 지정 태그와 클래스명 입력 가능
- 이미지 원본 폴더 삭제 옵션
- HTML 파일 삭제 옵션
- 진행률 표시 및 작업 로그 출력
- 폴더 선택 UI 지원

---

## 실행 환경

- Windows / macOS / Linux (Python 3.x 환경)
- Python 3.x
- `beautifulsoup4` 패키지 필요 (`pip install beautifulsoup4`)

---

## 배포 및 실행 방법

### Python 스크립트 실행

```bash
pip install beautifulsoup4
python __main__.py
```

독립 실행 파일 실행 (PyInstaller 빌드)
bash
복사
편집
pyinstaller --noconsole --onefile extractor_gui.py
빌드 완료 후, dist 폴더 내 생성된 실행파일(.exe 등)을 실행하세요.

## 사용 방법

프로그램 실행

[폴더 선택] 버튼 클릭 후 HTML 파일이 있는 폴더 지정

태그와 클래스명을 입력 (기본값: div, article-content)

이미지 원본 폴더 삭제, HTML 파일 삭제 여부 선택

[작업 시작] 버튼 클릭하여 실행

진행률과 로그를 확인

### 주의사항

이미지 파일은 원본 위치에서 이동되며, 삭제 옵션 사용 시 복구가 불가능합니다.

중요 파일은 미리 백업해 주세요.

### 라이선스

MIT License

제작자
개발자: 이수찬 (Suchan Lee)

기여 및 문의
기능 추가 요청, 버그 제보, 문의는 Issues에 남겨주세요.