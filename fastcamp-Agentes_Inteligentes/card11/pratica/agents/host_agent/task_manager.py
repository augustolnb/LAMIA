import asyncio
from common.a2a_client import call_agent

# URLs dos microsserviços locais
THEORY_URL = "http://localhost:8001/run"
EXERCISE_URL = "http://localhost:8002/run"
PKM_URL = "http://localhost:8003/run"

async def coordinate_lesson_plan(payload: dict):
    print(f"Iniciando planejamento para: {payload.get('topico', 'Aula')}")
    
    # 1. CRIANDO AS TAREFAS (É aqui que a variável theory_task nasce)
    # A chamada call_agent não espera a resposta imediatamente, ela apenas cria a "promessa" (task)
    theory_task = call_agent(THEORY_URL, payload)
    exercise_task = call_agent(EXERCISE_URL, payload)
    
    # 2. EXECUTANDO EM PARALELO
    # Aqui o Python finalmente olha para as variáveis acima e espera as duas terminarem juntas
    theory_res, exercise_res = await asyncio.gather(theory_task, exercise_task)
    
    # 3. EXTRAINDO O TEXTO
    # Garantimos que pegamos apenas o texto bruto para não quebrar a formatação do Obsidian
    texto_teoria = theory_res.get("explicacao", "Erro: Nenhuma teoria retornada.")
    texto_exercicios = exercise_res.get("questoes", "Erro: Nenhum exercício retornado.")
    
    # 4. ENVIANDO PARA O AGENTE PKM (Obsidian)
    pkm_payload = {
        "content": f"{texto_teoria}\n\n{texto_exercicios}",
        "metadata": payload
    }
    
    # Esta chamada precisa aguardar (await) os agentes anteriores terminarem
    obsidian_note = await call_agent(PKM_URL, pkm_payload)
    
    # 5. RETORNO FINAL PARA O STREAMLIT
    return {
        "teoria": texto_teoria,
        "exercicios": texto_exercicios,
        "obsidian_markdown": obsidian_note.get("markdown", "Erro ao gerar Markdown.")
    }
