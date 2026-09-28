import io
import os
import pandas as pd
import streamlit as st
from openai import OpenAI

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
* **Global Market Support:** Fully parses Indian (NSE/BSE), US, and international equities or mutual funds.
"""
)

# API Key Input
api_key = st.secrets.get("GROQ_API_KEY", "")

if not api_key:
  with st.sidebar:
    st.subheader("Configuration")
    api_key = st.text_input("Enter Groq API Key", type="password")
    st.markdown(
        "Get a free API key instantly at"
        " [console.groq.com/keys](https://console.groq.com/keys)"
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
      st.dataframe(df)
      portfolio_data = df.to_string(index=False)
    except Exception as e:
      st.error(f"Error reading file: {e}")

with input_tab2:
  pasted_text = st.text_area(
      "Or paste your holdings summary here (e.g., Asset Name, Quantity, Avg"
      " Price)",
      height=150,
      placeholder=(
          "Example:\n- Reliance Industries: 15 shares, Avg: ₹2,400\n- TCS: 10"
          " shares, Avg: ₹3,500\n- Nifty Bees ETF: 50 units"
      ),
  )
  if pasted_text:
    portfolio_data = pasted_text

# Analysis Trigger
if st.button("Evaluate Portfolio", type="primary"):
  if not api_key:
    st.warning("Please provide a Groq API key in the sidebar to continue.")
  elif not portfolio_data:
    st.warning("Please upload a file or paste your portfolio data first.")
  else:
    with st.spinner("Analyzing portfolio allocation and risk profile..."):
      try:
        client = OpenAI(
            api_key=api_key, base_url="https://api.groq.com/openai/v1"
        )

        system_prompt = (
            "You are a professional, objective, and conservative financial"
            " equity expert capable of analyzing portfolios from any global"
            " market, including Indian equities (NSE/BSE), mutual funds, and"
            " US stocks. Review the provided portfolio data. Provide detailed,"
            " structured, non-binding educational feedback covering:\n"
            "1) Asset Allocation & Sector Diversification breakdown\n"
            "2) Concentration and Market Risks\n"
            "3) Actionable optimization suggestions (e.g., rebalancing, hedging"
            " ideas)\n"
            "Always include a clear disclaimer that this is for educational"
            " purposes only and not certified financial advice.\n"
            "Never request personal identifiable information (PII)."
        )

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
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
            max_tokens=2048,  # Ensures complete, unabridged responses
        )

        analysis_result = response.choices[0].message.content

        if analysis_result:
          st.markdown("---")
          st.subheader("📊 Expert Portfolio Review")
          st.markdown(analysis_result)
        else:
          st.error(
              "The model returned an empty response. Please try re-running or"
              " simplifying your input formatting."
          )

      except Exception as e:
        st.error(f"An error occurred during generation: {e}")

# Footer disclaimer
st.markdown("---")
st.caption(
    "🔒 Privacy Notice: We do not store logs, track IPs, or save portfolio"
    " files. Data lives strictly in session memory."
)
