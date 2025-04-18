SYSTEM_PROMPT = """You are an expert HR assistant for startups, specializing in helping plan hiring processes.
Your goal is to help HR professionals and startup founders plan effective hiring processes for various roles.

You should:
1. Ask clarifying questions about their hiring needs (budget, skills, timeline, etc.)
2. Suggest appropriate job descriptions based on their requirements
3. Create hiring checklists and plans
4. Present results in a structured and useful format

Be helpful, concise, and focused on providing actionable hiring guidance.
"""

CLARIFICATION_PROMPT = """Based on the user's request to hire {roles}, I need to gather more information.
What specific details should I ask about to help create an effective hiring plan?
Consider budget, required skills, experience level, timeline, and any other relevant factors.
"""

# Define prompt templates for different stages of the process
JOB_DESCRIPTION_TEMPLATE = """
Create a job description for the role of {role} with the following requirements:
- Skills: {skills}
- Experience level: {experience}
- Company stage: {company_stage}

The job description should be professional, compelling, and highlight the key responsibilities and requirements.
"""

HIRING_PLAN_TEMPLATE = """
Based on the information gathered:
- Role: {role}
- Required skills: {skills}
- Experience level: {experience}
- Timeline: {timeline} weeks
- Budget: {budget}

Create a detailed hiring plan including sourcing strategy, interview process, and timeline.
"""