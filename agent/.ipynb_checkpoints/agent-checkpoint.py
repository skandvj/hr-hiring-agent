from typing import Dict, List, Any, Optional
import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from .tools import search_job_market, draft_job_description, create_hiring_checklist
from .memory import SessionMemory
from .prompts import SYSTEM_PROMPT

def create_hr_agent(openai_api_key: str, session_id: str = None):
    """Create and return the HR hiring agent"""
    # Initialize the memory
    memory = SessionMemory(session_id)
    
    # Initialize the LLM
    llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4o", temperature=0.5)
    
    # Create the main prompt
    hr_prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])
    
    # Create a simple chain
    chain = hr_prompt | llm | StrOutputParser()
    
    class HRAgent:
        def __init__(self, chain, memory, tools):
            self.chain = chain
            self.memory = memory
            self.tools = tools
            self.job_descriptions = {}
            self.hiring_plans = {}
            self.hiring_details = {
                "roles": [],
                "skills": {},
                "experience": {},
                "timeline": None,
                "budget": {}
            }
        
        def invoke(self, input_state):
            """Process the input and generate a response"""
            # Extract messages from input state
            user_messages = input_state.get("messages", [])
            if not user_messages:
                return {"messages": []}
            
            # Get the latest user message
            latest_message = user_messages[-1]
            user_input = latest_message.get("content", "")
            
            # Get chat history from memory
            chat_history = self._get_chat_history()
            
            # Check if we need to process any tools directly
            if "generate job description" in user_input.lower() or "create job description" in user_input.lower():
                return self._generate_job_descriptions(chat_history)
            
            if "hiring plan" in user_input.lower() or "checklist" in user_input.lower():
                return self._generate_hiring_plans(chat_history)
            
            # Run the chain to get a response
            response = self.chain.invoke({
                "chat_history": chat_history,
                "input": user_input
            })
            
            # Update memory
            self.memory.add_to_conversation("human", user_input)
            self.memory.add_to_conversation("ai", response)
            
            # Extract hiring details from the conversation
            self._extract_hiring_details(user_input, response)
            
            # Return the response
            ai_message = AIMessage(content=response)
            return {"messages": [ai_message]}
        
        def _get_chat_history(self):
            """Get formatted chat history from memory"""
            conversation = self.memory.get("conversation_history") or []
            chat_history = []
            
            for message in conversation:
                if message["role"] == "human":
                    chat_history.append(HumanMessage(content=message["content"]))
                elif message["role"] == "ai":
                    chat_history.append(AIMessage(content=message["content"]))
            
            return chat_history
        
        def _extract_hiring_details(self, user_input, response):
            """Extract hiring details from conversation"""
            combined_text = (user_input + " " + response).lower()
            
            # Extract roles
            if "founding engineer" in combined_text or "engineer" in combined_text:
                if "founding engineer" not in self.hiring_details["roles"]:
                    self.hiring_details["roles"].append("founding engineer")
            
            if "genai intern" in combined_text or "intern" in combined_text:
                if "genai intern" not in self.hiring_details["roles"]:
                    self.hiring_details["roles"].append("genai intern")
            
            # Extract skills (simplified)
            if "skill" in combined_text:
                if "founding engineer" in self.hiring_details["roles"] and "founding engineer" not in self.hiring_details["skills"]:
                    self.hiring_details["skills"]["founding engineer"] = ["Full-stack development", "System architecture", "DevOps"]
                
                if "genai intern" in self.hiring_details["roles"] and "genai intern" not in self.hiring_details["skills"]:
                    self.hiring_details["skills"]["genai intern"] = ["Python", "ML/AI fundamentals", "LangChain/LangGraph"]
            
            # Extract experience
            if "experience" in combined_text or "year" in combined_text:
                if "founding engineer" in self.hiring_details["roles"] and "founding engineer" not in self.hiring_details["experience"]:
                    self.hiring_details["experience"]["founding engineer"] = "3-5 years"
                
                if "genai intern" in self.hiring_details["roles"] and "genai intern" not in self.hiring_details["experience"]:
                    self.hiring_details["experience"]["genai intern"] = "Entry-level"
            
            # Extract timeline
            if "timeline" in combined_text or "week" in combined_text:
                self.hiring_details["timeline"] = 8  # Default to 8 weeks
            
            # Extract budget
            if "budget" in combined_text or "$" in combined_text or "salary" in combined_text:
                if "founding engineer" in self.hiring_details["roles"] and "founding engineer" not in self.hiring_details["budget"]:
                    self.hiring_details["budget"]["founding engineer"] = "$120,000-$150,000"
                
                if "genai intern" in self.hiring_details["roles"] and "genai intern" not in self.hiring_details["budget"]:
                    self.hiring_details["budget"]["genai intern"] = "$30-40/hour"
            
            # Update memory with extracted details
            self.memory.update("hiring_needs", self.hiring_details)
        
        def _generate_job_descriptions(self, chat_history):
            """Generate job descriptions using the tool"""
            if not self.hiring_details["roles"]:
                response = "I need to know which roles you're looking to hire for before I can create job descriptions. Could you please specify the roles?"
                self.memory.add_to_conversation("ai", response)
                return {"messages": [AIMessage(content=response)]}
            
            job_descriptions = {}
            for role in self.hiring_details["roles"]:
                skills = self.hiring_details["skills"].get(role, ["Relevant technical skills"])
                experience = self.hiring_details["experience"].get(role, "Appropriate")
                
                job_descriptions[role] = draft_job_description(
                    role=role,
                    skills=skills,
                    experience_level=experience
                )
            
            # Update the hiring details
            self.hiring_details["job_descriptions"] = job_descriptions
            self.memory.update("hiring_needs", self.hiring_details)
            
            # Create a response message
            response = "I've created job descriptions based on your requirements:\n\n"
            for role, desc in job_descriptions.items():
                response += f"## {role.upper()} JOB DESCRIPTION\n{desc}\n\n"
            response += "Would you like me to make any adjustments to these job descriptions or help create a hiring plan?"
            
            self.memory.add_to_conversation("ai", response)
            return {"messages": [AIMessage(content=response)]}
        
        def _generate_hiring_plans(self, chat_history):
            """Generate hiring plans using the tool"""
            if not self.hiring_details["roles"]:
                response = "I need to know which roles you're looking to hire for before I can create hiring plans. Could you please specify the roles?"
                self.memory.add_to_conversation("ai", response)
                return {"messages": [AIMessage(content=response)]}
            
            timeline = self.hiring_details.get("timeline", 8)
            hiring_plans = {}
            
            for role in self.hiring_details["roles"]:
                hiring_plans[role] = create_hiring_checklist(
                    role=role,
                    timeline_weeks=timeline
                )
            
            # Update the hiring details
            self.hiring_details["hiring_plan"] = hiring_plans
            self.memory.update("hiring_needs", self.hiring_details)
            
            # Create a response message
            response = "Based on your requirements, I've created a hiring plan for each role:\n\n"
            for role, plan in hiring_plans.items():
                response += f"## {role.upper()} HIRING PLAN\n```json\n{plan}\n```\n\n"
            response += "Is there anything else you'd like me to help with regarding your hiring process?"
            
            self.memory.add_to_conversation("ai", response)
            return {"messages": [AIMessage(content=response)]}
    
    # Set up tools
    tools = {
        "search_job_market": search_job_market,
        "draft_job_description": draft_job_description,
        "create_hiring_checklist": create_hiring_checklist
    }
    
    # Create and return the agent
    return HRAgent(chain, memory, tools)