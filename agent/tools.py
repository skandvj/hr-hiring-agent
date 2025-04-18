from langchain_core.tools import tool
import json

@tool
def search_job_market(query: str) -> str:
    """Simulate searching job market trends for specific roles"""
    # In a production app, this would connect to a real API
    if "engineer" in query.lower():
        return json.dumps({
            "founding engineer": {
                "avg_salary": "$120,000-$150,000",
                "demand": "High",
                "skills_in_demand": ["Full-stack development", "System architecture", "DevOps", "Leadership"]
            }
        })
    elif "genai" in query.lower() or "ai" in query.lower():
        return json.dumps({
            "genai intern": {
                "avg_salary": "$30-40/hour",
                "demand": "Very High",
                "skills_in_demand": ["Python", "LangChain/LangGraph", "NLP", "Prompt Engineering"]
            }
        })
    else:
        return "No specific market data found for this role."

@tool
def draft_job_description(role: str, skills: list, experience_level: str) -> str:
    """Generate a job description draft based on role, skills and experience level"""
    # In production, this could use a more sophisticated template system
    templates = {
        "founding engineer": """# Founding Engineer
        
## About Us
We're a startup focused on innovation and growth. We're looking for a founding engineer to help build our product from the ground up.

## Responsibilities
- Design and implement core system architecture
- Build and deploy initial product versions
- Work directly with founders on product strategy
- Establish engineering processes and best practices

## Requirements
- {experience_level} experience in software development
- Skills in: {skills}
- Ability to work in a fast-paced environment
- Strong problem-solving abilities
""",
        "genai intern": """# GenAI Intern
        
## About Us
We're innovating in the AI space and looking for talented individuals to join our team.

## Responsibilities
- Assist in developing and fine-tuning AI models
- Implement and test prompt engineering techniques
- Contribute to our AI-powered products
- Learn from experienced AI engineers

## Requirements
- {experience_level} in AI/ML
- Skills in: {skills}
- Passion for AI and its applications
- Strong programming foundation
"""
    }
    
    # Format template with specific details
    role_key = "founding engineer" if "found" in role.lower() or "engineer" in role.lower() else "genai intern"
    skills_formatted = ", ".join(skills)
    
    return templates[role_key].format(experience_level=experience_level, skills=skills_formatted)

@tool
def create_hiring_checklist(role: str, timeline_weeks: int) -> str:
    """Create a hiring process checklist with timeline"""
    # Base checklist template
    checklist = {
        "Pre-Hiring": [
            {"task": "Finalize job description", "timeframe": "Week 1"},
            {"task": "Determine budget and compensation range", "timeframe": "Week 1"},
            {"task": "Set up applicant tracking system", "timeframe": "Week 1"}
        ],
        "Sourcing": [
            {"task": "Post job on job boards", "timeframe": "Week 1-2"},
            {"task": "Reach out to network for referrals", "timeframe": "Week 1-2"},
            {"task": "Consider recruiter if applicable", "timeframe": "Week 2"}
        ],
        "Screening": [
            {"task": "Review applications", "timeframe": "Weeks 2-3"},
            {"task": "Conduct initial screening calls", "timeframe": "Weeks 3-4"}
        ],
        "Interviewing": [
            {"task": "Technical/skills assessment", "timeframe": "Week 4"},
            {"task": "Team interviews", "timeframe": "Week 5"},
            {"task": "Final interview with founders", "timeframe": "Week 5"}
        ],
        "Decision & Onboarding": [
            {"task": "Make offer", "timeframe": "Week 6"},
            {"task": "Negotiate and finalize offer", "timeframe": "Week 6"},
            {"task": "Prepare onboarding plan", "timeframe": "Weeks 6-7"}
        ]
    }
    
    # Adjust timeline based on provided timeline_weeks
    if timeline_weeks < 6:
        # Compress timeline for faster hiring
        for stage in checklist:
            for task in checklist[stage]:
                # Simple compression algorithm - divide weeks by 2 if timeline is short
                week_text = task["timeframe"]
                if "Week" in week_text:
                    if "-" in week_text:
                        start, end = week_text.replace("Week", "").replace("Weeks", "").split("-")
                        new_start = max(1, int(int(start)/2))
                        new_end = max(new_start + 1, int(int(end)/2))
                        task["timeframe"] = f"Week {new_start}-{new_end}"
                    else:
                        week_num = int(week_text.replace("Week ", "").replace("Weeks ", ""))
                        new_week = max(1, int(week_num/2))
                        task["timeframe"] = f"Week {new_week}"
    
    # Add role-specific tasks
    if "engineer" in role.lower():
        checklist["Screening"].append({"task": "Code review or system design challenge", "timeframe": "Week 3"})
        checklist["Interviewing"].append({"task": "Technical deep dive with engineering team", "timeframe": "Week 4"})
    
    if "intern" in role.lower():
        checklist["Screening"].append({"task": "Review academic projects and coursework", "timeframe": "Week 3"})
        checklist["Interviewing"].append({"task": "AI/ML knowledge assessment", "timeframe": "Week 4"})
    
    return json.dumps(checklist, indent=2)