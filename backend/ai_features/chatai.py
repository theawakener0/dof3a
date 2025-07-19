from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
import parserdb

def get_chat_model():
    return ChatVertexAI(model="gemini-1.5-flash-001")

def chatmodel(input):
    userdb = ""

    
    
