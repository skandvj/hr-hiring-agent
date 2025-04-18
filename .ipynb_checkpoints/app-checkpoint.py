import os
import streamlit as st
from dotenv import load_dotenv
import json
import pandas as pd
import uuid
import traceback
from agent.agent import create_hr_agent
from agent.memory import SessionMemory, AnalyticsTracker
from langchain_core.messages import AIMessage, HumanMessage


# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Make sure directories exist
os.makedirs("data/session_data", exist_ok=True)
os.makedirs("data/analytics", exist_ok=True)

# App title and configuration
st.set_page_config(
    page_title="HR Hiring Agent",
    page_icon="👥",
    layout="wide"
)

# Create tabs for chat and analytics
tab1, tab2 = st.tabs(["Chat", "Analytics"])

with tab1:
    st.title("HR Hiring Process Planner")
    st.subheader("Your AI assistant for planning startup hiring processes")
    
    # Initialize session state
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        try:
            st.session_state.agent = create_hr_agent(OPENAI_API_KEY, st.session_state.session_id)
            st.session_state.memory = SessionMemory(st.session_state.session_id)
            st.session_state.analytics = AnalyticsTracker(st.session_state.session_id)
            # Add a welcome message
            st.session_state.messages.append({
                "role": "assistant",
                "content": "👋 Hi there! I'm your HR assistant. I can help you plan a hiring process for your startup. What roles are you looking to hire for?"
            })
        except Exception as e:
            st.error(f"Error initializing agent: {str(e)}")
            st.code(traceback.format_exc())
            st.stop()
    
    # Sidebar with session info and status
    with st.sidebar:
        st.header("Session Information")
        st.write(f"Session ID: {st.session_state.session_id}")
        
        # Session management dropdown
        st.subheader("Session Management")
        sessions_dir = os.path.join("data", "session_data")
        os.makedirs(sessions_dir, exist_ok=True)
        sessions = [f for f in os.listdir(sessions_dir) if f.endswith(".json")]
        
        if sessions:
            session_options = ["Current Session"] + sessions
            selected_session = st.selectbox("Load Previous Session", session_options)
            
            if selected_session != "Current Session" and selected_session != st.session_state.session_id + ".json":
                try:
                    # Load the selected session
                    new_session_id = selected_session.replace(".json", "")
                    st.session_state.session_id = new_session_id
                    st.session_state.memory = SessionMemory(new_session_id)
                    st.session_state.agent = create_hr_agent(OPENAI_API_KEY, new_session_id)
                    st.session_state.analytics = AnalyticsTracker(new_session_id)
                    
                    # Load previous messages
                    st.session_state.messages = []
                    conversation_history = st.session_state.memory.get("conversation_history") or []
                    
                    for message in conversation_history:
                        st.session_state.messages.append({
                            "role": message["role"],
                            "content": message["content"]
                        })
                    
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error loading session: {str(e)}")
        
        # Add button to start a new session
        if st.button("Start New Session"):
            try:
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.messages = []
                st.session_state.agent = create_hr_agent(OPENAI_API_KEY, st.session_state.session_id)
                st.session_state.memory = SessionMemory(st.session_state.session_id)
                st.session_state.analytics = AnalyticsTracker(st.session_state.session_id)
                # Add a welcome message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "👋 Hi there! I'm your HR assistant. I can help you plan a hiring process for your startup. What roles are you looking to hire for?"
                })
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error creating new session: {str(e)}")
        
        # Display current hiring needs
        st.subheader("Current Hiring Needs")
        hiring_needs = st.session_state.memory.get("hiring_needs") or {}
        
        if hiring_needs:
            for role, details in hiring_needs.items():
                st.write(f"**Role:** {role}")
                # Display skills if available
                if "skills" in hiring_needs and role in hiring_needs["skills"]:
                    skills = hiring_needs["skills"][role]
                    st.write(f"**Skills:** {', '.join(skills)}")
                # Display experience if available
                if "experience" in hiring_needs and role in hiring_needs["experience"]:
                    experience = hiring_needs["experience"][role]
                    st.write(f"**Experience:** {experience}")
                # Display budget if available
                if "budget" in hiring_needs and role in hiring_needs["budget"]:
                    budget = hiring_needs["budget"][role]
                    st.write(f"**Budget:** {budget}")
                st.write("---")
        else:
            st.write("No hiring needs defined yet.")
        
        # Add example prompts
        st.subheader("Example Prompts")
        example_prompts = [
            "I need to hire a founding engineer and a GenAI intern. Can you help?",
            "What's a typical timeline for hiring a technical co-founder?",
            "What skills should I look for in a GenAI specialist?",
            "I have a budget of $120K for an engineer. Is that reasonable?"
        ]
        
        for prompt in example_prompts:
            if st.button(prompt):
                # Use session_state to store the selected prompt
                st.session_state.selected_prompt = prompt
                st.experimental_rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # If there are job descriptions or hiring plans in the message, show them in expandable sections
            if "job descriptions" in message["content"].lower() and "I've created job descriptions" in message["content"]:
                # Extract job descriptions from the memory
                hiring_details = st.session_state.memory.get("hiring_needs") or {}
                if "job_descriptions" in hiring_details:
                    for role, desc in hiring_details["job_descriptions"].items():
                        with st.expander(f"View {role.upper()} Job Description", expanded=False):
                            st.markdown(desc)
            
            if "hiring plan" in message["content"].lower() and "I've created a hiring plan" in message["content"]:
                # Extract hiring plans from the memory
                hiring_details = st.session_state.memory.get("hiring_needs") or {}
                if "hiring_plan" in hiring_details:
                    for role, plan_json in hiring_details["hiring_plan"].items():
                        with st.expander(f"View {role.upper()} Hiring Plan", expanded=False):
                            try:
                                plan = json.loads(plan_json)
                                for stage, tasks in plan.items():
                                    st.subheader(stage)
                                    for task in tasks:
                                        st.write(f"- {task['task']} ({task['timeframe']})")
                            except Exception as e:
                                st.write(plan_json)
                                st.write(f"Error parsing plan: {str(e)}")
    
    # User input
    user_input = st.chat_input("Type your message here...")
    
    # Check if there's a selected prompt from the example buttons
    if "selected_prompt" in st.session_state:
        user_input = st.session_state.selected_prompt
        # Clear the selected prompt
        del st.session_state.selected_prompt
    
    if user_input:
        # Add user input to messages
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        
        # Track message in analytics
        st.session_state.analytics.track_message("user", user_input)
        
        # Check for role mentions to track in analytics
        if "engineer" in user_input.lower():
            st.session_state.analytics.track_role_request("founding engineer")
        if "intern" in user_input.lower() or "genai" in user_input.lower():
            st.session_state.analytics.track_role_request("genai intern")
        
        # Get response from agent
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Create input state for the agent
                    input_state = {
                        "messages": [{"role": "human", "content": user_input}]
                    }
                    
                    # Get response from the agent
                    response = st.session_state.agent.invoke(input_state)
                    
                    # Extract the assistant's message from the response
                    assistant_response = ""
                    if "messages" in response:
                        for message in response["messages"]:
                            if hasattr(message, "type") and message.type == "ai":
                                assistant_response = message.content
                            elif isinstance(message, AIMessage):
                                assistant_response = message.content
                            elif isinstance(message, dict) and message.get("role") == "assistant":
                                assistant_response = message.get("content", "")
                    
                    if not assistant_response:
                        # Fall back to a simple response if we couldn't extract one
                        assistant_response = "I'm processing your request. Could you provide more details about your hiring needs?"
                    
                    # Display the response
                    st.write(assistant_response)
                    
                    # Add to messages
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                    
                    # Track message in analytics
                    st.session_state.analytics.track_message("assistant", assistant_response)
                    
                    # Check for tool usage in the response
                    if "search_job_market" in assistant_response:
                        st.session_state.analytics.track_tool_usage("search_job_market")
                    if "draft_job_description" in assistant_response:
                        st.session_state.analytics.track_tool_usage("draft_job_description")
                    if "create_hiring_checklist" in assistant_response:
                        st.session_state.analytics.track_tool_usage("create_hiring_checklist")
                
                except Exception as e:
                    error_msg = f"Error getting response from agent: {str(e)}"
                    st.error(error_msg)
                    st.code(traceback.format_exc())
                    
                    # Add error message to chat
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": "I'm sorry, I encountered an error processing your request. Please try again or start a new session."
                    })

