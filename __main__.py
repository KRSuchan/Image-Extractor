import os
import glob
from bs4 import BeautifulSoup
from collections import defaultdict


# 바탕화면 후보 경로들
possible_desktops = [
    os.path.join(os.path.expanduser("~"), "OneDrive", "바탕 화면"),  # 한국어 Windows
    os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop"),   # 영어 Windows
    os.path.join(os.path.expanduser("~"), "Desktop"),               # 일반 경로
]

# 존재하는 바탕화면 경로 찾기
desktop_path = next((path for path in possible_desktops if os.path.exists(path)), None)

if desktop_path is None:
    raise FileNotFoundError("바탕화면 경로를 찾을 수 없습니다.")

# 바탕화면의 HTML 파일 검색
html_files = glob.glob(os.path.join(desktop_path, "*.html"))

# 확인용 출력
print("바탕화면 경로:", desktop_path)
print("HTML 파일 목록:", html_files)

# 중복 방지용 딕셔너리 (파일명: 중복 수)
filename_counter = defaultdict(int)

# 결과 저장용 딕셔너리
results = {}

for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as file:
        html = file.read()

    soup = BeautifulSoup(html, 'html.parser')
    article_div = soup.select_one('div.article-content')

    img_srcs = []
    if article_div:
        for img in article_div.find_all('img'):
            src = img.get('src', '')
            if src:
                filename = os.path.basename(src)  # 파일명만 추출
                original_name, ext = os.path.splitext(filename)

                # 중복 방지 번호 붙이기
                count = filename_counter[filename]
                if count == 0:
                    new_filename = filename
                else:
                    new_filename = f"{original_name}({count}){ext}"

                filename_counter[filename] += 1
                img_srcs.append(new_filename)

    results[html_file] = img_srcs

# 테스트용 결과 출력
for html_file, filenames in results.items():
    print(f"[{html_file}]")
    for name in filenames:
        print("  ", name)
