"""
NYC Services GPT API Server
TODO: implement API endpoints for user queries to achieve Self-Service Success Rate ≥ 90% as specified in PROJECT_SPEC.md
"""

from flask import Flask, request, jsonify
from ..config import config

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def handle_query():
    """Handle user queries and return RAG-powered responses"""
    # TODO: implement query processing with RAG pipeline
    pass

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    api_config = config.get_api_config()
    app.run(debug=api_config['debug'], host=api_config['host'], port=api_config['port']) 