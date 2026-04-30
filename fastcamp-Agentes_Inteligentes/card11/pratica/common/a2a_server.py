from fastapi import FastAPI

def create_app(agent_module):
    app = FastAPI(title=f"API - {agent_module.__name__}")
    @app.post("/run")
    async def run(payload: dict):
        return await agent_module.execute(payload)
    return app
