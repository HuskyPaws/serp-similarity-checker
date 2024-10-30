import streamlit as st
import requests
import json
import pandas as pd
from typing import Dict, Any, List, Set
from urllib.parse import urlparse
import numpy as np
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="SERP Similarity Checker",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Streamlined Custom CSS
st.markdown("""
    <style>
    /* Global styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styling */
    h1 {
        color: #0f172a;
        font-weight: 700;
        padding-bottom: 1.5rem;
        margin-bottom: 2rem;
    }
    
    h3 {
        color: #1e40af;
        font-weight: 600;
        margin: 1rem 0;
    }
    
    /* Table styling */
    .dataframe {
        font-size: 0.875rem;
        border-radius: 0.75rem;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }
    
    .dataframe th {
        background: #f1f5f9;
        padding: 0.75rem 1rem;
        font-weight: 600;
    }
    
    .dataframe td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #e2e8f0;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        border-radius: 0.75rem;
        padding: 0.75rem 1.5rem;
        border: none;
        font-weight: 500;
        transition: all 0.2s;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.1);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
    }
    
    /* Input field styling */
    .stTextInput input {
        border-radius: 0.75rem;
        border: 2px solid #e2e8f0;
        padding: 0.75rem 1rem;
        transition: all 0.2s;
    }
    
    .stTextInput input:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    /* Tag styling */
    .tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0.25rem;
    }
    
    .tag-blue {
        background-color: #dbeafe;
        color: #1e40af;
    }
    
    .tag-green {
        background-color: #dcfce7;
        color: #166534;
    }
    
    .tag-yellow {
        background-color: #fef9c3;
        color: #854d0e;
    }
    </style>
""", unsafe_allow_html=True)

def perform_search(query: str, api_key: str) -> Dict[str, Any]:
    """Perform search using Serper.dev API"""
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=payload)
    return response.json()

def get_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        return domain.replace('www.', '')
    except:
        return url

def analyze_serp_similarity(results1: Dict[str, Any], results2: Dict[str, Any]) -> Dict:
    """Enhanced SERP analysis with additional metrics"""
    organic1 = results1.get('organic', [])
    organic2 = results2.get('organic', [])
    
    # Domain analysis
    domains1 = {get_domain(result['link']): i+1 for i, result in enumerate(organic1)}
    domains2 = {get_domain(result['link']): i+1 for i, result in enumerate(organic2)}
    
    # URL analysis
    urls1 = {result['link']: i+1 for i, result in enumerate(organic1)}
    urls2 = {result['link']: i+1 for i, result in enumerate(organic2)}
    
    common_domains = set(domains1.keys()) & set(domains2.keys())
    common_urls = set(urls1.keys()) & set(urls2.keys())
    
    # Calculate position differences for common domains
    position_differences = {
        domain: abs(domains1[domain] - domains2[domain])
        for domain in common_domains
    }
    
    # Calculate advanced metrics
    domain_similarity = len(common_domains) / max(len(domains1), len(domains2)) * 100
    url_similarity = len(common_urls) / max(len(urls1), len(urls2)) * 100
    avg_position_diff = np.mean(list(position_differences.values())) if position_differences else 0
    
    # Identify significant position changes
    position_changes = {
        domain: {
            'pos1': domains1[domain],
            'pos2': domains2[domain],
            'diff': domains2[domain] - domains1[domain]
        }
        for domain in common_domains
        if abs(domains1[domain] - domains2[domain]) > 2
    }
    
    return {
        'common_domains': common_domains,
        'common_urls': common_urls,
        'domain_similarity': domain_similarity,
        'url_similarity': url_similarity,
        'position_differences': position_differences,
        'avg_position_diff': avg_position_diff,
        'position_changes': position_changes,
        'domains1': domains1,
        'domains2': domains2,
        'total_results1': len(organic1),
        'total_results2': len(organic2)
    }

