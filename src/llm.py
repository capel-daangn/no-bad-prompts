from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


def load_model():
    return ChatOpenAI(model="gpt-4o-mini")
