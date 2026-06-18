import streamlit as st
import urllib.parse
import html
import streamlit.components.v1 as components

st.set_page_config(page_title="OSINT Search Launcher", page_icon="🔎", layout="wide")

# -------------------------
# Session state
# -------------------------
if "launch_urls" not in st.session_state:
    st.session_state.launch_urls = []
if "launch_mode" not in st.session_state:
    st.session_state.launch_mode = ""

# -------------------------
# Styling
# -------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #050b18;
        color: #f5f7fa;
    }
    html, body, [class*="css"] {
        color: #f5f7fa;
        font-family: "Segoe UI", sans-serif;
    }
    .block-container {
        max-width: 1120px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .main-title {
        font-size: 2.35rem;
        font-weight: 800;
        color: #f8fbff;
        margin-bottom: 0.15rem;
    }
    .subtitle {
        color: #d7e1ee;
        font-size: 1rem;
        font-style: italic;
        margin-bottom: 1.4rem;
    }
    .helper {
        color: #d3ddea;
        font-size: 0.96rem;
        margin-top: 0.35rem;
        margin-bottom: 1rem;
    }
    .section-card {
        background: #0a1220;
        border: 1px solid #22344f;
        border-radius: 14px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .section-desc {
        color: #d7e1ee;
        font-style: italic;
        font-size: 0.95rem;
        margin-bottom: 0.8rem;
    }
    .query-box {
        background: #08111d;
        border: 1px solid #314158;
        border-radius: 10px;
        padding: 0.72rem 0.85rem;
        color: #edf5ff;
        font-family: Consolas, Monaco, monospace;
        font-size: 0.95rem;
        margin-bottom: 0.2rem;
    }
    
    .divider-box {
        height: 1px;
        background: #2a3442;
        border: none;
        margin: 1.2rem 0;
        width: 100%;
    }

    .note {
        margin-top: 0.8rem;
        color: #d6deea;
        font-style: italic;
        font-size: 0.95rem;
    }
    .launch-card {
        background: #0a1220;
        border: 1px solid #1d4ed8;
        border-radius: 14px;
        padding: 1rem;
        margin-top: 1rem;
    }
    .launch-title {
        font-weight: 700;
        color: #eef5ff;
        margin-bottom: 0.3rem;
    }
    .launch-desc {
        color: #d7e1ee;
        font-size: 0.95rem;
        margin-bottom: 0.75rem;
    }
    div.stButton > button {
        background: #1d4ed8;
        color: white;
        border: 1px solid #2563eb;
        border-radius: 10px;
        padding: 0.65rem 1rem;
        font-weight: 650;
    }
    div.stButton > button:hover {
        background: #2563eb;
        border: 1px solid #3b82f6;
        color: white;
    }
    .stTextInput input {
        background-color: #101924 !important;
        color: #f5f7fa !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
    }
    .stTextInput input:focus {
        border: 1px solid #3b82f6 !important;
        box-shadow: 0 0 0 1px #3b82f6 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Header
# -------------------------
st.markdown('<div class="main-title">🔎 OSINT Search Launcher</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle"><em>Build and launch targeted search queries instantly</em></div>',
    unsafe_allow_html=True,
)

search_term = st.text_input("Search term", placeholder="Enter search term…")
st.markdown(
    '<div class="helper">Type a name, project, phrase, or keyword set. The tool will build Google searches around it.</div>',
    unsafe_allow_html=True,
)

# -------------------------
# Query templates
# -------------------------
DISPLAY_TEMPLATES = {
    "platform": [
        'site:reddit.com "*******"',
        'site:github.com "*******"',
        'site:replit.com "*******"',
        'site:x.com "*******"',
        'site:facebook.com "*******"',
        'site:instagram.com "*******"',
    ],
    "documents": [
        'filetype:pdf "*******"',
        'filetype:xls "*******"',
        'filetype:xlsx "*******"',
    ],
    "leak": [
        '"*******" AND ("leak" OR "unreleased") ⏱ Last 7 days',
    ],
}


def actual_queries(term: str):
    return {
        "platform": [
            (f'site:reddit.com "{term}"', False),
            (f'site:github.com "{term}"', False),
            (f'site:replit.com "{term}"', False),
            (f'site:x.com "{term}"', False),
            (f'site:facebook.com "{term}"', False),
            (f'site:instagram.com "{term}"', False),
        ],
        "documents": [
            (f'filetype:pdf "{term}"', False),
            (f'filetype:xls "{term}"', False),
            (f'filetype:xlsx "{term}"', False),
        ],
        "leak": [
            (f'"{term}" AND ("leak" OR "unreleased")', True),
        ],
    }


def build_google_url(query: str, last_week: bool = False) -> str:
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded}"
    if last_week:
        url += "&tbs=qdr:w"
    return url


# -------------------------
# Copy widget
# -------------------------
def render_copy_button(query_text: str, widget_id: str):
    safe_text = query_text.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    button_html = f"""
    <button
        onclick='navigator.clipboard.writeText(`{safe_text}`); this.innerText="✅"; setTimeout(() => this.innerText="📋", 900);'
        title="Copy query"
        style="
            width:100%;
            background:#09111d;
            color:#9fc4ff;
            border:1px solid #2f528f;
            border-radius:10px;
            padding:0.42rem 0.55rem;
            font-size:1rem;
            cursor:pointer;
        "
        id="{widget_id}"
    >📋</button>
    """
    components.html(button_html, height=42)


# -------------------------
# Section renderer
# -------------------------
def render_section(section_key: str, title: str, description: str, queries, icon: str):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    category_enabled = st.checkbox(f"{icon} {title}", value=True, key=f"cat_{section_key}")
    st.markdown(f'<div class="section-desc"><em>{description}</em></div>', unsafe_allow_html=True)

    row_selected = []
    for idx, query_text in enumerate(queries):
        c1, c2, c3 = st.columns([0.06, 0.84, 0.10])
        with c1:
            checked = st.checkbox(
                "",
                value=True,
                key=f"{section_key}_{idx}",
                label_visibility="collapsed",
            )
            row_selected.append(checked)
        with c2:

            display_text = query_text.replace("*******", search_term or "name")

            st.markdown(
                f'<div class="query-box">{html.escape(display_text)}</div>',
                unsafe_allow_html=True,
            )


        
        with c3:
            cleaned = query_text.replace(" ⏱ Last 7 days", "")
            render_copy_button(cleaned, f"copy_{section_key}_{idx}")
            final_query = cleaned.replace("*******", search_term)
            render_copy_button(final_query, f"copy_{section_key}_{idx}")


    st.markdown('</div>', unsafe_allow_html=True)
    return category_enabled, row_selected


cat_platform, selected_platform = render_section(
    section_key="platform",
    title="Platform Searches",
    description="Searches the platform for uses of the search word",
    queries=DISPLAY_TEMPLATES["platform"],
    icon="📁",
)

st.markdown('<div class="divider-box"></div>', unsafe_allow_html=True)

cat_documents, selected_documents = render_section(
    section_key="documents",
    title="Document Searches",
    description="Searches for instances of the search word in PDFs and Excel files online",
    queries=DISPLAY_TEMPLATES["documents"],
    icon="📄",
)

st.markdown('<div class="divider-box"></div>', unsafe_allow_html=True)

cat_leak, selected_leak = render_section(
    section_key="leak",
    title="Recent Leak Searches",
    description='Searches for the search word and the words "leak" or "unreleased" in the last 7 days',
    queries=DISPLAY_TEMPLATES["leak"],
    icon="⚠️",
)


# -------------------------
# URL collection
# -------------------------
def get_selected_urls(term: str):
    data = actual_queries(term)
    urls = []

    if cat_platform:
        for idx, (query, last_week) in enumerate(data["platform"]):
            if selected_platform[idx]:
                urls.append(build_google_url(query, last_week))

    if cat_documents:
        for idx, (query, last_week) in enumerate(data["documents"]):
            if selected_documents[idx]:
                urls.append(build_google_url(query, last_week))

    if cat_leak:
        for idx, (query, last_week) in enumerate(data["leak"]):
            if selected_leak[idx]:
                urls.append(build_google_url(query, last_week))

    return urls


def get_all_urls(term: str):
    data = actual_queries(term)
    urls = []
    for section in ["platform", "documents", "leak"]:
        for query, last_week in data[section]:
            urls.append(build_google_url(query, last_week))
    return urls


# -------------------------
# Search buttons
# -------------------------
btn1, btn2 = st.columns(2)

with btn1:
    if st.button("✅ Search Selected Queries", use_container_width=True):
        if not search_term.strip():
            st.warning("Enter a search term.")
            st.session_state.launch_urls = []
            st.session_state.launch_mode = ""
        else:
            st.session_state.launch_urls = get_selected_urls(search_term.strip())
            st.session_state.launch_mode = "selected"

with btn2:
    if st.button("🔎 Search All", use_container_width=True):
        if not search_term.strip():
            st.warning("Enter a search term.")
            st.session_state.launch_urls = []
            st.session_state.launch_mode = ""
        else:
            st.session_state.launch_urls = get_all_urls(search_term.strip())
            st.session_state.launch_mode = "all"

st.markdown(
    '<div class="note"><em>Search Selected Queries only launches the categories and queries you have ticked. Search All launches every query in the tool regardless of what is selected.</em></div>',
    unsafe_allow_html=True,
)


# -------------------------
# Launch panel
# -------------------------
if st.session_state.launch_urls:
    count = len(st.session_state.launch_urls)
    label = "selected Google searches" if st.session_state.launch_mode == "selected" else "Google searches"

    st.markdown('<div class="launch-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="launch-title">{count} {label} ready</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="launch-desc">Click the button below to open the search tabs. This second click is required so the browser treats it as a direct user action.</div>',
        unsafe_allow_html=True,
    )



    js_lines = []
    for idx, url in enumerate(st.session_state.launch_urls):
        safe_url = url.replace('"', '\\"')
        js_lines.append(f'''
            setTimeout(function() {{
                var a = document.createElement("a");
                a.href = "{safe_url}";
                a.target = "_blank";
                document.body.appendChild(a);
                a.click();
                a.remove();
            }}, {idx * 600});
        ''')

    js_code = "".join(js_lines)




    launcher_html = f"""
    <button
        onclick='{js_code}'
        style="
            background:#1d4ed8;
            color:white;
            border:1px solid #2563eb;
            border-radius:10px;
            padding:0.75rem 1.1rem;
            font-size:1rem;
            font-weight:700;
            cursor:pointer;
        "
    >
        🔎 Open Web Pages
    </button>
    """
    components.html(launcher_html, height=65)
    st.markdown('</div>', unsafe_allow_html=True)
