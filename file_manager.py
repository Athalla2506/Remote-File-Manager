import streamlit as st
import paramiko
import os

# Fungsi untuk koneksi ke server
def connect_to_server(host, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=username, password=password)
        sftp = client.open_sftp()
        return client, sftp
    except Exception as e:
        st.error(f"Error: {e}")
        return None, None

# Fungsi untuk mengunggah file
def upload_file(sftp, file):
    try:
        # Simpan file sementara di sistem lokal
        with open(file.name, "wb") as f:
            f.write(file.getbuffer())

        # Upload ke server
        remote_path = f"/home/{file.name}"  # Sesuaikan path tujuan
        sftp.put(file.name, remote_path)

        # Hapus file sementara setelah upload
        os.remove(file.name)

        st.success(f"✅ File {file.name} berhasil diunggah ke {remote_path}!")
    except Exception as e:
        st.error(f"❌ Error: {e}")


# Fungsi untuk menampilkan daftar file di server
def list_files(sftp):
    try:
        return sftp.listdir("/home/")
    except Exception as e:
        st.error(f"Error: {e}")
        return []

import os

# Fungsi untuk mengunduh file
def download_file(sftp, filename):
    try:
        # Pastikan folder 'downloads/' ada
        download_folder = "downloads"
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)  # Buat folder jika belum ada

        local_path = os.path.join(download_folder, filename)  # Path lengkap file
        sftp.get(f"/home/{filename}", local_path)  # Unduh file dari server

        st.download_button("⬇ Klik untuk Unduh", local_path, file_name=filename)  # Tombol unduh
        ##st.success(f"✅ File {filename} berhasil diunduh!")

    except Exception as e:
        st.error(f"❌ Error: {e}")


# Streamlit UI
st.set_page_config(page_title="File Manager", page_icon="📂")
st.title("📂 Remote File Manager")

# Sidebar untuk login
st.sidebar.header("🔑 Koneksi ke Server")
host = st.sidebar.text_input("Host", "")
username = st.sidebar.text_input("Username", "")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Hubungkan"):
    client, sftp = connect_to_server(host, username, password)
    if sftp:
        st.session_state["sftp"] = sftp
        st.sidebar.success("✅ Koneksi berhasil!")

# Jika terhubung, tampilkan fitur
if "sftp" in st.session_state:
    sftp = st.session_state["sftp"]

    # Upload File
    uploaded_file = st.file_uploader("📤 Pilih file untuk di-upload")
    if uploaded_file and st.button("Upload"):
        upload_file(sftp, uploaded_file)

    # Menampilkan daftar file di server
    files = list_files(sftp)
    if files:
        st.write("📄 *Daftar file di server:*")
        selected_file = st.selectbox("Pilih file untuk diunduh atau dihapus", files)

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("⬇ Download"):
                download_file(sftp, selected_file)
        with col5:
            if st.button("🗑 Hapus"):
                try:
                    sftp.remove(f"/home/{selected_file}")
                    st.success(f"File {selected_file} berhasil dihapus!")
                except Exception as e:
                    st.error(f"Error: {e}")