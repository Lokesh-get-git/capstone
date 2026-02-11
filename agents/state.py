from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from models.data_models import ResumeClaim, InterviewQuestion
import operator

class AgentState(TypedDict):
    raw_text: str
    sections: Dict[str, dict]
    claims: Annotated[List[ResumeClaim], operator.add]
    questions: Annotated[List[InterviewQuestion], operator.add]
    messages: Annotated[List[BaseMessage], add_messages]
    metadata: Dict[str, Any]