#!/usr/bin/env python3
"""
Conversation Display Demo for RepurAgent System

This demo replicates the main app's visual structure and functionality 
to showcase all conversation threads in the system.
"""

import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
import streamlit as st

from app.config import APP_TITLE, LOGO_PATH, SQLITE_DB_PATH, logger
from backend.memory.episodic_memory.thread_manager import load_thread_ids
from backend.memory.episodic_memory.conversation import (
    get_conversation_history_from_sqlite,
    reconstruct_formatted_message_from_sqlite,
    get_welcome_message,
    load_conversation
)
from app.ui.components import display_header, display_sidebar, display_chat_messages
from app.ui.formatters import (
    pretty_print_tool_call,
    separate_agent_outputs, 
    reconstruct_assistant_response
)
from core.supervisor.supervisor import create_app


def initialize_demo_session():
    """Initialize session state exactly like the main app."""
    # Initialize episodic learning system (for compatibility)
    if 'episodic_orchestrator' not in st.session_state:
        try:
            from backend.memory.episodic_memory.episodic_learning import get_orchestrator
            st.session_state.episodic_orchestrator = get_orchestrator()
        except Exception as e:
            logger.warning(f"Could not initialize episodic learning: {e}")
            st.session_state.episodic_orchestrator = None
    
    # Initialize thread-specific file upload tracking (for compatibility)
    if 'thread_files' not in st.session_state:
        st.session_state.thread_files = {}
    
    # Initialize file upload state (for compatibility)
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'uploaded_file_path' not in st.session_state:
        st.session_state.uploaded_file_path = None
    if 'uploaded_file_hash' not in st.session_state:
        st.session_state.uploaded_file_hash = None
    if 'uploaded_file_name' not in st.session_state:
        st.session_state.uploaded_file_name = None
    
    # Initialize episodic learning settings
    if 'use_episodic_learning' not in st.session_state:
        st.session_state.use_episodic_learning = True
    
    # Initialize content deduplication tracking
    if 'processed_content_hashes' not in st.session_state:
        st.session_state.processed_content_hashes = set()
    
    # Initialize expander states for UI persistence
    if 'expander_states' not in st.session_state:
        st.session_state.expander_states = {
            'progress_expander': True,
            'show_progress_content': False
        }
    
    # Load existing thread IDs
    if 'thread_ids' not in st.session_state:
        st.session_state.thread_ids = load_thread_ids()

    # Initialize current conversation if none exists
    if 'current_thread_id' not in st.session_state:
        if st.session_state.thread_ids:
            # Load the most recent conversation
            recent_thread = st.session_state.thread_ids[-1]
            try:
                app = create_app(use_episodic_learning=False)
                load_conversation(recent_thread["thread_id"], app)
            except Exception as e:
                logger.error(f"Error loading conversation: {e}")
                # Fallback to basic initialization
                st.session_state.current_thread_id = recent_thread["thread_id"]
                st.session_state.messages = [get_welcome_message()]
                st.session_state.processed_message_ids = set()
                st.session_state.processed_tools_ids = set()
        else:
            # Create a new conversation (fallback)
            from backend.memory.episodic_memory.conversation import create_new_conversation
            new_conv = create_new_conversation()
            st.session_state.current_thread_id = new_conv["thread_id"]
            st.session_state.messages = new_conv["messages"]
            st.session_state.processed_message_ids = new_conv["processed_message_ids"]
            st.session_state.processed_tools_ids = new_conv["processed_tools_ids"]
            st.session_state.thread_ids = load_thread_ids()
    
    # Initialize waiting state (for compatibility)
    if 'waiting_for_approval' not in st.session_state:
        st.session_state.waiting_for_approval = False
    if 'current_plan' not in st.session_state:
        st.session_state.current_plan = None
    if 'approval_interrupted' not in st.session_state:
        st.session_state.approval_interrupted = False


def set_page_config():
    """Set page configuration."""
    st.set_page_config(
        page_title=f"{APP_TITLE} - Demo",
        page_icon="🧬",
        layout="wide"
    )


def add_demo_info():
    """Add demo-specific information to the main content area."""
    st.info("🎯 **Demo Mode**: This is a read-only demonstration of the conversation display system. All formatting capabilities from the main app are preserved here.")


def update_current_thread_files():
    """Update current session uploaded_files with current thread's files (compatibility function)."""
    if 'current_thread_id' in st.session_state:
        thread_id = st.session_state.current_thread_id
        thread_files = st.session_state.thread_files.get(thread_id, [])
        st.session_state.uploaded_files = thread_files


def main():
    """Main demo application using the exact same structure as the main app."""
    # Set page configuration
    set_page_config()
    
    # Initialize session state exactly like main app
    initialize_demo_session()
    
    # Display header using main app component
    display_header()
    
    # Add demo-specific info
    add_demo_info()
    
    # Create app for sidebar compatibility
    try:
        app = create_app(use_episodic_learning=False)
    except Exception as e:
        logger.warning(f"Could not create app for demo: {e}")
        app = None
    
    # Display sidebar using main app component
    display_sidebar(app)
    
    # Display all messages using main app component
    display_chat_messages(st.session_state.messages)


if __name__ == "__main__":
    main()