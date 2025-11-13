# RepurAgent Demo - Standalone Deployment

This demo folder contains all necessary components to run the RepurAgent conversation display system as a standalone application.

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Setup**
   - Edit `.env` file and add your API keys:
   ```bash
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Run the Demo**
   ```bash
   streamlit run conversation_demo.py --server.port 8502 --server.headless true
   ```

## Features

✅ **Identical Visual Structure**: Uses the exact same UI components as the main app  
✅ **Thread Management**: Full sidebar with conversation switching capabilities  
✅ **Advanced Formatting**: All agent output separation and tool call formatting  
✅ **Progress Tracking**: Expandable sections for agent activity  
✅ **Content Deduplication**: Same duplicate prevention system  
✅ **Episodic Learning UI**: Compatible with all main app features

## What You'll See

The demo provides an **identical experience** to the main app, showing:
- 🧬 Same header with logo and title
- 📋 Full sidebar with thread management
- 💬 Complete conversation history with proper formatting
- 🔄 Agent progress separation (expandable sections)
- 🛠️ Tool call visualization with syntax highlighting

## What's Included

- **conversation_demo.py** - Main Streamlit application
- **app/** - UI components and configuration
- **backend/** - Memory management and conversation handling  
- **core/** - Agent system and supervisor
- **images/** - Logo and assets
- **requirements.txt** - All Python dependencies

## Deployment

This demo is designed to be deployed as a standalone Streamlit application. All dependencies and assets are self-contained within this folder.

For production deployment, consider:
- Setting proper environment variables
- Configuring database paths for your deployment environment
- Setting up proper logging and monitoring