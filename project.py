import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------- setup
ROOT = Path("workspace").resolve()   # everything happens inside this folder
ROOT.mkdir(exist_ok=True)

st.set_page_config(page_title="File Manager", page_icon="🗂️", layout="wide")

st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; max-width: 1100px;}
    div[data-testid="stMetric"] {
        background: rgba(128,128,128,0.08);
        border: 1px solid rgba(128,128,128,0.2);
        padding: 14px 18px; border-radius: 12px;
    }
    .stButton > button {border-radius: 8px;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- helpers
def safe_path(rel: str) -> Path:
    """Resolve a path and make sure it stays inside the workspace."""
    p = (ROOT / rel).resolve()
    if p != ROOT and ROOT not in p.parents:
        raise ValueError("Path is outside the workspace.")
    return p


def rel(p: Path) -> str:
    r = p.relative_to(ROOT).as_posix()
    return r if r != "." else "."


def all_folders():
    return sorted(rel(p) for p in ROOT.rglob("*") if p.is_dir())


def all_files():
    return sorted(rel(p) for p in ROOT.rglob("*") if p.is_file())


def human_size(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def valid_name(name: str) -> bool:
    name = name.strip()
    return bool(name) and "/" not in name and "\\" not in name and name not in (".", "..")


def flash(msg: str, icon: str = "✅"):
    st.session_state.setdefault("flash", []).append((msg, icon))


def folder_label(x: str) -> str:
    return "📁 (workspace root)" if x == "." else f"📁 {x}"


def file_label(x: str) -> str:
    return f"📄 {x}"


# show queued toasts from the previous action
for msg, icon in st.session_state.pop("flash", []):
    st.toast(msg, icon=icon)

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.title("🗂️ File Manager")
    st.caption("Create, read, update and delete folders & files.")
    page = st.radio(
        "Navigate",
        ["🏠 Explorer", "📁 Folders", "📄 Files"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption(f"Working in:\n`{ROOT}`")
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# ================================================================ EXPLORER
if page == "🏠 Explorer":
    st.header("Explorer")
    folders, files = all_folders(), all_files()
    total = sum(safe_path(f).stat().st_size for f in files)

    c1, c2, c3 = st.columns(3)
    c1.metric("Folders", len(folders))
    c2.metric("Files", len(files))
    c3.metric("Total size", human_size(total))

    st.write("")
    f1, f2 = st.columns([3, 1])
    query = f1.text_input("🔍 Search", placeholder="Type to filter by name…")
    kind = f2.selectbox("Show", ["All", "Folders", "Files"])

    rows = []
    for p in sorted(ROOT.rglob("*")):
        is_dir = p.is_dir()
        rows.append(
            {
                "Name": rel(p),
                "Type": "📁 Folder" if is_dir else "📄 File",
                "Size": "—" if is_dir else human_size(p.stat().st_size),
                "Modified": datetime.fromtimestamp(p.stat().st_mtime).strftime("%d %b %Y, %H:%M"),
            }
        )
    df = pd.DataFrame(rows, columns=["Name", "Type", "Size", "Modified"])

    if not df.empty:
        if query:
            df = df[df["Name"].str.contains(query, case=False, regex=False)]
        if kind == "Folders":
            df = df[df["Type"].str.contains("Folder")]
        elif kind == "Files":
            df = df[df["Type"].str.contains("File")]

    if df.empty:
        st.info("Nothing here yet. Create a folder or a file from the sidebar.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

# ================================================================ FOLDERS
elif page == "📁 Folders":
    st.header("Folders")
    t_create, t_rename, t_delete = st.tabs(["➕ Create", "✏️ Rename", "🗑️ Delete"])

    # ---- create
    with t_create:
        with st.form("create_folder", clear_on_submit=True):
            parent = st.selectbox("Parent folder", ["."] + all_folders(), format_func=folder_label)
            name = st.text_input("Folder name", placeholder="e.g. projects")
            go = st.form_submit_button("Create folder", type="primary")
        if go:
            if not valid_name(name):
                st.error("Enter a valid name (no slashes).")
            else:
                p = safe_path(f"{parent}/{name.strip()}")
                if p.exists():
                    st.error("A folder or file with that name already exists.")
                else:
                    p.mkdir()
                    flash(f"Folder '{name.strip()}' created")
                    st.rerun()

    # ---- rename
    with t_rename:
        folders = all_folders()
        if not folders:
            st.info("No folders to rename.")
        else:
            with st.form("rename_folder"):
                old = st.selectbox("Folder", folders, format_func=folder_label)
                new = st.text_input("New name")
                go = st.form_submit_button("Rename", type="primary")
            if go:
                if not valid_name(new):
                    st.error("Enter a valid new name.")
                else:
                    old_p = safe_path(old)
                    new_p = old_p.parent / new.strip()
                    if new_p.exists():
                        st.error("That name is already taken.")
                    else:
                        old_p.rename(new_p)
                        flash("Folder renamed")
                        st.rerun()

    # ---- delete
    with t_delete:
        folders = all_folders()
        if not folders:
            st.info("No folders to delete.")
        else:
            target = st.selectbox("Folder to delete", folders, format_func=folder_label, key="del_folder")
            p = safe_path(target)
            contents = list(p.rglob("*"))
            confirmed = True
            if contents:
                st.warning(f"This folder contains {len(contents)} item(s). They will be deleted too.")
                confirmed = st.checkbox("Yes, delete the folder and everything inside it")
            if st.button("Delete folder", type="primary", disabled=not confirmed):
                shutil.rmtree(p)
                flash("Folder deleted", "🗑️")
                st.rerun()

# ================================================================ FILES
else:
    st.header("Files")
    t_create, t_read, t_update, t_delete = st.tabs(
        ["➕ Create", "👁️ Read", "✏️ Update", "🗑️ Delete"]
    )

    # ---- create
    with t_create:
        with st.form("create_file", clear_on_submit=True):
            c1, c2 = st.columns([1, 1])
            folder = c1.selectbox("Folder", ["."] + all_folders(), format_func=folder_label)
            name = c2.text_input("File name with extension", placeholder="notes.txt")
            content = st.text_area("Content", height=200)
            go = st.form_submit_button("Create file", type="primary")
        if go:
            if not valid_name(name):
                st.error("Enter a valid file name (no slashes).")
            else:
                p = safe_path(f"{folder}/{name.strip()}")
                if p.exists():
                    st.error("A file with that name already exists.")
                else:
                    p.write_text(content, encoding="utf-8")
                    flash(f"File '{name.strip()}' created")
                    st.rerun()

        st.divider()
        uploads = st.file_uploader("…or upload files into the workspace", accept_multiple_files=True)
        if uploads and st.button("Save uploads"):
            for up in uploads:
                safe_path(up.name).write_bytes(up.getbuffer())
            flash(f"{len(uploads)} file(s) uploaded", "📤")
            st.rerun()

    # ---- read
    with t_read:
        files = all_files()
        if not files:
            st.info("No files yet.")
        else:
            target = st.selectbox("Choose a file", files, format_func=file_label, key="read_file")
            p = safe_path(target)
            st.caption(
                f"{human_size(p.stat().st_size)} · modified "
                f"{datetime.fromtimestamp(p.stat().st_mtime):%d %b %Y, %H:%M}"
            )
            try:
                text = p.read_text(encoding="utf-8")
                st.code(text or "(empty file)", language=p.suffix.lstrip(".") or None, line_numbers=True)
            except UnicodeDecodeError:
                st.warning("This looks like a binary file, so it can't be previewed.")
            st.download_button("⬇️ Download", p.read_bytes(), file_name=p.name)

    # ---- update
    with t_update:
        files = all_files()
        if not files:
            st.info("No files yet.")
        else:
            target = st.selectbox("File to update", files, format_func=file_label, key="upd_file")
            p = safe_path(target)
            action = st.radio(
                "What do you want to do?",
                ["Rename", "Overwrite content", "Append content"],
                horizontal=True,
            )

            if action == "Rename":
                new = st.text_input("New name with extension", value=p.name)
                if st.button("Rename file", type="primary"):
                    if not valid_name(new):
                        st.error("Enter a valid name.")
                    elif (p.parent / new.strip()).exists():
                        st.error("That name is already taken.")
                    else:
                        p.rename(p.parent / new.strip())
                        flash("File renamed")
                        st.rerun()

            elif action == "Overwrite content":
                try:
                    current = p.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    current = None
                if current is None:
                    st.warning("Binary file – can't be edited as text.")
                else:
                    data = st.text_area("Content", value=current, height=250, key=f"ow_{target}")
                    if st.button("Save changes", type="primary"):
                        p.write_text(data, encoding="utf-8")
                        flash("File overwritten")
                        st.rerun()

            else:  # append
                data = st.text_area("Text to append", height=150, key=f"ap_{target}")
                if st.button("Append", type="primary"):
                    with open(p, "a", encoding="utf-8") as fs:
                        fs.write(data)
                    flash("Content appended")
                    st.rerun()

    # ---- delete
    with t_delete:
        files = all_files()
        if not files:
            st.info("No files yet.")
        else:
            target = st.selectbox("File to delete", files, format_func=file_label, key="del_file")
            ok = st.checkbox("I'm sure I want to delete this file")
            if st.button("Delete file", type="primary", disabled=not ok):
                safe_path(target).unlink()
                flash("File deleted", "🗑️")
                st.rerun()