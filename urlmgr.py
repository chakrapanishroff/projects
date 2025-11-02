import streamlit as st
import sqlite3
import os

DB_FILE = "urls.db"

# --- Initialize SQLite DB ---
if not os.path.exists(DB_FILE):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# --- Helper Functions ---
def get_urls():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, title, url FROM urls")
    rows = c.fetchall()
    conn.close()
    return rows

def add_url(title, url):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO urls (title, url) VALUES (?, ?)", (title, url))
    conn.commit()
    conn.close()

def update_url(url_id, title, url):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE urls SET title=?, url=? WHERE id=?", (title, url, url_id))
    conn.commit()
    conn.close()

def delete_url(url_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM urls WHERE id=?", (url_id,))
    conn.commit()
    conn.close()

# --- Streamlit UI ---
st.set_page_config(page_title="URL Manager", page_icon="🔗", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.markdown("""
<style>
h1, h2 { text-align: center; color: #1e90ff; }
button { border-radius: 6px !important; }
</style>
""", unsafe_allow_html=True)

# --- Login Page ---
if not st.session_state.logged_in:
    st.title("🔒 URL Manager Login")

    with st.form("login_form", clear_on_submit=False):
        userid = st.text_input("User ID")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if userid == "admin" and password == "admin":
                st.session_state.logged_in = True
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials. Try again.")

# --- Main Page ---
else:
    st.title("🔗 URL Manager")
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/609/609803.png", width=100)
    st.sidebar.success("Logged in as: admin")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.subheader("➕ Add New URL")
    with st.form("add_url_form"):
        title = st.text_input("Enter Title")
        url = st.text_input("Enter URL (include https://)")
        add_submit = st.form_submit_button("Add URL")
        if add_submit and title and url:
            add_url(title, url)
            st.success("✅ URL added successfully!")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 Manage URLs")

    urls = get_urls()
    if not urls:
        st.info("No URLs found. Add one above.")
    else:
        for url_id, title, url in urls:
            with st.expander(f"🔹 {title}", expanded=False):
                new_title = st.text_input(f"Edit Title (ID {url_id})", title, key=f"title_{url_id}")
                new_url = st.text_input(f"Edit URL (ID {url_id})", url, key=f"url_{url_id}")
                col1, col2, col3 = st.columns([1,1,1])
                with col1:
                    if st.button("💾 Update", key=f"update_{url_id}"):
                        update_url(url_id, new_title, new_url)
                        st.success("✅ Updated successfully!")
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{url_id}"):
                        delete_url(url_id)
                        st.warning("❌ Deleted!")
                        st.rerun()
                with col3:
                    st.link_button("🌐 Open", new_url)

