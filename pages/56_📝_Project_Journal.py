"""
Module 56: Project Journal — DataScience Flow v9.5
Experiment tracking, observations, decisions log
Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="Project Journal | DataScience Flow", page_icon="📝", layout="wide")

from subscription import init_subscription_state, TIERS, tier_badge_html, get_tier_info, local_save_subscription
from security import (
    init_secure_session, verify_subscription_integrity,
    authenticate_subscription, check_rate_limit, check_export_limit,
    validate_upload, sanitise_string, sanitise_email,
    log_action, check_session_timeout,
    watermark_dataframe, BRAND_WATERMARK, BRAND_FOOTER,
)

# ═══ Security & Session Verification ═══
init_secure_session()
if not st.session_state.get("sub_authenticated"):
    st.warning("⚠️ Subscription required. Start your free trial from the Home page.")
    st.stop()
if not verify_subscription_integrity():
    st.error("🔒 Session integrity check failed. Please re-authenticate.")
    st.stop()
if check_session_timeout():
    st.warning("⏰ Session expired. Please re-authenticate.")
    st.stop()
check_rate_limit()

st.markdown("""
## 📝 Project Journal — Module 56

> **What is a Project Journal?** A project journal is a structured log where you record your data science 
> project's decisions, experiments, observations, and learnings. It's your project's memory — ensuring 
> nothing is lost and everything is reproducible.

### 🎓 Key Concepts
| Concept | What It Means | Why It Matters |
|---------|---------------|----------------|
| Experiment Log | Record of every experiment | Know what you tried and what worked |
| Decision Record | Why you chose X over Y | Avoid revisiting settled decisions |
| Observation | Interesting finding | Capture insights before they're forgotten |
| Hypothesis | What you expect to find | Gives analysis direction |
| Lesson Learned | What went wrong/right | Improves future projects |

