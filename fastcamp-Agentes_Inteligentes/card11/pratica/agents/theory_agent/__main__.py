from common.a2a_server import create_app
import agents.theory_agent.agent as theory_module

app = create_app(theory_module)
