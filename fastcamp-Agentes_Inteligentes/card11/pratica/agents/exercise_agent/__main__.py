from common.a2a_server import create_app
import agents.exercise_agent.agent as exercise_module

app = create_app(exercise_module)
