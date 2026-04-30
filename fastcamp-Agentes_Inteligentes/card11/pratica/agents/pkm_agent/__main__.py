from common.a2a_server import create_app
import agents.pkm_agent.agent as pkm_module

app = create_app(pkm_module)
