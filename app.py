import html
import streamlit as st
from librarian import process_url, search_index, load_index, delete_entry, update_entry, entry_category

st.set_page_config(
    page_title="Knowledge Librarian",
    page_icon="📚",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

    /* ── Base ───────────────────────────────────────────── */
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .main, .stApp { background-color: #111111; }
    h1, h2, h3 { font-family: 'DM Serif Display', serif; color: #ede9df; }

    /* ── Hero ───────────────────────────────────────────── */
    .hero-title {
        font-family: 'DM Serif Display', serif;
        font-size: 2.8rem;
        color: #ede9df;
        line-height: 1.1;
        margin-bottom: 0.25rem;
    }
    .hero-sub {
        font-family: 'DM Mono', monospace;
        font-size: 0.7rem;
        color: #484440;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }

    /* ── Section labels ─────────────────────────────────── */
    .section-label {
        font-family: 'DM Mono', monospace;
        font-size: 0.7rem;
        color: #5a5650;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        margin: 0 0 1.25rem 0;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid #1e1e1e;
    }

    /* ── Stats ──────────────────────────────────────────── */
    .stat-box {
        background: #161616;
        border: 1px solid #1e1e1e;
        border-radius: 6px;
        padding: 0.9rem 1rem;
        text-align: center;
    }
    .stat-num {
        font-family: 'DM Serif Display', serif;
        font-size: 1.75rem;
        color: #c9a96e;
        line-height: 1.2;
    }
    .stat-label {
        font-family: 'DM Mono', monospace;
        font-size: 0.65rem;
        color: #484440;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.15rem;
    }

    /* ── Cards ──────────────────────────────────────────── */
    .card {
        background: #181818;
        border: 1px solid #222222;
        border-radius: 8px;
        padding: 1.1rem 1.25rem;
        margin-bottom: 0.75rem;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    .card:hover {
        border-color: #3a3530;
        box-shadow: 0 2px 12px rgba(0,0,0,0.4);
    }
    .card-title {
        font-family: 'DM Serif Display', serif;
        font-size: 1rem;
        color: #ede9df;
        margin-bottom: 0.35rem;
        line-height: 1.4;
    }
    .card-summary {
        font-size: 0.875rem;
        color: #7a7672;
        line-height: 1.7;
        margin-bottom: 0.65rem;
    }
    .card-meta {
        font-family: 'DM Mono', monospace;
        font-size: 0.68rem;
        color: #484440;
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        margin-top: 0.6rem;
        padding-top: 0.6rem;
        border-top: 1px solid #1e1e1e;
    }
    .card-meta-left {
        display: flex;
        gap: 0.75rem;
        align-items: center;
        flex-wrap: wrap;
    }
    .breadcrumb { color: #484440; }

    /* ── Tags & badges ──────────────────────────────────── */
    .tag {
        border: 1px solid #282420;
        border-radius: 3px;
        padding: 1px 6px;
        font-family: 'DM Mono', monospace;
        font-size: 0.68rem;
        color: #8a7a5a;
    }
    .source-badge {
        font-family: 'DM Mono', monospace;
        font-size: 0.65rem;
        padding: 1px 6px;
        border-radius: 3px;
        font-weight: 500;
        letter-spacing: 0.03em;
    }
    .source-youtube { color: #904040; border: 1px solid #2a1414; }
    .source-kaggle  { color: #407a7a; border: 1px solid #14282a; }
    .source-web     { color: #407050; border: 1px solid #142218; }
    .collection-badge {
        border: 1px solid #1a2a40;
        border-radius: 3px;
        padding: 1px 6px;
        font-family: 'DM Mono', monospace;
        font-size: 0.68rem;
        color: #3a5a7a;
    }

    /* ── Expanders ──────────────────────────────────────── */
    [data-testid="stExpander"] {
        border: 1px solid #1e1e1e !important;
        border-radius: 6px !important;
        margin-bottom: 0.35rem !important;
        overflow: hidden !important;
    }
    [data-testid="stExpander"] details summary {
        font-family: 'DM Mono', monospace !important;
        font-size: 0.72rem !important;
        color: #6a6460 !important;
        letter-spacing: 0.06em !important;
        padding: 0.65rem 0.9rem !important;
        user-select: none !important;
    }
    [data-testid="stExpander"] details summary:hover {
        color: #c8c3b8 !important;
        background: #161616 !important;
    }
    [data-testid="stExpander"] details[open] summary {
        border-bottom: 1px solid #1e1e1e !important;
        color: #a8a49c !important;
    }

    /* ── Inputs ─────────────────────────────────────────── */
    .stTextInput > div > div > input {
        background: #161616 !important;
        border: 1px solid #222 !important;
        color: #ede9df !important;
        border-radius: 6px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.875rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #7a6040 !important;
        box-shadow: 0 0 0 1px #7a604018 !important;
    }
    input::placeholder { color: #333 !important; }
    label, [data-testid="stWidgetLabel"] p {
        color: #5a5650 !important;
        font-size: 0.75rem !important;
        font-family: 'DM Mono', monospace !important;
    }

    /* ── Selectboxes ────────────────────────────────────── */
    [data-baseweb="select"] > div {
        background-color: #161616 !important;
        border-color: #222 !important;
        color: #ede9df !important;
        border-radius: 6px !important;
    }
    [data-baseweb="select"] [data-baseweb="tag"] { color: #ede9df !important; }
    [data-baseweb="select"] span { color: #ede9df !important; }
    [data-baseweb="popover"] > div { background-color: #1a1a1a !important; }
    [role="listbox"]               { background-color: #1a1a1a !important; }
    [data-baseweb="option"] {
        background-color: #1a1a1a !important;
        color: #a8a49c !important;
        font-size: 0.875rem !important;
    }
    [data-baseweb="option"]:hover,
    [data-baseweb="option"][aria-selected="true"] {
        background-color: #202020 !important;
        color: #ede9df !important;
    }
    .stSelectbox > div > div {
        background: #161616 !important;
        border-color: #222 !important;
        color: #ede9df !important;
    }

    /* ── Buttons ────────────────────────────────────────── */
    [data-testid="baseButton-secondary"] {
        background: #161616 !important;
        border: 1px solid #242424 !important;
        color: #5a5650 !important;
        padding: 3px 10px !important;
        font-size: 0.7rem !important;
        font-family: 'DM Mono', monospace !important;
        border-radius: 4px !important;
        line-height: 1.5 !important;
        transition: border-color 0.15s, color 0.15s !important;
    }
    [data-testid="baseButton-secondary"]:hover {
        border-color: #484440 !important;
        color: #a8a49c !important;
    }
    .stButton > button[kind='secondary'] {
        background: #161616 !important;
        color: #8a8680 !important;
        border: 1px solid #242424 !important;
        border-radius: 6px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.875rem !important;
        font-weight: 400 !important;
        transition: border-color 0.15s, color 0.15s !important;
    }
    .stButton > button[kind='secondary']:hover {
        background: #1a1a1a !important;
        border-color: #484440 !important;
        color: #c8c3b8 !important;
    }
    [data-testid="baseButton-primary"] {
        background: #1a0f0f !important;
        color: #904040 !important;
        border: 1px solid #2a1414 !important;
        border-radius: 6px !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 0.7rem !important;
        font-weight: 400 !important;
        transition: border-color 0.15s, color 0.15s !important;
    }
    [data-testid="baseButton-primary"]:hover {
        border-color: #904040 !important;
        color: #c05050 !important;
    }

    /* ── Messages ───────────────────────────────────────── */
    .success-msg {
        background: #0d140d;
        border: 1px solid #1a321a;
        border-radius: 6px;
        padding: 0.65rem 0.9rem;
        color: #4a8a4a;
        font-family: 'DM Mono', monospace;
        font-size: 0.75rem;
    }
    .error-msg {
        background: #140d0d;
        border: 1px solid #321a1a;
        border-radius: 6px;
        padding: 0.65rem 0.9rem;
        color: #904040;
        font-family: 'DM Mono', monospace;
        font-size: 0.75rem;
    }

    /* ── Misc ───────────────────────────────────────────── */
    .divider { border: none; border-top: 1px solid #191919; margin: 2rem 0; }
    a { color: #c9a96e !important; text-decoration: none; }
    a:hover { color: #c9a96e !important; text-decoration: underline; }
</style>
""", unsafe_allow_html=True)


def source_badge(source_type):
    cls = f"source-{source_type.lower()}"
    return f'<span class="source-badge {cls}">{source_type.upper()}</span>'


def render_card(entry):
    # Escape everything that lands in an HTML text node or attribute value.
    # quote=True also escapes " so no URL can break out of href="...".
    url        = html.escape(entry.get("url", "#"), quote=True)
    title      = html.escape(entry.get("title", ""))
    summary    = html.escape(entry.get("summary", ""))
    date_str   = html.escape(entry.get("date_saved", "")[:10])
    breadcrumb = html.escape(" \u203a ".join(filter(None, [
        entry_category(entry),
        entry.get("subcategory", ""),
        entry.get("topic", ""),
    ])))

    tags_html = " ".join(
        f'<span class="tag">{html.escape(t)}</span>'
        for t in entry.get("tags", [])
    )
    badge = source_badge(entry.get("source_type", "web"))
    collection = entry.get("collection", "")
    collection_html = (
        f'<span class="collection-badge">{html.escape(collection)}</span>'
        if collection else ""
    )

    entry_id = entry.get("id", "")

    # Div audit — 6 opens, 6 closes:
    #   1: div.card  2: div.card-title/2  3: div.card-summary/3
    #   4: div[tags]/4  5: div.card-meta  6: div.card-meta-left/6  /5  /1
    card_html = (
        '<div class="card">'
            '<div class="card-title">'
                f'<a href="{url}" target="_blank">{title}</a>'
            '</div>'
            f'<div class="card-summary">{summary}</div>'
            f'<div style="margin-bottom:0.5rem">{tags_html}</div>'
            '<div class="card-meta">'
                '<div class="card-meta-left">'
                    f'{badge}'
                    f'<span class="breadcrumb">{breadcrumb}</span>'
                    f'{collection_html}'
                    f'<span>{date_str}</span>'
                '</div>'
            '</div>'
        '</div>'
    )

    st.markdown(card_html, unsafe_allow_html=True)

    is_editing = st.session_state.get(f"editing_{entry_id}", False)
    gear_col, c1, c2, c3, c4, c5 = st.columns([1, 4, 4, 4, 2, 2])

    with gear_col:
        if st.button("⚙", key=f"gear_{entry_id}"):
            st.session_state[f"editing_{entry_id}"] = not is_editing
            st.rerun()

    if is_editing:
        with c1:
            new_cat = st.text_input("Category", value=entry_category(entry), key=f"cat_{entry_id}")
        with c2:
            new_sub = st.text_input("Subcategory", value=entry.get("subcategory", ""), key=f"sub_{entry_id}")
        with c3:
            new_topic = st.text_input("Topic", value=entry.get("topic", ""), key=f"top_{entry_id}")
        with c4:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("Save", key=f"save_{entry_id}", type="secondary", use_container_width=True):
                update_entry(entry_id, category=new_cat.strip(),
                             subcategory=new_sub.strip(), topic=new_topic.strip())
                st.session_state[f"editing_{entry_id}"] = False
                st.rerun()
        with c5:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("delete", key=f"delete_{entry_id}", type="primary", use_container_width=True):
                delete_entry(entry_id)
                st.rerun()


def main():
    # Header
    st.markdown('<div class="hero-title">Knowledge Librarian</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Personal Knowledge Index</div>', unsafe_allow_html=True)

    index = load_index()

    # Stats row
    categories = list(set(entry_category(e) for e in index))
    source_types = [e.get("source_type", "web") for e in index]
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{len(index)}</div><div class="stat-label">Sources saved</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{len(categories)}</div><div class="stat-label">Categories</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{source_types.count("youtube")}</div><div class="stat-label">Videos</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{source_types.count("kaggle")}</div><div class="stat-label">Kaggle notebooks</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Two-column layout
    left, right = st.columns([1, 1], gap="large")

    # --- LEFT: Add a URL ---
    with left:
        st.markdown('<p class="section-label">Add a source</p>', unsafe_allow_html=True)
        url_input = st.text_input("Paste a URL", placeholder="https://...")
        cat_col, subcat_col, topic_col = st.columns(3)
        with cat_col:
            category_input = st.text_input("Category", placeholder="e.g. Machine Learning & AI")
        with subcat_col:
            subcategory_input = st.text_input("Subcategory", placeholder="e.g. Deep Learning")
        with topic_col:
            topic_input = st.text_input("Topic", placeholder="e.g. Transformers")
        user_note = st.text_input("Your note (optional)", placeholder="e.g. good explanation of SMOTE")

        if st.button("Save to library", type="secondary"):
            if url_input.strip():
                with st.spinner("Reading and summarising..."):
                    result = process_url(
                        url=url_input.strip(),
                        user_note=user_note.strip() or None,
                        category=category_input.strip() or None,
                        subcategory=subcategory_input.strip() or None,
                        topic=topic_input.strip() or None,
                    )
                if result["success"]:
                    st.markdown(f'<div class="success-msg">Saved: <strong>{result["entry"]["title"]}</strong></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-msg">Error: {result["error"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-msg">Please enter a URL.</div>', unsafe_allow_html=True)

    # --- RIGHT: Search ---
    with right:
        st.markdown('<p class="section-label">Search your library</p>', unsafe_allow_html=True)
        query = st.text_input("What are you looking for?", placeholder="e.g. class imbalance, Cox PH, DAX filter context")

        filter_category = st.selectbox("Filter by category", ["All"] + sorted(set(entry_category(e) for e in index)))
        filter_source = st.selectbox("Filter by source", ["All", "YouTube", "Kaggle", "Web"])

        if query.strip():
            results = search_index(
                query=query.strip(),
                category=None if filter_category == "All" else filter_category,
                source_type=None if filter_source == "All" else filter_source.lower()
            )
            if results:
                st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:0.75rem;color:#555;margin-bottom:0.8rem">{len(results)} result{"s" if len(results)>1 else ""} found</div>', unsafe_allow_html=True)
                for entry in results:
                    render_card(entry)
            else:
                st.markdown('<div style="color:#555;font-family:DM Mono,monospace;font-size:0.85rem">No matches found.</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # --- Full library browser ---
    st.markdown('<p class="section-label">Your library</p>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)

    with f1:
        all_cats = ["All"] + sorted(set(entry_category(e) for e in index))
        browse_cat = st.selectbox("Category", all_cats, key="browse_cat")

    cat_filtered = [e for e in index if browse_cat == "All" or entry_category(e) == browse_cat]

    with f2:
        all_subcats = ["All"] + sorted(set(e.get("subcategory", "") for e in cat_filtered if e.get("subcategory")))
        browse_subcat = st.selectbox("Subcategory", all_subcats, key="browse_subcat")

    subcat_filtered = [e for e in cat_filtered if browse_subcat == "All" or e.get("subcategory") == browse_subcat]

    with f3:
        all_topics = ["All"] + sorted(set(e.get("topic", "") for e in subcat_filtered if e.get("topic")))
        browse_topic = st.selectbox("Topic", all_topics, key="browse_topic")

    topic_filtered = [e for e in subcat_filtered if browse_topic == "All" or e.get("topic") == browse_topic]

    filtered = sorted(topic_filtered, key=lambda x: x.get("date_saved", ""), reverse=True)

    if filtered:
        # Group by category → subcategory
        from collections import defaultdict
        groups = defaultdict(lambda: defaultdict(list))
        for e in filtered:
            groups[entry_category(e)][e.get("subcategory", "") or "General"].append(e)

        for cat in sorted(groups):
            cat_entries = [e for sub in groups[cat].values() for e in sub]
            cat_label = f"{cat}  ·  {len(cat_entries)} source{'s' if len(cat_entries) != 1 else ''}"
            with st.expander(cat_label, expanded=False):
                for subcat in sorted(groups[cat]):
                    entries = groups[cat][subcat]
                    sub_label = f"{subcat}  ·  {len(entries)} source{'s' if len(entries) != 1 else ''}"
                    with st.expander(sub_label, expanded=False):
                        for entry in entries:
                            render_card(entry)
    else:
        st.markdown('<div style="color:#555;font-family:DM Mono,monospace;font-size:0.85rem">No sources saved yet. Add your first URL above.</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()