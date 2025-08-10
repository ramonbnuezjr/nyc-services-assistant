"""
NYC Services GPT - Local MVP UI

Streamlit interface for testing the RAG pipeline as if in production.
Leverages existing infrastructure for optimal performance.
"""

import streamlit as st
import time
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.retrieve.vector_store import init_vector_store
from src.models.router import answer_with_rag
from src.config import config

# Page configuration
st.set_page_config(
    page_title="NYC Services GPT — Local MVP",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .source-item {
        background-color: #f8f9fa;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
        border-left: 3px solid #28a745;
    }
    .debug-panel {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">NYC Services GPT — Local MVP</h1>', unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Feature flags display
    st.subheader("Feature Flags")
    ui_config = config.get_ui_config()
    
    st.write(f"**Real LLM:** {'✅ Enabled' if ui_config['use_real_llm'] else '❌ Disabled'}")
    st.write(f"**Default Provider:** {ui_config['default_provider']}")
    st.write(f"**Rate Limiting:** {'✅ Enabled' if ui_config['rate_limit_enabled'] else '❌ Disabled'}")
    st.write(f"**Rate Limit RPS:** {ui_config['rate_limit_rps']}")
    
    # Environment info
    st.subheader("Environment")
    st.write(f"**Vector DB:** {config.vector_db_path}")
    st.write(f"**LLM Model:** {config.llm_model}")
    st.write(f"**Embedding Model:** {config.embedding_model}")
    
    # Quick actions
    st.subheader("Quick Actions")
    if st.button("🔄 Refresh Vector Store"):
        with st.spinner("Refreshing vector store..."):
            vs = init_vector_store()
            if vs:
                st.success("Vector store refreshed!")
            else:
                st.error("Failed to refresh vector store")
    
    if st.button("📊 Show Collection Stats"):
        with st.spinner("Loading stats..."):
            vs = init_vector_store()
            if vs:
                stats = vs.get_collection_stats()
                st.json(stats)
            else:
                st.error("Failed to load stats")

# Main interface
st.markdown("---")

# Query input
st.subheader("🤔 Ask about NYC Services")
example_questions = [
    "What benefits can I apply for if I lost my job?",
    "How do I apply for SNAP benefits?",
    "What documents do I need for Medicaid?",
    "How do I check my unemployment payment status?",
    "What income limits apply to cash assistance?"
]

# Question input with examples
question = st.text_input(
    "Your question:",
    placeholder="e.g., 'What benefits can I apply for if I lost my job?'",
    help="Ask any question about NYC government services"
)

# Show example questions
with st.expander("💡 Example Questions"):
    for example in example_questions:
        if st.button(example, key=f"example_{example[:20]}"):
            st.session_state.question = example
            st.rerun()

# Configuration controls
col1, col2, col3 = st.columns(3)

with col1:
    top_k = st.number_input(
        "📚 Top K Documents",
        min_value=1,
        max_value=10,
        value=5,
        help="Number of document chunks to retrieve"
    )

with col2:
    provider = st.selectbox(
        "🤖 Provider",
        ["openai", "gemini", "mock"],
        index=0 if ui_config['default_provider'] == 'openai' else 2,
        help="AI provider to use for response generation"
    )

with col3:
    service_options = ["", "unemployment", "snap", "medicaid", "cash_assistance", "childcare"]
    service_filter = st.selectbox(
        "🎯 Service Filter (Optional)",
        service_options,
        help="Filter results by specific service type"
    )

# Query button
if st.button("🚀 Ask Question", type="primary", use_container_width=True):
    if not question.strip():
        st.error("Please enter a question!")
    else:
        # Show processing state
        with st.spinner("🔍 Searching documents and generating response..."):
            start_time = time.time()
            
            # Prepare filters
            filters = {"service_type": service_filter} if service_filter else None
            
            # Get response from RAG pipeline
            response = answer_with_rag(
                question=question,
                top_k=top_k,
                filters=filters,
                provider=provider
            )
            
            processing_time = time.time() - start_time

# Display results
if 'response' in locals():
    st.markdown("---")
    
    # Answer section
    st.subheader("💬 Answer")
    st.markdown(f"**{response['answer']}**")
    
    # Sources section
    if response['sources']:
        st.subheader("📚 Sources")
        for i, source in enumerate(response['sources']):
            with st.expander(f"Source {i+1}: {source['service']} - {source['source']}"):
                st.write(f"**Service:** {source['service']}")
                st.write(f"**Document:** {source['source']}")
                st.write(f"**Relevance Score:** {source['score']:.3f}")
                st.write(f"**Content Preview:**")
                st.text(source['text'])
    else:
        st.info("No sources found for this query.")
    
    # Debug panel
    st.subheader("🔧 Debug Information")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("⏱️ Latency", f"{response['meta']['latency_ms']}ms")
    
    with col2:
        st.metric("🤖 Provider", response['meta']['provider'])
    
    with col3:
        st.metric("📚 Top K", response['meta']['top_k'])
    
    with col4:
        st.metric("💰 Cost Est.", f"${response['meta']['cost_estimate']:.4f}")
    
    # Additional metadata
    with st.expander("📊 Detailed Metadata"):
        st.json(response['meta'])
    
    # Performance metrics
    st.markdown("---")
    st.subheader("📈 Performance Metrics")
    
    # Success rate indicator (based on whether we got a meaningful response)
    response_quality = "✅ Good" if len(response['answer']) > 50 and not response['answer'].startswith("❌") else "⚠️ Needs Improvement"
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Response Quality", response_quality)
    
    with col2:
        st.metric("Sources Found", len(response['sources']))
    
    with col3:
        st.metric("Processing Time", f"{processing_time:.2f}s")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8rem;'>
    NYC Services GPT - Local MVP | Built with Streamlit | Leveraging 87% Success Rate RAG Pipeline
</div>
""", unsafe_allow_html=True)
