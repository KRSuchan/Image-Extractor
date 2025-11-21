import glob
import os
import shutil
import tkinter as tk
from collections import defaultdict
from tkinter import filedialog, messagebox, ttk
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import urlparse
import re
import threading
from concurrent.futures import ThreadPoolExecutor
import time

########################################
# 🔧 파일명 정제 함수
########################################
def sanitize_filename(filename):
    return re.sub(r'[\\/:*?"<>|]', '', filename)

def get_clean_filename(url, title, idx):
    parsed = urlparse(url)
    base = os.path.basename(parsed.path)
    name, ext = os.path.splitext(base)
    if not ext:
        ext = ".dat"
    name = sanitize_filename(name)
    return f"{title} ({idx}){ext}"

########################################
# Tkinter GUI 설정
########################################
root = tk.Tk()
root.title("HTML 링크 다운로드 프로그램 (멀티스레드 + 재시도 + 퍼센트)")
root.geometry("650x800")

selected_path = ""

########################################
# 폴더 선택 함수
########################################
def choose_folder():
    global selected_path
    selected_path = filedialog.askdirectory(title="HTML 파일이 있는 폴더를 선택하세요")
    if selected_path:
        path_label.config(text=selected_path)

########################################
# 개별 링크 다운로드 (재시도 포함)
########################################
def download_link(src_path, dst_path, clean_filename, idx, total):
    retries = 3
    for attempt in range(1, retries + 1):
        try:
            urllib.request.urlretrieve(src_path, dst_path)
            percent = int((idx / total) * 100)
            root.after(0, lambda: log_listbox.insert(tk.END, f"⬇ {clean_filename} 완료 ({percent}%)"))
            break
        except Exception as e:
            if attempt < retries:
                root.after(0, lambda e=e, a=attempt, f=clean_filename: log_listbox.insert(tk.END, f"⚠ 재시도 {a} 실패: {f} - {e}"))
                time.sleep(0.5)
            else:
                root.after(0, lambda e=e, f=clean_filename: log_listbox.insert(tk.END, f"❌ 다운로드 실패: {f} - {e}"))
    time.sleep(0.5)
    root.after(0, lambda: download_bar.step(1))

########################################
# HTML 처리 함수 (각 HTML 파일)
########################################
def process_single_html(html_file, tag, class_name):
    title = os.path.splitext(os.path.basename(html_file))[0].split(' - ')[0]
    output_dir = os.path.join(selected_path, title)
    os.makedirs(output_dir, exist_ok=True)

    root.after(0, lambda f=html_file: log_listbox.insert(tk.END, f"\n📂 처리 중: {f}"))

    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')

    selector = f"{tag}.{class_name}"
    target_div = soup.select_one(selector)
    links = target_div.find_all('a') if target_div else []
    total_links = len(links)

    root.after(0, lambda: download_bar.config(maximum=max(total_links,1), value=0))
    root.after(0, lambda: log_listbox.insert(tk.END, f"🔗 총 {total_links}개의 링크 발견"))

    # 멀티스레딩 다운로드 (max_workers=3)
    with ThreadPoolExecutor(max_workers=3) as executor:
        for idx, a in enumerate(links, start=1):
            href = a.get('href', '')
            if not href:
                continue
            if href.startswith("http://") or href.startswith("https://"):
                src_path = href
            else:
                src_path = os.path.normpath(os.path.join(os.path.dirname(html_file), href))
            clean_filename = get_clean_filename(src_path, title, idx)
            dst_path = os.path.join(output_dir, clean_filename)
            executor.submit(download_link, src_path, dst_path, clean_filename, idx, total_links)

    # HTML 삭제 옵션
    if delete_html_var.get():
        try:
            os.remove(html_file)
            root.after(0, lambda f=html_file: log_listbox.insert(tk.END, f"🗑 HTML 삭제됨: {f}"))
        except Exception as e:
            root.after(0, lambda f=html_file, e=e: log_listbox.insert(tk.END, f"⚠ HTML 삭제 실패: {f} - {e}"))

########################################
# 전체 HTML 처리 (스레드용)
########################################
def process_html_files():
    if not selected_path:
        root.after(0, lambda: messagebox.showwarning("경고", "먼저 경로를 선택해주세요."))
        return

    tag = tag_entry.get().strip()
    class_name = class_entry.get().strip()
    html_files = glob.glob(os.path.join(selected_path, "*.html"))

    if not html_files:
        root.after(0, lambda: messagebox.showwarning("경고", "HTML 파일이 없습니다."))
        return

    log_listbox.delete(0, tk.END)

    # HTML 처리 진행률
    progress_bar["maximum"] = len(html_files)
    progress_bar["value"] = 0

    for html_file in html_files:
        process_single_html(html_file, tag, class_name)
        root.after(0, lambda: progress_bar.step(1))

    root.after(0, lambda: messagebox.showinfo("완료", "모든 작업이 완료되었습니다."))

########################################
# 스레드 실행
########################################
def start_process():
    thread = threading.Thread(target=process_html_files)
    thread.daemon = True
    thread.start()

########################################
# GUI 구성
########################################
label = tk.Label(root, text="HTML a태그 링크 다운로드 프로그램 (멀티스레드 + 재시도 + 퍼센트)", pady=10)
label.pack()

tk.Button(root, text="폴더 선택", command=choose_folder).pack(pady=5)
path_label = tk.Label(root, text="선택된 경로 없음", fg="blue")
path_label.pack()

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

tk.Button(root, text="작업 시작", command=start_process).pack(pady=10)

delete_html_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="HTML 파일 삭제", variable=delete_html_var).pack()\

tk.Label(root, text="📄 HTML 처리 진행률").pack()
progress_bar = ttk.Progressbar(root, orient="horizontal", length=450, mode="determinate")
progress_bar.pack(pady=5)

tk.Label(root, text="⬇ 다운로드 진행률").pack()
download_bar = ttk.Progressbar(root, orient="horizontal", length=450, mode="determinate")
download_bar.pack(pady=5)

log_frame = tk.LabelFrame(root, text="작업 로그")
log_frame.pack(fill="both", expand=True, padx=10, pady=5)
log_listbox = tk.Listbox(log_frame, height=20)
log_listbox.pack(fill="both", expand=True)

root.mainloop()
