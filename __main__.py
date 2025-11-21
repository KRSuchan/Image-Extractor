import glob
import os
import shutil
import tkinter as tk
from collections import defaultdict
from tkinter import filedialog, messagebox, ttk
from bs4 import BeautifulSoup
import urllib.request

# tkinter GUI 설정
root = tk.Tk()
root.title("HTML 링크 다운로드 프로그램")
root.geometry("500x550")

selected_path = ""

# 경로 선택 함수
def choose_folder():
    global selected_path
    selected_path = filedialog.askdirectory(title="HTML 파일이 있는 폴더를 선택하세요")
    if selected_path:
        path_label.config(text=selected_path)

# HTML 처리 함수
def process_html_files():
    if not selected_path:
        messagebox.showwarning("경고", "먼저 경로를 선택해주세요.")
        return

    tag = tag_entry.get().strip()
    class_name = class_entry.get().strip()

    if not tag or not class_name:
        messagebox.showwarning("경고", "태그와 클래스 이름을 입력해주세요.")
        return

    selector = f"{tag}.{class_name}"
    html_files = glob.glob(os.path.join(selected_path, "*.html"))

    if not html_files:
        messagebox.showwarning("경고", "HTML 파일이 없습니다.")
        return

    progress_bar["maximum"] = len(html_files)
    progress_bar["value"] = 0
    log_listbox.delete(0, tk.END)

    for html_file in html_files:

        # HTML 파일명에서 제목 추출
        title = os.path.splitext(os.path.basename(html_file))[0].split(' - ')[0]
        filename_counter = defaultdict(int)

        # 출력 폴더 생성
        output_dir = os.path.join(selected_path, title)
        os.makedirs(output_dir, exist_ok=True)

        # HTML 파싱
        with open(html_file, 'r', encoding='utf-8') as file:
            html = file.read()

        soup = BeautifulSoup(html, 'html.parser')
        target_div = soup.select_one(selector)

        used_dirs = set()

        if target_div:
            idx = 0

            # a 태그의 href만 다운로드
            for a in target_div.find_all('a'):
                href = a.get('href', '')
                if not href:
                    continue

                # 절대 경로일 경우 처리
                if href.startswith("http://") or href.startswith("https://"):
                    src_path = href
                else:
                    src_path = os.path.normpath(os.path.join(os.path.dirname(html_file), href))

                filename = os.path.basename(src_path)
                if not filename:
                    continue

                # 확장자 추출
                original_name, ext = os.path.splitext(filename)
                if not ext:
                    ext = ".dat"  # 확장자가 없는 경우 기본값

                count = filename_counter[filename]
                if count != 0:
                    continue

                idx += 1
                new_filename = f"{title} ({idx}){ext}"
                dst_path = os.path.join(output_dir, new_filename)

                try:
                    # 다운로드 실행
                    urllib.request.urlretrieve(src_path, dst_path)
                    log_listbox.insert(tk.END, f"⬇ 다운로드 완료: {new_filename}")
                except Exception as e:
                    log_listbox.insert(tk.END, f"⚠ 다운로드 실패: {src_path} - {e}")

        # HTML 파일 삭제 옵션
        if delete_html_var.get():
            try:
                os.remove(html_file)
                log_listbox.insert(tk.END, f"🗑 HTML 삭제됨: {html_file}")
            except Exception as e:
                log_listbox.insert(tk.END, f"⚠ HTML 삭제 실패: {html_file} - {e}")

        progress_bar["value"] += 1
        root.update_idletasks()

    messagebox.showinfo("완료", "모든 작업이 완료되었습니다.")

# GUI 시작
label = tk.Label(root, text="HTML에서 a태그 링크 다운로드 프로그램", pady=10)
label.pack()

select_btn = tk.Button(root, text="폴더 선택", command=choose_folder)
select_btn.pack(pady=5)

path_label = tk.Label(root, text="선택된 경로 없음", fg="blue")
path_label.pack()

# 태그와 클래스명 입력
tag_frame = tk.Frame(root)
tag_frame.pack(pady=5)

tk.Label(tag_frame, text="태그:").pack(side="left")
tag_entry = tk.Entry(tag_frame, width=10)
tag_entry.insert(0, "div")
tag_entry.pack(side="left", padx=5)

tk.Label(tag_frame, text="클래스명:").pack(side="left")
class_entry = tk.Entry(tag_frame, width=20)
class_entry.insert(0, "article-content")
class_entry.pack(side="left")

btn = tk.Button(root, text="작업 시작", command=process_html_files)
btn.pack(pady=5)

# 체크박스
delete_html_var = tk.BooleanVar(value=True)
check2 = tk.Checkbutton(root, text="HTML 파일 삭제", variable=delete_html_var)
check2.pack()

# 진행률 바
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

# 로그 출력 리스트박스
log_frame = tk.LabelFrame(root, text="작업 로그")
log_frame.pack(fill="both", expand=True, padx=10, pady=5)

log_listbox = tk.Listbox(log_frame, height=10)
log_listbox.pack(fill="both", expand=True)

root.mainloop()
