import io
import os
import pandas as pd  # standard alias
import streamlit as st
from openai import OpenAI  # or replace with groq / deepseek client if preferred

# Page Configuration
st.set_page_config(
    page_title="Anonymous Portfolio Expert", page_icon="📈", layout="wide"
)

# App Header
st.title("🛡️ Anonymous Investment & Equity Portfolio Reviewer")
st.markdown(
    """
* **100% Non-Invasive:** No login, no signup, no database tracking. 
* **Zero Persistence:** Your portfolio summary/data is processed in-memory and discarded the moment you refresh or close the page.
"""
)

# Initialize LLM Client (using environment secret or input)
# For completely free execution, you can use Groq or OpenRouter free tiers, or standard OpenAI keys.
api_key = st.secrets.get("OPENAI_API_KEY", "")

if not api_key:
  with st.sidebar:
    st.subheader("Configuration")
    api_key = st.text_input("Enter LLM API Key (OpenAI/Groq)", type="password")
    st.markdown(
        "[Get a free/low-cost API key]"
        "(https://console.groq.com/keys) (Groq offers free tiers)"
    )

# Input Methods
st.subheader("1. Share Your Portfolio Summary")
input_tab1, input_tab2 = st.tabs(["📁 Upload File (CSV/Excel)", "✍️ Paste Text"])

portfolio_data = ""

with input_tab1:
  uploaded_file = st.file_uploader(
      "Upload your portfolio CSV or Excel file", type=["csv", "xlsx", "xls"]
  )
  if uploaded_file is not None:
    try:
      if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
      else:
        df = pd.read_excel(uploaded_file)
      st.dataframe(df.head())
      portfolio_data = df.to_string(index=False)
    except Exception as e:
      st.error(f"Error reading file: {e}")

with input_tab2:
  pasted_text = st.text_area(
      "Or paste your holdings summary here (e.g., Asset Name, Allocation %,"
      " Value)",
      height=150,
      placeholder=(
          "Example:\n- Apple Inc (AAPL): 30%\n- Vanguard S&P 500 ETF (VOO):"
          " 50%\n- Cash: 20%"
      ),
  )
  if pasted_text:
    portfolio_data = pasted_text

# Analysis Trigger
if st.button("Evaluate Portfolio", type="primary"):
  if not api_key:
    st.warning("Please provide an API key to run the analysis.")
  elif not portfolio_data:
    st.warning("Please upload a file or paste your portfolio data first.")
  else:
    with st.spinner("Analyzing portfolio allocation and risk profile..."):
      try:
        client = OpenAI(
            api_key=api_key,
            # If using Groq, change base_url to "https://api.groq.com/openai/v1" and model to "llama-3.3-70b-versatile"
        )

        system_prompt = (
            "You are a professional, objective, and conservative financial"
            " equity expert. Review the provided portfolio summary. Provide"
            " structured, non-binding educational feedback covering: 1) Asset"
            " Allocation & Diversification breakdown, 2) Concentration risks,"
            " 3) General suggestions for optimization (e.g., rebalancing ideas)."
            " Always include a clear disclaimer that this is for educational"
            " purposes only and not certified financial advice."
            " Never request personal identifiable information (PII)."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or lightweight model like llama-3.3-70b-versatile via Groq
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        "Here is the portfolio summary data:\n\n"
                        f"{portfolio_data}"
                    ),
                },
            ],
            temperature=0.3,
        )

        analysis_result = response.choices[0].message.content

        st.markdown("---")
        st.subheader("📊 Expert Portfolio Review")
        st.markdown(analysis_result)

      except Exception as e:
        st.error(f"An error occurred during generation: {e}")

# Footer disclaimer
st.markdown("---")
st.caption(
    "🔒 Privacy Notice: We do not store logs, track IPs, or save portfolio"
    " files. Data lives strictly in session memory."
)
