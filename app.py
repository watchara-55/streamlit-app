import os
import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename

# 📂 ตั้งค่าโฟลเดอร์หลักและหมวดหมู่เอกสาร
UPLOAD_FOLDER = "uploaded_files"
MENU_FOLDERS = {
    "📂 เอกสารอื่น": "เอกสารอื่นๆ",
    "🛠️ วัสดุภายในโครงการ": "วัสดุภายในโครงการ",
    "📤 เอกสารออกนิติ": "เอกสารออกนิติ",
    "📑 แบบ As-Built": "แบบ As-Built"
}

# สร้างโฟลเดอร์หากยังไม่มี
for folder in MENU_FOLDERS.values():
    os.makedirs(os.path.join(UPLOAD_FOLDER, folder), exist_ok=True)

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="โครงการ ศุภาลัย ลอฟท์ ภาษีเจริญ", layout="wide")
st.sidebar.title("📂 เมนูหลัก")

# 📌 ตรวจสอบ session_state สำหรับ Admin
if "admin_access" not in st.session_state:
    st.session_state.admin_access = False

# 🔐 ระบบล็อกอิน Admin
password = st.sidebar.text_input("🔑 ใส่รหัสผ่าน Admin", type="password")
if st.sidebar.button("เข้าสู่ระบบ"):
    if password == os.getenv("ADMIN_PASSWORD", "1234"):
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

    # 🚀 **ซ่อนไฟล์ .xlsx ไม่ให้แสดงในหน้าเว็บ**
    visible_files = [file for file in files if not file.endswith(".xlsx")]

    if not visible_files:
        st.warning("")
    else:
        for file_name in sorted(visible_files, reverse=True):
            file_path = os.path.join(folder_path, file_name)
            with st.expander(f"📄 {file_name}"):
                with open(file_path, "rb") as f:
                    st.download_button("📥 ดาวน์โหลดไฟล์", f, file_name=file_name)

                # 🗑️ ปุ่มลบไฟล์ (เฉพาะ Admin)
                if st.session_state.admin_access:
                    if st.button(f"🗑️ ลบ {file_name}", key=f"delete_{file_name}"):
                        os.remove(file_path)
                        st.success(f"❌ ลบไฟล์ {file_name} สำเร็จ!")
                        st.experimental_rerun()

# 📂 อัปโหลดไฟล์ (เฉพาะ Admin)
if st.session_state.admin_access:
    st.sidebar.subheader("📤 อัปโหลดไฟล์")
    upload_folder = MENU_FOLDERS.get(menu)

    if upload_folder:
        uploaded_files = st.sidebar.file_uploader(
            "📎 แนบไฟล์เอกสาร", 
            type=["pdf", "docx", "xlsx", "jpg", "png", "csv"], 
            accept_multiple_files=True
        )

        if uploaded_files:
            for uploaded_file in uploaded_files:
                timestamp = int(time.time())  # ป้องกันชื่อไฟล์ซ้ำ
                safe_filename = f"{timestamp}_{secure_filename(uploaded_file.name)}"
                file_path = os.path.join(UPLOAD_FOLDER, upload_folder, safe_filename)
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            st.sidebar.success("✅ อัปโหลดไฟล์สำเร็จ!")
            st.experimental_rerun()

# 📌 แสดงรายการไฟล์ของหมวดที่เลือก
if menu in MENU_FOLDERS:
    display_files(MENU_FOLDERS[menu])

# 🔹 แสดงรายการวัสดุในโครงการ (ถ้าเลือกหมวดวัสดุภายในโครงการ)
if menu == "🛠️ วัสดุภายในโครงการ":
    st.subheader("📋 รายการวัสดุภายในโครงการ")

    # **ซ่อนปุ่มอัปโหลดจากผู้ใช้ทั่วไป**
    if st.session_state.admin_access:
        uploaded_file = st.file_uploader("📂 อัปโหลดไฟล์ Excel หรือ CSV", type=["csv", "xlsx"])
        if uploaded_file:
            timestamp = int(time.time())
            file_name = f"{timestamp}_{uploaded_file.name}"
            file_path = os.path.join(UPLOAD_FOLDER, "วัสดุภายในโครงการ", file_name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ อัปโหลดไฟล์ {uploaded_file.name} สำเร็จ!")

    # 📌 แสดงไฟล์วัสดุที่มีอยู่
    materials_files = os.listdir(os.path.join(UPLOAD_FOLDER, "วัสดุภายในโครงการ"))
    if materials_files:
        selected_material_file = st.selectbox("📄 เลือกไฟล์วัสดุ", materials_files)
        material_file_path = os.path.join(UPLOAD_FOLDER, "วัสดุภายในโครงการ", selected_material_file)

        if selected_material_file.endswith(".csv"):
            df = pd.read_csv(material_file_path)
        else:
            df = pd.read_excel(material_file_path, engine="openpyxl")

        # 🔎 ตัวกรองวัสดุขั้นสูง
        col1, col2 = st.columns(2)
        with col1:
            search_material = st.text_input("🔎 ค้นหาชื่อวัสดุ")
        with col2:
            search_location = st.text_input("📍 ค้นหาตามตำแหน่งที่ใช้")

        filtered_df = df[
            df["ชื่อวัสดุ"].astype(str).str.contains(search_material, case=False, na=False) &
            df["ตำแหน่งที่ใช้"].astype(str).str.contains(search_location, case=False, na=False)
        ] if search_material or search_location else df

        st.write("**📊 ข้อมูลวัสดุ:**")
        st.dataframe(filtered_df, use_container_width=True)

        # 🛠️ แก้ไขข้อมูลวัสดุ
        if st.session_state.admin_access:
            st.subheader("✏️ แก้ไขข้อมูลวัสดุ")
            edited_df = st.data_editor_data(filtered_df)
            save_button = st.button("💾 บันทึกการเปลี่ยนแปลง")
            if save_button:
                edited_df.to_csv(material_file_path, index=False)
                st.success("✅ บันทึกข้อมูลสำเร็จ!")


        # 📥 ปุ่มดาวน์โหลดข้อมูลที่ค้นหา
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 ดาวน์โหลดข้อมูลที่ค้นหา", csv, "filtered_material_list.csv", "text/csv")

