from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


class ResumeClaim(BaseModel):
    text: str
    section: str


class InterviewQuestion(BaseModel):
    question: str
    target_claim: str
    reasoning: str