def main():
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='font-size: 2.5rem; font-weight: bold; margin-bottom: 1rem;'>
                🔍 SERP Similarity Checker
            </h1>
            <p style='font-size: 1.2rem; color: #334155;'>
                Compare and analyze search results between queries
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2 = st.tabs(["📊 Analysis", "⚙️ Settings"])
    
    with tab2:
        api_key = st.text_input(
            "Enter your Serper.dev API key:",
            value="",
            type="password"
        )
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            query1 = st.text_input("First Query:", placeholder="e.g., apple inc")
        with col2:
            query2 = st.text_input("Second Query:", placeholder="e.g., apple company")
        
        if st.button("🔍 Compare Results"):
            try:
                with st.spinner("Analyzing search results..."):
                    # Perform searches
                    results1 = perform_search(query1, api_key)
                    results2 = perform_search(query2, api_key)
                    
                    # Analyze similarities
                    similarity = analyze_serp_similarity(results1, results2)
                    
                    # Display key metrics
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("Domain Similarity", f"{similarity['domain_similarity']:.1f}%")
                    with m2:
                        st.metric("URL Similarity", f"{similarity['url_similarity']:.1f}%")
                    with m3:
                        st.metric("Avg. Position Difference", f"{similarity['avg_position_diff']:.1f}")
                    
                    # Results comparison
                    col1, col2 = st.columns(2)
                    
                    # Process results with enhanced information
                    def process_results(results, other_domains):
                        return pd.DataFrame([{
                            'Position': i+1,
                            'Title': r.get('title', ''),
                            'Domain': get_domain(r['link']),
                            'URL': r['link'],
                            'Status': 'Common' if get_domain(r['link']) in other_domains else 'Unique',
                            'Snippet': r.get('snippet', '')[:150] + '...' if r.get('snippet') else ''
                        } for i, r in enumerate(results.get('organic', []))])
                    
                    df1 = process_results(results1, similarity['domains2'])
                    df2 = process_results(results2, similarity['domains1'])
                    
                    # Display results with position change highlighting
                    with col1:
                        st.markdown(f"### Results for: {query1}")
                        st.dataframe(
                            df1.style.apply(lambda x: [
                                'background-color: #dcfce7' if x['Status'] == 'Common' else ''
                                for i in range(len(x))
                            ], axis=1),
                            use_container_width=True
                        )
                    
                    with col2:
                        st.markdown(f"### Results for: {query2}")
                        st.dataframe(
                            df2.style.apply(lambda x: [
                                'background-color: #dcfce7' if x['Status'] == 'Common' else ''
                                for i in range(len(x))
                            ], axis=1),
                            use_container_width=True
                        )
                    
                    # Position Changes Analysis
                    if similarity['position_changes']:
                        st.markdown("### 📊 Significant Position Changes")
                        changes_df = pd.DataFrame([
                            {
                                'Domain': domain,
                                'Position in Query 1': data['pos1'],
                                'Position in Query 2': data['pos2'],
                                'Change': data['diff']
                            }
                            for domain, data in similarity['position_changes'].items()
                        ]).sort_values('Change', ascending=False)
                        
                        st.dataframe(
                            changes_df.style.apply(lambda x: [
                                'background-color: #fef9c3' if x['Change'] > 0 else 'background-color: #fee2e2'
                                for i in range(len(x))
                            ], axis=1),
                            use_container_width=True
                        )
                    
                    # Common Elements Section
                    st.markdown("### 🔍 Common Elements")
                    common_col1, common_col2 = st.columns(2)
                    
                    with common_col1:
                        st.markdown("#### 🌐 Common Domains")
                        if similarity['common_domains']:
                            for domain in sorted(similarity['common_domains']):
                                st.markdown(f"""
                                    <div style='
                                        background: #f0f9ff;
                                        padding: 0.5rem 1rem;
                                        border-radius: 0.5rem;
                                        margin: 0.25rem 0;
                                        border: 1px solid #bae6fd;
                                        font-family: monospace;
                                    '>
                                        {domain}
                                    </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No common domains found")
                    
                    with common_col2:
                        st.markdown("#### 🔗 Exact URL Matches")
                        if similarity['common_urls']:
                            for url in sorted(similarity['common_urls']):
                                st.markdown(f"""
                                    <div style='
                                        background: #f0f9ff;
                                        padding: 0.5rem 1rem;
                                        border-radius: 0.5rem;
                                        margin: 0.25rem 0;
                                        border: 1px solid #bae6fd;
                                        overflow-wrap: break-word;
                                    '>
                                        <a href="{url}" target="_blank" style='
                                            color: #2563eb;
                                            text-decoration: none;
                                            font-size: 0.875rem;
                                        '>
                                            {url}
                                        </a>
                                    </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No exact URL matches found")
                    
                    # Export results
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    export_data = {
                        'analysis_time': timestamp,
                        'queries': {'query1': query1, 'query2': query2},
                        'metrics': {
                            'domain_similarity': similarity['domain_similarity'],
                            'url_similarity': similarity['url_similarity'],
                            'avg_position_difference': similarity['avg_position_diff']
                        },
                        'results1': df1.to_dict('records'),
                        'results2': df2.to_dict('records'),
                        'position_changes': similarity['position_changes'],
                        'common_domains': list(similarity['common_domains']),
                        'common_urls': list(similarity['common_urls'])
                    }
                    
                    st.download_button(
                        label="📥 Export Analysis",
                        data=json.dumps(export_data, indent=2),
                        file_name=f"serp_analysis_{timestamp}.json",
                        mime="application/json"
                    )
                    
            except Exception as e:
                st.error("An error occurred during analysis")
                with st.expander("View Error Details"):
                    st.code(str(e))

if __name__ == "__main__":
    main()
