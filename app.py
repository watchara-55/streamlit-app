import os
import streamlit as st
from werkzeug.utils import secure_filename

# 📂 ตั้งค่าโฟลเดอร์หลักและเมนู
UPLOAD_FOLDER = "uploaded_files"
MENU_FOLDERS = {
    "📂 เอกสารอื่นๆ": "เอกสารอื่นๆ",
    "🛠️ วัสดุภายในโครงการ": "วัสดุภายในโครงการ",
    "📤 เอกสารออกนิติ": "เอกสารออกนิติ",
    "📑 แบบ As-Built": "แบบ As-Built"
}

# สร้างโฟลเดอร์สำหรับเก็บไฟล์
for folder in MENU_FOLDERS.values():
    os.makedirs(os.path.join(UPLOAD_FOLDER, folder), exist_ok=True)

# 🔹 ตั้งค่าหน้าตา UI ของ Streamlit
st.set_page_config(page_title="โครงการ ศุภาลัย ลอฟท์ ภาษีเจริญ", layout="wide")

# 📌 ตรวจสอบ session_state สำหรับ Admin Access
if "admin_access" not in st.session_state:
    st.session_state.admin_access = False

st.sidebar.title("📂 เมนูหลัก")

# 🔐 ช่องใส่รหัสผ่าน Admin
password = st.sidebar.text_input("🔑 ใส่รหัสผ่าน Admin", type="password")
if st.sidebar.button("เข้าสู่ระบบ"):
    if password == "spl123":  # ✅ ใช้รหัสแบบกำหนดเอง
        st.session_state.admin_access = True
        st.sidebar.success("✅ เข้าสู่ระบบสำเร็จ!")
    else:
        st.sidebar.error("❌ รหัสผ่านไม่ถูกต้อง!")

# 📌 เลือกเมนู
menu = st.sidebar.radio("เลือกเมนู:", list(MENU_FOLDERS.keys()))

# 🔹 ฟังก์ชันแสดงรายการไฟล์
def display_files(folder_name):
    st.header(f"📂 {folder_name}")
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
    files = os.listdir(folder_path)

    if not files:
        st.warning("⚠️ ไม่มีเอกสารในโฟลเดอร์นี้")
    else:
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)

            with open(file_path, "rb") as f:
                file_bytes = f.read()

            with st.expander(f"📄 {file_name}"):
                # ✅ ใช้ลิงก์ดาวน์โหลดที่ Streamlit รองรับ
                st.download_button(
                    label="📥 ดาวน์โหลดไฟล์",
                    data=file_bytes,
                    file_name=file_name,
                    key=f"download_{folder_name}_{file_name}"
                )

# แสดงไฟล์จากเมนูที่เลือก
if menu in MENU_FOLDERS:
    display_files(MENU_FOLDERS[menu])

# 📤 ส่วนอัปโหลดไฟล์ (Admin เท่านั้น)
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
                safe_filename = secure_filename(uploaded_file.name)
                file_path = os.path.join(upload_path, safe_filename)

                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            st.sidebar.success("✅ ไฟล์แนบถูกอัปโหลดเรียบร้อย")
