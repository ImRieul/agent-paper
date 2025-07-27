# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Setup and Installation
```bash
# Install UV package manager
pip install uv

# Install dependencies
crewai install

# Setup environment
cp .env.sample .env
# Add OPENAI_API_KEY to .env file
```

### Running the Application
```bash
# Main command to run the full workflow
crewai run

# Alternative entry points
python -m agent_paper.main
kickoff  # Script entry point
```

### Development and Testing
```bash
# Run individual crew modules
python src/agent_paper/crews/initialize/initialize.py
python src/agent_paper/crews/analysis/analysis.py
python src/agent_paper/crews/outline/outline.py
python src/agent_paper/crews/section_loop/section_loop.py
```

## Code Architecture

### Multi-Agent Workflow System
This is a CrewAI-based multi-agent system that generates research papers through a structured 5-stage workflow:

1. **Initialize** (`src/agent_paper/crews/initialize/`) - Requirements gathering from user
2. **Analysis** (`src/agent_paper/crews/analysis/`) - Topic analysis and research
3. **Outline** (`src/agent_paper/crews/outline/`) - Document structure generation  
4. **Section Loop** (`src/agent_paper/crews/section_loop/`) - Individual section writing
5. **Assemble** (`src/agent_paper/crews/assemble/`) - Final document assembly (currently unused)

### Core Components

**Flow Management** (`src/agent_paper/main.py`)
- `AgentPaperFlow` inherits from CrewAI's `Flow` class
- Uses decorators: `@start()`, `@listen()`, `@router()` for workflow control
- Manages state transitions and crew coordination
- Implements file existence checks to skip completed stages

**State Management** (`src/agent_paper/state.py`)  
- `AgentPaperState` - Main state container
- `OutlineStructure` - Document structure with sections
- `OutlineSection` - Individual section with recursive subsections
- Uses Pydantic models for validation and serialization

**Configuration** (`src/config.py`)
- Centralized path management for output files
- `OUTPUT_DIR` for generated content (`output/`)
- `GUIDE_PATH` for final document (`output/guide.md`)

### Agent Configuration Pattern
Each crew has YAML configuration files in `config/` subdirectories:
- `agents.yaml` - Defines agent roles, goals, backstories, and LLM settings
- `tasks.yaml` - Defines specific tasks with descriptions and expected outputs

All agents use `openai/gpt-4o-mini` by default with `max_iter: 3`.

### File Flow and Persistence
- Requirements → `output/requirements.md`
- Analysis → `output/analysis_result.md`, `output/analysis_summary.md`  
- Outline → `output/outline.json` (JSON structure)
- Final guide → `output/guide.md`

The main workflow checks for existing files and skips completed stages, enabling resumable execution.

## Key Design Patterns

**Flow-Based Architecture**: Uses CrewAI Flow decorators for declarative workflow definition rather than imperative control flow.

**State Persistence**: Critical data is persisted to JSON/markdown files between stages, allowing for workflow resumption and debugging.

**Crew Isolation**: Each stage is implemented as a separate crew with its own agents and tasks, promoting modularity.

**Progressive Content Building**: Each section loop iteration builds upon previous sections, maintaining narrative continuity.

## Environment Requirements
- Python 3.10+ (< 3.13)
- OpenAI API key in `.env` file
- UV package manager for dependency management