
from langchain.agents import AgentExecutor, Tool
from langchain.tools import GmailSearch, GmailModify

tools = [
    Tool(name="Email Fetcher", func=fetch_emails, description="Fetch unread emails"),
    Tool(name="Label Applier", func=apply_label, description="Apply Gmail labels")
]
agent = AgentExecutor(tools=tools, llm=llm)
agent.run("Monitor emails and label them.")