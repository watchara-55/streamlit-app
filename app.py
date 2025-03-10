import os
import threading
import functools
import http.server
import socketserver
from werkzeug.utils import secure_filename
import streamlit as st

# 📂 ตั้งค่าโฟลเดอร์หลักและรายการเมนู
UPLOAD_FOLDER = "uploaded_files"
MENU_FOLDERS = {
    "📂 เอกสารอื่นๆ": "เอกสารอื่นๆ",
    "🛠️ วัสดุภายในโครงการ": "วัสดุภายในโครงการ",
    "📤 เอกสารออกนิติ": "เอกสารออกนิติ",
    "📑 แบบ As-Built": "แบบ As-Built"
}

# สร้างโฟลเดอร์สำหรับแต่ละเมนูถ้ายังไม่มี
for folder in MENU_FOLDERS.values():
    os.makedirs(os.path.join(UPLOAD_FOLDER, folder), exist_ok=True)

# 🔹 ตั้งค่าหน้าตา UI ของ Streamlit
st.set_page_config(page_title="โครงการ ศุภาลัย ลอฟท์ ภาษีเจริญ", layout="wide")

# 📌 ตรวจสอบ session_state สำหรับการเข้าถึง Admin
if "admin_access" not in st.session_state:
    st.session_state.admin_access = False

st.sidebar.title("📂 เมนูหลัก")

# 🔐 ช่องใส่รหัสผ่าน Admin (ใช้ ENV var ถ้ามี ตั้งค่า default เป็น "admin123")
password = st.sidebar.text_input("🔑 ใส่รหัสผ่าน Admin", type="password")
if st.sidebar.button("เข้าสู่ระบบ"):
    if password == os.getenv("ADMIN_PASSWORD", "admin123"):
        st.session_state.admin_access = True
        st.sidebar.success("✅ เข้าสู่ระบบสำเร็จ!")
    else:
        st.sidebar.error("❌ รหัสผ่านไม่ถูกต้อง!")

# 📌 เลือกเมนูที่ต้องการแสดงไฟล์
menu = st.sidebar.radio("เลือกเมนู:", list(MENU_FOLDERS.keys()))

# 🔹 ฟังก์ชันเริ่มเซิร์ฟเวอร์สำหรับเสิร์ฟไฟล์จาก UPLOAD_FOLDER ใน background
def start_file_server(port=8502):
    Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=UPLOAD_FOLDER)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
        httpd.serve_forever()# เริ่มเซิร์ฟเวอร์ไฟล์เพียงครั้งเดียว
if "file_server_started" not in st.session_state:
    t = threading.Thread(target=start_file_server, daemon=True)
    t.start()
    st.session_state.file_server_started = True

# 🔹 ฟังก์ชันแสดงรายการไฟล์ในโฟลเดอร์ที่เลือก
def display_files(folder_name):
    st.header(f"📂 {folder_name}")
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    files = os.listdir(folder_path)
    if not files:
        st.warning("⚠️ ไม่มีเอกสารในโฟลเดอร์นี้")
    else:
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            # ใช้เซิร์ฟเวอร์ไฟล์ที่รันอยู่ที่ port 8502
            file_url = f"http://localhost:8502/{folder_name}/{file_name}"
            with st.expander(f"📄 {file_name}"):
                st.markdown(f'<a href="{file_url}" target="_blank">📂 คลิกเพื่อเปิดไฟล์</a>', unsafe_allow_html=True)
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="📥 ดาวน์โหลดไฟล์",
                        data=f,
                        file_name=file_name,
                        key=f"download_{folder_name}_{file_name}"
                    )

# แสดงไฟล์จากเมนูที่เลือก
if menu in MENU_FOLDERS:
    display_files(MENU_FOLDERS[menu])

# 📤 ส่วนอัปโหลดไฟล์ (สำหรับ Admin เท่านั้น)
if st.session_state.admin_access:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📤 อัปโหลดไฟล์")
    upload_folder = MENU_FOLDERS.get(menu)
    if upload_folder:
        upload_path = os.path.join(UPLOAD_FOLDER, upload_folder)
        uploaded_files = st.sidebar.file_uploader(
            "📎 แนบไฟล์เอกสาร", 
            type=["pdf", "docx", "xlsx", "jpg", "png"], 
            accept_multiple_files=True
        )
        if uploaded_files:
            for uploaded_file in uploaded_files:
                # ใช้ secure_filename เพื่อล้างข้อมูลของชื่อไฟล์
                safe_filename = secure_filename(uploaded_file.name)
                file_path = os.path.join(upload_path, safe_filename)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            st.sidebar.success("✅ ไฟล์แนบถูกอัปโหลดเรียบร้อย")
