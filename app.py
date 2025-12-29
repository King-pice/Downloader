import streamlit as st
import yt_dlp
import os
import time

# Konfigurasi Halaman
st.set_page_config(
    page_title="Public Video Downloader",
    page_icon="🚀",
    layout="wide" # Layout lebar agar lebih enak dilihat
)

# Judul
st.title("🚀 Universal Video Downloader")
st.markdown("Aplikasi downloader publik yang berjalan di cloud. Support YouTube, TikTok, IG, dll.")

# Buat folder downloads jika belum ada
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# --- BAGIAN INPUT ---
url_input = st.text_input("Masukkan URL Video:", placeholder="https://www.youtube.com/watch?v=...")

# --- BAGIAN PROSES ---
if st.button("🔍 Cek Video", use_container_width=True):
    if url_input:
        with st.spinner("Menganalisis video..."):
            try:
                ydl_opts_info = {
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                    info = ydl.extract_info(url_input, download=False)
                    
                    # Simpan info ke session_state agar tidak hilang saat interaksi
                    st.session_state['info'] = info
                    st.session_state['url'] = url_input
                    
            except Exception as e:
                st.error(f"Gagal mengambil info: {e}")
                st.stop()
    else:
        st.warning("URL tidak boleh kosong!")

# --- BAGIAN TAMPILAN INFO & DOWNLOAD ---
if 'info' in st.session_state:
    info = st.session_state['info']
    url = st.session_state['url']
    
    # Tampilkan Thumbnail & Judul
    col1, col2 = st.columns([1, 3])
    with col1:
        if 'thumbnail' in info:
            st.image(info['thumbnail'], width=200)
    
    with col2:
        st.subheader(info.get('title', 'Tidak ada judul'))
        st.write(f"**Penonton:** {info.get('view_count', 0):,} | **Durasi:** {info.get('duration_string', 'N/A')}")
    
    st.divider()
    
    # Proses Format
    formats = info.get('formats', [])
    
    # Ambil hanya format video
    video_formats = [f for f in formats if f.get('vcodec') != 'none']
    # Urutkan dari resolusi tertinggi
    video_formats.sort(key=lambda f: (-f.get('height', 0), f.get('ext') != 'mp4'))
    
    # Filter Agar List Tidak Terlalu Panjang (Ambil unik resolusi + ext)
    choices = []
    seen = set()
    for f in video_formats:
        h = f.get('height', 0)
        ext = f.get('ext')
        fid = f['format_id']
        label = f"{h}p ({ext})" if h else f"{ext}"
        
        key = (h, ext)
        if key not in seen:
            seen.add(key)
            choices.append((fid, label))
            
    # Tambahkan opsi Audio
    choices.append(('bestaudio/best', '🎵 Audio Only (MP3)'))
    
    # Dropdown Pilihan
    selected_choice = st.selectbox("Pilih Kualitas:", choices, format_func=lambda x: x[1])
    format_id = selected_choice[0]
    
    # Tombol Download
    if st.button("⬇️ Download Sekarang", use_container_width=True, type="primary"):
        with st.spinner(f"Sedang mendownload {selected_choice[1]}..."):
            try:
                out_tmpl = os.path.join("downloads", "%(title)s.%(ext)s")
                
                ydl_opts = {
                    'format': format_id,
                    'outtmpl': out_tmpl,
                    'quiet': True,
                    'no_warnings': True,
                    'noplaylist': True,
                }
                
                # Jika pilih audio, tambahkan postprocessor
                if format_id == 'bestaudio/best':
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                else:
                    ydl_opts['merge_output_format'] = 'mp4'

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # Cari file terbaru di folder downloads
                files = sorted(
                    [os.path.join("downloads", f) for f in os.listdir("downloads")],
                    key=os.path.getmtime
                )
                file_path = files[-1]
                
                st.success("✅ Download Selesai di Server!")
                
                # Tombol untuk user menyimpan file ke HP/Komputer
                with open(file_path, "rb") as file:
                    st.download_button(
                        label="📥 Simpan File ke Perangkat Anda",
                        data=file,
                        file_name=os.path.basename(file_path),
                        mime="application/octet-stream"
                    )
                    
            except Exception as e:
                st.error(f"❌ Gagal download: {e}")
