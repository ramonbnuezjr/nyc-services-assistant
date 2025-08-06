# NYC Services GPT

A one-stop helper over NYC Open Data / DSS docs that lets users self-serve without human intervention.

## Objective

Deliver a RAG-powered assistant that provides accurate, helpful responses to NYC service-related queries with a target **Self-Service Success Rate ≥ 90%**.

## Key Metrics

- **Primary KPI**: Self-Service Success Rate (% of queries fully answered without human fallback)
- **Baseline Target**: ≥ 90% by Day 14 post-launch
- **Measurement**: 100 synthetic queries across 5 NYC services

## Project Structure

```
nyc_services_gpt_rag/
├── src/
│   ├── api/          # API endpoints and web interface
│   ├── ingest/       # Data ingestion and processing
│   ├── retrieve/     # RAG retrieval and search
│   ├── models/       # LLM models and prompts
│   └── tests/        # Test suite and evaluation
├── PROJECT_SPEC.md   # Detailed MVP requirements
├── ACTIVITY_LOG.md   # Development progress tracking
└── IMPROVEMENTS.md   # Post-MVP backlog
```

## Setup

### Prerequisites

- Python 3.8+
- OpenAI API key
- NYC Open Data access

### Installation

```bash
# Clone repository
git clone <repository-url>
cd nyc_services_gpt_rag

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-api-key"
```

## Key Commands

### Development

```bash
# Run tests
python -m pytest src/tests/

# Run baseline evaluation
python src/tests/baseline_evaluation.py

# Start API server
python src/api/server.py
```

### Data Processing

```bash
# Ingest NYC service data
python src/ingest/data_processor.py

# Build vector database
python src/retrieve/vector_store.py
```

### Evaluation

```bash
# Run synthetic query evaluation
python src/tests/synthetic_evaluation.py

# Generate success rate report
python src/tests/success_rate_calculator.py
```

## Success Criteria

### MVP Acceptance Criteria

1. **Baseline Measurement**: Run 100 synthetic queries through RAG pipeline
2. **Success Rate**: ≥ 90% of queries answered correctly without human fallback
3. **Coverage**: Support for 5 key NYC services:
   - Unemployment Benefits
   - SNAP (Food Stamps)
   - Medicaid (Health Coverage)
   - Cash Assistance
   - Child Care Subsidy

### Evaluation Protocol

1. Assemble 100 synthetic queries across top 5 services
2. Run through RAG pipeline without prompt-tuning
3. Annotate responses as "Correct" or "Needs Human"
4. Compute Self-Service Success Rate = (#Correct / 100) × 100

## Persona Example

**Maria the Micro-Entrepreneur**
- Single mother running a pop-up café
- Unfamiliar with NYC licensing
- Needs plain-language answers about permits & benefits in ≤20 sec
- Acceptance: Given "food cart permit" question, returns 3 relevant steps with links, ≥90% accuracy

## Development Workflow

1. **Week 0**: ✅ Implement baseline RAG pipeline
   - ✅ Project structure scaffolded
   - ✅ API connectivity verified
   - ✅ Ingestion chunker module complete
2. **Week 1**: Run 100-query pilot (expect 50-60% success rate)
3. **Week 2**: Optimize prompts and retrieval
4. **Day 14**: Achieve ≥ 90% Self-Service Success Rate

## Current Status

**✅ Completed:**
- Ingestion chunker module complete (tested)
- API connectivity verified (OpenAI, Gemini, ElevenLabs)
- Project structure scaffolded with TODO comments

**🔄 Next Up:**
- Data processor & vector store implementation
- RAG pipeline integration
- Synthetic query evaluation framework

## Out-of-Scope (MVP)

- Time-to-Answer metrics
- Page-Click Reduction tracking
- Multi-language support
- Dark mode UI

## Contributing

1. Follow the TODO comments in each module
2. Reference PROJECT_SPEC.md for requirements
3. Log activities in ACTIVITY_LOG.md
4. Add improvements to IMPROVEMENTS.md

## License

[Add license information] 