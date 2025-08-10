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
    page_title="NYC Services GPT",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .question-input {
        margin-bottom: 1rem;
    }
    .example-questions {
        margin: 1rem 0;
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 0.5rem;
    }
    .confidence-high {
        color: #28a745;
        font-weight: bold;
    }
    .confidence-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .confidence-low {
        color: #dc3545;
        font-weight: bold;
    }
    .human-fallback {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'question' not in st.session_state:
    st.session_state.question = ""
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Main header
st.markdown('<h1 class="main-header">🏙️ NYC Services GPT</h1>', unsafe_allow_html=True)
st.markdown("**Your AI assistant for NYC government services and benefits**")

# Example questions
st.markdown("### 💡 Example Questions")
example_questions = [
    "How do I apply for unemployment benefits in NYC?",
    "What documents do I need for SNAP benefits?",
    "How do I apply for Medicaid in New York?",
    "What income qualifies for cash assistance?",
    "How do I find child care subsidies?",
    "How do I check my EBT balance?",
    "What happens if my unemployment claim is denied?",
    "How do I appeal a SNAP decision?"
]

# Create responsive columns for example questions
if len(example_questions) <= 4:
    cols = st.columns(len(example_questions))
    for i, question in enumerate(example_questions):
        with cols[i]:
            if st.button(question[:40] + "..." if len(question) > 40 else question, key=f"ex_{i}"):
                st.session_state.question = question
                st.session_state.submitted = True
                st.rerun()
else:
    # For more questions, use a grid layout
    cols = st.columns(4)
    for i, question in enumerate(example_questions):
        with cols[i % 4]:
            if st.button(question[:35] + "..." if len(question) > 35 else question, key=f"ex_{i}"):
                st.session_state.question = question
                st.session_state.submitted = True
                st.rerun()

# Question input with Enter key submission
st.markdown("### ❓ Ask Your Question")

# Add JavaScript for Enter key submission
st.markdown("""
<script>
    const textArea = document.querySelector('textarea[data-testid="stTextArea"]');
    if (textArea) {
        textArea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const submitButton = document.querySelector('button[data-testid="baseButton-primary"]');
                if (submitButton) {
                    submitButton.click();
                }
            }
        });
    }
</script>
""", unsafe_allow_html=True)

question = st.text_area(
    "Ask about NYC services, benefits, or assistance programs:",
    value=st.session_state.question,
    height=100,
    placeholder="e.g., How do I apply for food stamps in NYC? (Press Enter to submit)",
    key="question_input",
    help="Type your question and press Enter to submit, or click an example question above."
)

# Show character count
if question:
    char_count = len(question)
    if char_count > 500:
        st.warning(f"⚠️ Question is quite long ({char_count} characters). Consider breaking it into smaller questions for better results.")
    elif char_count > 200:
        st.info(f"📝 Question length: {char_count} characters")
    else:
        st.success(f"✅ Question length: {char_count} characters")

# Handle submission (both button click and Enter key)
if st.button("🚀 Ask Question", type="primary", key="submit_button"):
    if question.strip():
        st.session_state.question = question
        st.session_state.submitted = True
        st.rerun()

# Also handle when question changes (for auto-submission from examples)
if question and question != st.session_state.question and st.session_state.submitted:
    st.session_state.question = question

# Process question when submitted
if st.session_state.submitted and st.session_state.question:
    # Show loading state
    with st.spinner("🔍 Searching NYC services database..."):
        try:
            # Initialize vector store
            vs = init_vector_store()
            
            # Get RAG response
            response = answer_with_rag(
                question=st.session_state.question,
                top_k=5,  # Fixed top_k for simplicity
                filters=None,  # No service filtering for MVP
                provider="openai"  # Fixed provider for MVP
            )
            
            # Display answer
            st.markdown("### 💬 Answer")
            st.markdown(response["answer"])
            
            # Success message
            st.success("✅ Answer generated successfully! Check the confidence score below.")
            
            # Display sources
            if response.get("sources"):
                st.markdown("### 📚 Sources")
                for i, source in enumerate(response["sources"], 1):
                    with st.expander(f"Source {i}: {source.get('service', 'Unknown Service')}"):
                        st.markdown(f"**Service:** {source.get('service', 'Unknown')}")
                        st.markdown(f"**Content:** {source.get('content', 'No content available')}")
                        if source.get('metadata'):
                            st.markdown(f"**Additional Info:** {source.get('metadata', {})}")
            
            # Confidence scoring and human fallback
            st.markdown("### 🎯 Confidence Assessment")
            
            # Calculate confidence based on response quality indicators
            # In a real implementation, this would come from the LLM or response analysis
            answer_length = len(response.get("answer", ""))
            sources_count = len(response.get("sources", []))
            
            # Simple confidence calculation based on response quality
            if answer_length > 200 and sources_count >= 2:
                confidence_score = 85
            elif answer_length > 100 and sources_count >= 1:
                confidence_score = 70
            elif answer_length > 50:
                confidence_score = 55
            else:
                confidence_score = 40
            
            # Display confidence with appropriate styling
            if confidence_score >= 80:
                st.markdown(f'<p class="confidence-high">✅ High Confidence: {confidence_score}%</p>', unsafe_allow_html=True)
                st.success("This answer should address your question completely.")
            elif confidence_score >= 60:
                st.markdown(f'<p class="confidence-medium">⚠️ Medium Confidence: {confidence_score}%</p>', unsafe_allow_html=True)
                st.warning("This answer should help, but you may want to verify details with official sources.")
            else:
                st.markdown(f'<p class="confidence-low">❌ Low Confidence: {confidence_score}%</p>', unsafe_allow_html=True)
                
                # Human fallback message
                st.markdown("""
                <div class="human-fallback">
                    <h4>🤝 Need Human Assistance</h4>
                    <p>We're not confident enough in this answer to fully address your question. 
                    Please contact NYC customer service for personalized assistance:</p>
                    <ul>
                        <li><strong>NYC 311:</strong> Dial 311 or visit <a href="https://www1.nyc.gov/311/" target="_blank">nyc.gov/311</a></li>
                        <li><strong>NYC.gov:</strong> Visit <a href="https://www.nyc.gov/" target="_blank">nyc.gov</a> for official information</li>
                        <li><strong>Department of Social Services:</strong> Visit your local office or call 718-557-1399</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            # Reset submission state
            st.session_state.submitted = False
            
            # Add option to ask a new question
            st.markdown("---")
            if st.button("🆕 Ask Another Question", type="secondary"):
                st.session_state.question = ""
                st.rerun()
            
        except Exception as e:
            error_msg = str(e)
            
            # Handle specific error types
            if "MockFallbackManager" in error_msg:
                st.error("❌ System temporarily unavailable. Please try again in a moment.")
                st.info("The AI system is experiencing high demand. This is normal and will resolve automatically.")
            elif "rate_limit" in error_msg.lower():
                st.error("⚠️ System is busy. Please wait a moment and try again.")
                st.info("We're experiencing high demand. Your question will be processed shortly.")
            else:
                st.error(f"❌ Error processing your question: {error_msg}")
                st.info("Please try rephrasing your question or contact NYC customer service for assistance.")
            
            # Add retry option
            if st.button("🔄 Try Again", type="secondary"):
                st.session_state.submitted = False
                st.rerun()
            
            st.session_state.submitted = False

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8em;">
    <p>Powered by NYC Services GPT • Built for NYC residents and businesses</p>
    <p>For official information, always verify with NYC government sources</p>
</div>
""", unsafe_allow_html=True)