with tab2:
    st.header("Usage Analytics")
    
    try:
        # Get analytics data
        analytics = st.session_state.analytics
        stats = analytics.get_usage_stats()
        
        # Display analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Sessions", stats["total_sessions"])
            st.metric("Most Requested Role", stats["most_requested_role"] or "None")
        
        with col2:
            st.metric("Avg. Session Duration", f"{stats['avg_session_duration']:.1f}s")
            
        # Top tools used
        st.subheader("Top Tools Used")
        if stats["top_tools"]:
            for tool, count in stats["top_tools"]:
                st.write(f"- {tool}: {count} times")
        else:
            st.write("No tools used yet")
        
        # Show role request distribution
        analytics_data = analytics._load_analytics()
        if analytics_data["role_requests"]:
            st.subheader("Role Request Distribution")
            role_data = list(analytics_data["role_requests"].items())
            roles = [item[0] for item in role_data]
            counts = [item[1] for item in role_data]
            
            # Create a dataframe for the chart
            df = pd.DataFrame({
                "role": roles,
                "count": counts
            })
            
            # Create a simple bar chart
            st.bar_chart(df, x="role", y="count")
        
        # Session activity over time
        if len(analytics_data["sessions"]) > 1:
            st.subheader("Session Activity")
            sessions = analytics_data["sessions"]
            session_dates = [s["start_time"].split("T")[0] for s in sessions]
            session_count_by_date = {}
            
            for date in session_dates:
                if date not in session_count_by_date:
                    session_count_by_date[date] = 0
                session_count_by_date[date] += 1
            
            dates = list(session_count_by_date.keys())
            counts = list(session_count_by_date.values())
            
            # Create a dataframe for the line chart
            df = pd.DataFrame({
                "date": dates,
                "sessions": counts
            })
            
            # Create a line chart
            st.line_chart(df, x="date", y="sessions")
    
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")
        st.code(traceback.format_exc())