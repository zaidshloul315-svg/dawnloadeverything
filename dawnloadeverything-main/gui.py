import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
from PIL import Image, ImageTk
from io import BytesIO
from downloader import get_video_info, download_media

def create_gui():
    def paste_url():
        try:
            url = root.clipboard_get()
            url_entry.delete(0, tk.END)
            url_entry.insert(0, url)
        except tk.TclError:
            pass

    def fetch_info():
        url = url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL first")
            return
        
        status_label.config(text="Fetching video info...")
        fetch_btn.config(state=tk.DISABLED)
        
        def run():
            try:
                info = get_video_info(url)
                root.after(0, update_ui_with_info, info)
            except Exception as e:
                root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch info: {e}"))
                root.after(0, lambda: status_label.config(text="Error occurred while fetching info."))
            finally:
                root.after(0, lambda: fetch_btn.config(state=tk.NORMAL))

        threading.Thread(target=run, daemon=True).start()

    def update_ui_with_info(info):
        title_label.config(text=info['title'][:60] + "...")
        
        if info['thumbnail']:
            try:
                response = requests.get(info['thumbnail'])
                img_data = Image.open(BytesIO(response.content))
                img_data.thumbnail((300, 300))
                img = ImageTk.PhotoImage(img_data)
                thumb_label.config(image=img)
                thumb_label.image = img
            except:
                pass
                
        resolutions = [f"{res}p" for res in info['resolutions']]
        res_combobox['values'] = resolutions
        if resolutions:
            res_combobox.current(0)
            
        status_label.config(text="Ready to download.")

    def start_download():
        url = url_entry.get().strip()
        format_type = format_var.get()
        quality_str = res_combobox.get().replace('p', '')
        quality = int(quality_str) if quality_str.isdigit() else None
        is_playlist = playlist_var.get()

        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return

        if format_type == 'mp4' and not quality:
            messagebox.showerror("Error", "Please fetch video info and select quality first")
            return

        status_label.config(text="Downloading... Please wait.")
        download_btn.config(state=tk.DISABLED)

        def run():
            try:
                download_media(url, format_type, quality, is_playlist)
                root.after(0, lambda: status_label.config(text="Download completed successfully!"))
                root.after(0, lambda: messagebox.showinfo("Success", "Download completed successfully!"))
            except Exception as e:
                root.after(0, lambda: status_label.config(text="Download failed."))
                root.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                root.after(0, lambda: download_btn.config(state=tk.NORMAL))

        threading.Thread(target=run, daemon=True).start()

    root = tk.Tk()
    root.title("dawnloadeverything")
    root.geometry("550x650")
    root.resizable(False, False)

    frame_top = tk.Frame(root)
    frame_top.pack(pady=15)

    tk.Label(frame_top, text="Video URL:").pack(side=tk.LEFT, padx=5)
    url_entry = tk.Entry(frame_top, width=40)
    url_entry.pack(side=tk.LEFT, padx=5)

    paste_btn = tk.Button(frame_top, text="Paste", command=paste_url)
    paste_btn.pack(side=tk.LEFT, padx=5)

    fetch_btn = tk.Button(frame_top, text="Fetch Info", command=fetch_info)
    fetch_btn.pack(side=tk.LEFT, padx=5)

    thumb_label = tk.Label(root, text="[ Thumbnail will appear here ]")
    thumb_label.pack(pady=10)

    title_label = tk.Label(root, text="", font=("Arial", 10, "bold"))
    title_label.pack(pady=5)

    frame_options = tk.Frame(root)
    frame_options.pack(pady=15)

    tk.Label(frame_options, text="Format:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
    format_var = tk.StringVar(value="mp4")
    tk.Radiobutton(frame_options, text="MP4", variable=format_var, value="mp4").grid(row=0, column=1)
    tk.Radiobutton(frame_options, text="MP3", variable=format_var, value="mp3").grid(row=0, column=2)

    tk.Label(frame_options, text="Quality:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
    res_combobox = ttk.Combobox(frame_options, state="readonly", width=15)
    res_combobox.grid(row=1, column=1, columnspan=2, pady=5, sticky='w')

    playlist_var = tk.BooleanVar()
    tk.Checkbutton(frame_options, text="Download as Playlist", variable=playlist_var).grid(row=2, column=0, columnspan=3, pady=10, sticky='w')

    download_btn = tk.Button(root, text="Download Now", command=start_download, bg="green", fg="white", font=("Arial", 12, "bold"), width=20)
    download_btn.pack(pady=10)

    status_label = tk.Label(root, text="Waiting for URL...", fg="blue")
    status_label.pack(pady=5)

    root.mainloop()