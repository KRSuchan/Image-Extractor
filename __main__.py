import glob
import os
import shutil
import tkinter as tk
from collections import defaultdict
from tkinter import filedialog, messagebox, ttk

from bs4 import BeautifulSoup

# tkinter GUI 설정
root = tk.Tk()
root.title("HTML 이미지 추출기")
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
        title = os.path.splitext(os.path.basename(html_file))[0].split(' - ')[0]
        filename_counter = defaultdict(int)
        output_dir = os.path.join(selected_path, title)
        os.makedirs(output_dir, exist_ok=True)

        with open(html_file, 'r', encoding='utf-8') as file:
            html = file.read()

        soup = BeautifulSoup(html, 'html.parser')
        target_div = soup.select_one(selector)

        used_dirs = set()

        if target_div:
            idx = 0
            for img in target_div.find_all('img'):
                src = img.get('src', '')
                if not src:
                    continue

                src_path = os.path.normpath(os.path.join(os.path.dirname(html_file), src))
                if not os.path.isfile(src_path):
                    continue

                image_dir = os.path.normpath(os.path.dirname(src_path))
                used_dirs.add(image_dir)

                filename = os.path.basename(src_path)
                original_name, ext = os.path.splitext(filename)

                count = filename_counter[filename]
                if count != 0:
                    continue

                idx += 1
                new_filename = f"{title} ({idx}){ext}"
                dst_path = os.path.join(output_dir, new_filename)
                shutil.move(src_path, dst_path)
                log_listbox.insert(tk.END, f"✔ {filename} → {new_filename}")

        # 폴더 삭제
        if delete_images_var.get():
            for image_dir in used_dirs:
                if os.path.isdir(image_dir):
                    try:
                        shutil.rmtree(image_dir)
                        log_listbox.insert(tk.END, f"🗑 폴더 삭제됨: {image_dir}")
                    except Exception as e:
                        log_listbox.insert(tk.END, f"⚠ 폴더 삭제 실패: {image_dir} - {e}")

        # HTML 파일 삭제
        if delete_html_var.get():
            try:
                os.remove(html_file)
                log_listbox.insert(tk.END, f"🗑 HTML 삭제됨: {html_file}")
            except Exception as e:
                log_listbox.insert(tk.END, f"⚠ HTML 삭제 실패: {html_file} - {e}")

        progress_bar["value"] += 1
        root.update_idletasks()

    messagebox.showinfo("완료", "모든 작업이 완료되었습니다.")


# GUI 위젯들
label = tk.Label(root, text="HTML 파일 폴더에서 이미지 추출 및 정리", pady=10)
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

# 체크박스들
delete_images_var = tk.BooleanVar(value=True)
delete_html_var = tk.BooleanVar(value=True)

check1 = tk.Checkbutton(root, text="이미지 원본 폴더 삭제", variable=delete_images_var)
check2 = tk.Checkbutton(root, text="HTML 파일 삭제", variable=delete_html_var)
check1.pack()
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
