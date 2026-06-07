from backend.agents.resume_agent import ResumeAgent

agent = ResumeAgent()

resume = agent.parse("uploads/resume2.pdf")

print("\n====================")
print("NAME:", resume.name)
print("EMAIL:", resume.email)
print("PHONE:", resume.phone)
print("SKILLS:", resume.skills)
print("====================")