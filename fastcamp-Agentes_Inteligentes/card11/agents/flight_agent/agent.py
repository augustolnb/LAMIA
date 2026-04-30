from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json
import uuid

flight_agent = Agent(
    name="flight_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Recommends flight options based on destination, dates, and budget.",
    instruction=(
        "Given a destination, dates, and budget, suggest 2-3 flight options. "
        "For each option, provide the airline name, a short description of the route (e.g., direct vs 1 stop), and estimated total price. "
        "Respond in plain English. Keep it concise and well-formatted."
    )
)

session_service = InMemorySessionService()
runner = Runner(
    agent=flight_agent,
    app_name="flight_app",
    session_service=session_service
)
USER_ID = "user_flights"

async def execute(request):
    current_session_id = f"session_flights_{uuid.uuid4().hex}"

    await session_service.create_session(
        app_name="flight_app",
        user_id=USER_ID,
        session_id=current_session_id
    )
    
    prompt = (
        f"User is flying to {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a budget of {request['budget']}. Suggest 2-3 flight options, each with airline name, route description, and estimated total price. "
        f"Respond in JSON format using the key 'flights' with a list of flight objects."
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    async for event in runner.run_async(user_id=USER_ID, session_id=current_session_id, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            try:
                parsed = json.loads(response_text)
                if "flights" in parsed and isinstance(parsed["flights"], list):
                    return {"flights": parsed["flights"]}
                else:
                    print("'flights' key missing or not a list in response JSON")
                    return {"flights": response_text}
            except json.JSONDecodeError as e:
                print("JSON parsing failed:", e)
                print("Response content:", response_text)
                return {"flights": response_text}
