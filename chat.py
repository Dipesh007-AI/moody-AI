# chat.py
import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

# Import the mood.py file
import mood

load_dotenv()

# Initialize LLM
model = ChatOpenAI(
    model="openrouter/free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0.8,
)

current_mood = "happy"

print("--- MOODY AI INITIALIZED ---")
print("Available moods:", ", ".join(mood.MOODS.keys()))
print("Type 'mood: happy', 'mood: sad', or 'mood: angry' to change personality.\n")

while True:
    user_input = input("You: ").strip()
    
    if not user_input:
        continue
        
    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break
        
    # Switch mood dynamically
    if user_input.lower().startswith("mood:"):
        requested_mood = user_input.split(":", 1)[1].strip().lower()
        if requested_mood in mood.MOODS:
            current_mood = requested_mood
            print(f"[MOODY AI switched to {current_mood.upper()} mode]\n")
        else:
            print(f"[Unknown mood! Available: {', '.join(mood.MOODS.keys())}]\n")
        continue

    # Build prompt with system message from mood.py
    messages = [
        SystemMessage(content=mood.get_system_prompt(current_mood)),
        HumanMessage(content=user_input)
    ]
    
    response = model.invoke(messages)
    print(f"\nMOODY AI ({current_mood.upper()}): {response.content}\n")