### 📐 The Scientific Method for Data Science
| Step | Journal Entry Type | Example |
|------|-------------------|---------|
| 1. Question | Hypothesis | "I think churn is driven by contract type" |
| 2. Explore | Observation | "Month-to-month customers churn 3x more" |
| 3. Experiment | Experiment | "Trained Random Forest with contract features" |
| 4. Analyze | Result | "Accuracy: 78%, contract type is top feature" |
| 5. Decide | Decision | "Use contract type in final model" |
| 6. Reflect | Lesson | "Always check class balance before training" |
""")

# Initialize journal state
if "journal_entries" not in st.session_state:
    st.session_state["journal_entries"] = []

if "journal_project" not in st.session_state:
    st.session_state["journal_project"] = {
        "name": "My Data Science Project",
        "description": "",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "status": "In Progress",
    }

tab_project, tab_new, tab_timeline, tab_search, tab_export = st.tabs([
    "📁 Project Info", "➕ New Entry", "📅 Timeline", "🔍 Search", "📤 Export"
])

with tab_project:
    st.markdown("### 📁 Project Information")
    
    name = st.text_input("Project Name", st.session_state["journal_project"]["name"], key="proj_name")
    desc = st.text_area("Project Description", st.session_state["journal_project"]["description"], key="proj_desc")
    status = st.selectbox("Status", ["Planning", "In Progress", "Review", "Complete", "On Hold"], 
                          index=["Planning", "In Progress", "Review", "Complete", "On Hold"].index(
                              st.session_state["journal_project"].get("status", "In Progress")), key="proj_status")
    
    if st.button("💾 Save Project Info"):
        st.session_state["journal_project"] = {
            "name": name, "description": desc,
            "start_date": st.session_state["journal_project"].get("start_date", datetime.now().strftime("%Y-%m-%d")),
            "status": status,
            "updated": datetime.now().isoformat(),
        }
        st.success("✅ Project info saved!")
    
    # Show current data summary
    if st.session_state.get("df_cleaned") is not None:
        df = st.session_state["df_cleaned"]
        st.markdown("### 📊 Current Dataset Summary")
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", f"{df.shape[0]:,}")
        c2.metric("Columns", f"{df.shape[1]}")
        c3.metric("Missing %", f"{df.isnull().sum().sum()/(df.shape[0]*df.shape[1])*100:.1f}%")

with tab_new:
    st.markdown("### ➕ New Journal Entry")
    
    entry_type = st.selectbox("Entry Type", [
        "🔬 Experiment", "👀 Observation", "✅ Decision", "💡 Hypothesis",
        "📝 Note", "⚠️ Issue", "📚 Lesson Learned", "🎯 Milestone"
    ], key="entry_type")
    
    entry_title = st.text_input("Title", key="entry_title")
    entry_content = st.text_area("Content", height=150, key="entry_content", 
                                  placeholder="Describe your experiment, observation, or decision in detail...")
    
    # Type-specific fields
    extra = {}
    if entry_type == "🔬 Experiment":
        extra["hypothesis"] = st.text_input("Hypothesis", key="exp_hyp")
        extra["method"] = st.text_input("Method/Approach", key="exp_method")
        extra["result"] = st.text_input("Result/Outcome", key="exp_result")
        extra["metric"] = st.text_input("Key Metric & Value", key="exp_metric")
    elif entry_type == "✅ Decision":
        extra["options"] = st.text_input("Options considered", key="dec_options")
        extra["chosen"] = st.text_input("Chosen option", key="dec_chosen")
        extra["rationale"] = st.text_input("Rationale", key="dec_rationale")
    elif entry_type == "💡 Hypothesis":
        extra["status"] = st.selectbox("Status", ["Proposed", "Testing", "Confirmed", "Rejected"], key="hyp_status")
    elif entry_type == "⚠️ Issue":
        extra["severity"] = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"], key="issue_sev")
        extra["resolution"] = st.text_input("Resolution (if resolved)", key="issue_res")
    
    tags = st.text_input("Tags (comma-separated)", key="entry_tags")
    
    if st.button("📝 Save Entry"):
        if not entry_title:
            st.error("Please enter a title.")
        else:
            entry = {
                "id": len(st.session_state["journal_entries"]) + 1,
                "type": entry_type,
                "title": sanitise_string(entry_title),
                "content": sanitise_string(entry_content),
                "tags": [t.strip() for t in tags.split(',') if t.strip()],
                "timestamp": datetime.now().isoformat(),
                "extra": extra,
            }
            st.session_state["journal_entries"].append(entry)
            log_action("journal_entry", f"{entry_type}: {entry_title}")
            st.success(f"✅ Entry saved: {entry_type} — {entry_title}")

with tab_timeline:
    st.markdown("### 📅 Journal Timeline")
    
    if not st.session_state["journal_entries"]:
        st.info("No journal entries yet. Go to New Entry tab to add your first entry.")
    else:
        # Filter
        type_filter = st.multiselect("Filter by type", 
            ["🔬 Experiment", "👀 Observation", "✅ Decision", "💡 Hypothesis",
             "📝 Note", "⚠️ Issue", "📚 Lesson Learned", "🎯 Milestone"],
            key="timeline_filter")
        
        entries = st.session_state["journal_entries"]
        if type_filter:
            entries = [e for e in entries if e["type"] in type_filter]
        
        # Sort by timestamp (newest first)
        entries = sorted(entries, key=lambda x: x.get("timestamp", ""), reverse=True)
        
        st.markdown(f"**{len(entries)} entries**")
        
        for entry in entries:
            icon = entry["type"].split()[0]
            type_name = entry["type"].split()[1] if len(entry["type"].split()) > 1 else entry["type"]
            
            with st.expander(f"{icon} **{entry['title']}** — {type_name} — {entry.get('timestamp', '')[:10]}"):
                st.markdown(f"**{entry['type']}** | {entry.get('timestamp', '')[:19]}")
                st.markdown(entry["content"])
                
                if entry.get("tags"):
                    tag_str = " ".join([f"`{t}`" for t in entry["tags"]])
                    st.markdown(f"🏷️ {tag_str}")
                
                if entry.get("extra"):
                    for k, v in entry["extra"].items():
                        if v:
                            st.markdown(f"- **{k.title()}:** {v}")
                
                if st.button("🗑️ Delete", key=f"del_entry_{entry['id']}"):
                    st.session_state["journal_entries"] = [
                        e for e in st.session_state["journal_entries"] if e["id"] != entry["id"]
                    ]
                    st.rerun()

with tab_search:
    st.markdown("### 🔍 Search Journal")
    
    search_term = st.text_input("Search term", key="journal_search")
    
    if search_term and st.session_state["journal_entries"]:
        results = []
        for e in st.session_state["journal_entries"]:
            if (search_term.lower() in e.get("title", "").lower() or 
                search_term.lower() in e.get("content", "").lower() or
                any(search_term.lower() in t.lower() for t in e.get("tags", []))):
                results.append(e)
        
        st.markdown(f"**Found {len(results)} entries matching '{search_term}'**")
        for entry in results:
            st.markdown(f"- **{entry['type']}** — {entry['title']} ({entry.get('timestamp', '')[:10]})")
    elif not search_term:
        # Show statistics
        if st.session_state["journal_entries"]:
            type_counts = {}
            for e in st.session_state["journal_entries"]:
                t = e["type"]
                type_counts[t] = type_counts.get(t, 0) + 1
            st.markdown("#### Entry Statistics")
            for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
                st.markdown(f"- {t}: **{c}**")
        else:
            st.info("No entries to search.")

with tab_export:
    st.markdown("### 📤 Export Journal")
    
    if not st.session_state["journal_entries"]:
        st.info("No entries to export.")
    else:
        # Export as JSON
        journal_data = {
            "project": st.session_state["journal_project"],
            "entries": st.session_state["journal_entries"],
            "export_date": datetime.now().isoformat(),
            "platform": "DataScience Flow v9.5 — HMG Academy",
            "total_entries": len(st.session_state["journal_entries"]),
        }
        journal_json = json.dumps(journal_data, indent=2, default=str)
        
        # Export as Markdown
        md_lines = [
            f"# {st.session_state['journal_project']['name']}",
            f"\n> Generated by DataScience Flow v9.5 — HMG Academy\n",
            f"**Status:** {st.session_state['journal_project'].get('status', 'N/A')}",
            f"**Description:** {st.session_state['journal_project'].get('description', 'N/A')}",
            f"**Total Entries:** {len(st.session_state['journal_entries'])}",
            f"\n---\n",
            "## Journal Entries\n",
        ]
        for entry in sorted(st.session_state["journal_entries"], key=lambda x: x.get("timestamp", "")):
            md_lines.append(f"### {entry['type']} — {entry['title']}")
            md_lines.append(f"**Date:** {entry.get('timestamp', '')[:10]}\n")
            md_lines.append(entry["content"])
            if entry.get("tags"):
                md_lines.append(f"\nTags: {', '.join(entry['tags'])}")
            if entry.get("extra"):
                md_lines.append("\n**Details:**")
                for k, v in entry["extra"].items():
                    if v:
                        md_lines.append(f"- {k.title()}: {v}")
            md_lines.append("\n---\n")
        
        md_content = "\n".join(md_lines)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button(
                "📥 Download Journal (JSON)",
                journal_json,
                "project_journal.json",
                "application/json"
            )
        with c2:
            st.download_button(
                "📝 Download Journal (Markdown)",
                md_content,
                "project_journal.md",
                "text/markdown"
            )
        with c3:
            # CSV export
            entries_df = pd.DataFrame(st.session_state["journal_entries"])
            st.download_button(
                "📊 Download Entries (CSV)",
                entries_df.to_csv(index=False),
                "journal_entries.csv",
                "text/csv"
            )

st.markdown("---")
st.markdown("""
💡 **Key Takeaway:** A project journal is your data science project's memory. Record every decision, 
experiment, and observation. Future you (and your team) will thank you. The best data scientists 
don't just analyze data — they document their reasoning.

📚 **Next Steps:** Use Module 57 (DS Roadmap) to plan your next data science learning milestone.
""")

# ═══════════════════════════════════════════════════════════════
# BRAND FOOTER — DataScience Flow v9.5 | HMG Academy
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="text-align:center; padding:16px 0; font-size:0.82rem; color:#A0A8B8;">
<b>DataScience Flow</b> v9.5 — Part of <b>HMG Academy</b> Ecosystem — Subsidiary of <b>HMG Concepts</b> (est. 2015)<br>
Built by <b>Adewale Samson Adeagbo</b> | 🔒 Secured Platform | 🏗️ HMG Academy · HMG Technologies · HMG Media · HMG Gospel<br>
<a href="https://hmgacademy.pages.dev" style="color:#6C63FF;">hmgacademy.pages.dev</a> ·
<a href="https://hmgconcepts.pages.dev" style="color:#6C63FF;">hmgconcepts.pages.dev</a> ·
<a href="https://cssadewale.pages.dev" style="color:#6C63FF;">cssadewale.pages.dev</a>
</div>
""", unsafe_allow_html=True)
