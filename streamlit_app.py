import streamlit as st
import openai
from tavily import TavilyClient

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Web Research Agent",
    page_icon="🧠",
    layout="wide",
)

# --- ACCESS SECRETS ---
openai.api_key = st.secrets["openai"]["api_key"]
tavily_client = TavilyClient(api_key=st.secrets["tavily"]["api_key"])

# --- STYLING ---
st.markdown("""
    <style>
        .main {
            background-color: #F9FAFB;
        }
        .reportview-container {
            padding-top: 2rem;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 0.6rem 1.2rem;
            font-size: 16px;
            border-radius: 8px;
        }
        .stDownloadButton>button {
            background-color: #2196F3;
            color: white;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---
def generate_questions(topic):
    prompt = f"""
    Generate 5-6 in-depth research questions about the topic: "{topic}". 
    Cover causes, effects, data, solutions, and controversies.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response['choices'][0]['message']['content']
        questions = content.strip().split("\n")
        return [q.strip("- ").strip() for q in questions if q.strip()]
    except Exception as e:
        st.error(f"Error with OpenAI: {e}")
        return []

def search_web(question):
    try:
        results = tavily_client.search(query=question, max_results=5)
        return results.get("results", [])
    except Exception as e:
        st.error(f"Web search error: {e}")
        return []

def generate_report(topic, qna):
    report = f"# 📘 Research Report: {topic}\n\n"
    report += f"## 🧾 Introduction\nThis report explores the topic \"{topic}\" through a series of structured research questions and web-based answers.\n\n"
    for q, answers in qna.items():
        report += f"## ❓ {q}\n"
        for a in answers:
            title = a.get("title")
            content = a.get("content")
            url = a.get("url")
            report += f"- **{title}**: {content}\n  [🔗 Read More]({url})\n"
        report += "\n"
    report += "## ✅ Conclusion\nThis report compiles current online insights to offer a comprehensive understanding of the topic."
    return report

# --- UI LAYOUT ---
st.title("🧠 AI Web Research Agent")
st.markdown("### Powered by GPT & Tavily · ReAct Pattern")

with st.expander("📘 How it works", expanded=False):
    st.markdown("""
    1. Enter a topic you're interested in.
    2. The AI generates key research questions.
    3. It performs web searches using Tavily.
    4. All results are compiled into a downloadable markdown report.
    """)

# --- MAIN FORM ---
st.markdown("### 🔍 Enter a Research Topic")
topic = st.text_input("Topic", placeholder="e.g. Climate change, AI in agriculture, etc.")

if st.button("✨ Generate Report"):
    if not topic:
        st.warning("Please enter a topic.")
    else:
        with st.spinner("🤖 Generating research questions..."):
            questions = generate_questions(topic)
            st.success("✅ Questions generated!")

        qna = {}
        with st.spinner("🌐 Searching the web for answers..."):
            for q in questions:
                st.markdown(f"<b>🔍 {q}</b>", unsafe_allow_html=True)
                results = search_web(q)
                qna[q] = results

        with st.spinner("📝 Compiling your report..."):
            report_md = generate_report(topic, qna)

        st.markdown("---")
        st.markdown("## 📄 Final Research Report")
        st.markdown(report_md)

        st.download_button(
            label="📥 Download Report (Markdown)",
            data=report_md,
            file_name=f"{topic.replace(' ', '_')}_report.md",
            mime="text/markdown"
        )

# Optional: Add a footer
st.markdown("---")
st.markdown(
    "<center><sub>Made with ❤️ by Nokwanda Buthelezi · Powered by OpenAI + Tavily</sub></center>",
    unsafe_allow_html=True
)
