import base64
import streamlit as st
from typing import List, Dict
from app.config import APP_TITLE, LOGO_PATH, SQLITE_DB_PATH
from backend.memory.episodic_memory.thread_manager import load_thread_ids, remove_thread_id
from backend.memory.episodic_memory.conversation import create_new_conversation
from app.ui.formatters import split_content_with_tool_blocks


def get_image_base64(file_path: str) -> str:
    """Convert image to base64 string."""
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def display_header():
    """Display the application header with logo."""
    try:
        logo_base64 = get_image_base64(LOGO_PATH)
        
        st.markdown(
            f"""
            <div style="display: flex; align-items: center;">
                <img src="data:image/png;base64,{logo_base64}" width="60" style="margin-right: 10px;">
                <h1 style="margin: 0;">{APP_TITLE}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        # Fallback to text-only header
        st.title(APP_TITLE)


def display_sidebar(app) -> None:
    """Display the sidebar with conversation management."""

    with st.sidebar:
        
        # Episodic Learning Section
        _display_episodic_learning_section()

        st.divider()

        st.header("Task Management")
        
        # New Conversation Button
        if st.button("New Task", use_container_width=True):
            st.rerun()
        
        
        
        st.divider()
        
        # Display conversation list from persistent storage
        _display_conversation_list(app)
        
        st.divider()
        
        # Display database info
        _display_database_info()
        


def _display_episodic_learning_section() -> None:
    """Display the episodic learning control section."""
    with st.expander("🧠 Episodic Learning", expanded=False):
        st.caption("Save patterns from this conversation for future use")
        
        # Single extract button
        if st.button("📚 Extract Learning", 
                    use_container_width=True,
                    help="Extract and save task patterns from current conversation"):
            st.rerun()
        
        # Display statistics
        if 'episodic_orchestrator' in st.session_state and st.session_state.episodic_orchestrator:
            try:
                status = st.session_state.episodic_orchestrator.get_system_status()
                total_episodes = status.get('episodic_system', {}).get('total_episodes', 0)
                st.caption(f"📊 Stored patterns: {total_episodes}")
            except:
                pass


def add_episodic_controls() -> None:
    """Add episodic learning controls to the sidebar."""
    if not st.session_state.episodic_orchestrator:
        return
        
    with st.sidebar:
        st.header("🔧 Learning Controls")
        
        # Toggle episodic learning
        st.session_state.use_episodic_learning = st.checkbox(
            "Use Episodic Learning", 
            value=st.session_state.get('use_episodic_learning', True)
        )
        
        try:
            orchestrator = st.session_state.episodic_orchestrator
            
            # Show system stats
            status = orchestrator.get_system_status()
            total_episodes = status.get('vector_store', {}).get('total_episodes', 0)
            st.metric("Total Episodes Learned", total_episodes)
                        
        except Exception as e:
            st.error(f"Error in learning controls: {e}")


def _display_conversation_list(app) -> None:
    """Display the list of conversations in the sidebar."""
    if st.session_state.thread_ids:
        for i, thread_data in enumerate(reversed(st.session_state.thread_ids)):  # Show most recent first
            thread_id = thread_data["thread_id"]
            is_current = thread_id == st.session_state.current_thread_id
            
            # Create a container for each conversation
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Conversation button
                    button_style = "🔵 " if is_current else "💬 "
                    conv_title = thread_data["title"]
                    if len(conv_title) > 30:
                        conv_title = conv_title[:30] + "..."
                    
                    if st.button(f"{button_style}{conv_title}", 
                               key=f"thread_{thread_id}", 
                               use_container_width=True,
                               disabled=is_current):
                        from backend.memory.episodic_memory.conversation import load_conversation
                        load_conversation(thread_id, app)
                        st.rerun()
                
                with col2:
                    # Delete button
                    if st.button("🗑️", key=f"del_{thread_id}", help="Delete conversation"):
                        st.rerun()



def _display_database_info() -> None:
    """Display database information in the sidebar."""
    st.caption(f"💾 Memory: {SQLITE_DB_PATH.name}")
    if SQLITE_DB_PATH.exists():
        size_mb = SQLITE_DB_PATH.stat().st_size / (1024 * 1024)
        st.caption(f"📊 Size: {size_mb:.2f} MB")


def render_tool_call_block(block: str, *, label: str = "🛠️ Tools Calling", expanded: bool = False) -> None:
    """Render a single tool call block inside an expander."""
    if not block or not block.strip():
        return

    with st.expander(label, expanded=expanded):
        st.markdown(block.strip())


def render_tool_call_expander(tool_calls: List[str], *, label: str = "🛠️ Tools Calling", expanded: bool = False) -> None:
    """Render multiple tool call blocks, preserving their sequence."""
    if not tool_calls:
        return

    for block in tool_calls:
        render_tool_call_block(block, label=label, expanded=expanded)


def render_markdown_with_tool_blocks(markdown: str, *, label: str = "🛠️ Tools Calling", expanded: bool = False) -> None:
    """Render markdown interleaving tool call expanders in chronological order."""
    segments = split_content_with_tool_blocks(markdown)
    for segment_type, content in segments:
        if segment_type == "text":
            text = content.strip()
            if text:
                st.markdown(text)
        elif segment_type == "tool":
            render_tool_call_block(content, label=label, expanded=expanded)


def display_chat_messages(messages: List[Dict[str, str]]) -> None:
    """Display chat messages in the main area with enhanced formatting for agent outputs."""
    for message in messages:
        with st.chat_message(message["role"]):
            content = message["content"]
            
            # Check if this is an assistant message with agent outputs
            if message["role"] == "assistant" and content:
                # Split content into progress agents (expander) and final agents (main display)
                progress_content = ""
                final_content = ""
                
                # Parse content to separate different agents while preserving chronological order
                lines = content.split('\n')
                current_section = "final"  # Default to final
                
                for line in lines:
                    # Check for agent headers to determine section
                    line_upper = line.upper()
                    if line.startswith('**') and line.endswith('**'):
                        if any(agent in line_upper for agent in ["SUPERVISOR", "RESEARCH_AGENT", "DATA_AGENT", "PREDICTION_AGENT"]):
                            current_section = "progress"
                        elif any(agent in line_upper for agent in ["PLANNING_AGENT", "REPORT_AGENT"]):
                            current_section = "final"
                        # For other agent headers, maintain current section
                    
                    # Add line to appropriate section
                    if current_section == "progress":
                        progress_content += line + '\n'
                    else:
                        final_content += line + '\n'
                
                # Display final content first (Planning and Report agents)
                if final_content.strip():
                    render_markdown_with_tool_blocks(final_content, label="🛠️ Tools Calling")
                
                # Display progress content in expander if it exists
                if progress_content.strip():
                    # For historical messages, always show expander if there's content
                    with st.expander("🔄 Processing Progress", expanded=False):
                        render_markdown_with_tool_blocks(
                            progress_content,
                            label="🛠️ Tools Calling",
                            expanded=False
                        )
            else:
                # Regular display for user messages or simple assistant messages
                st.markdown(content)
