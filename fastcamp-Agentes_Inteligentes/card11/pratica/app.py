import streamlit as st
import asyncio
from agents.host_agent.task_manager import coordinate_lesson_plan

st.set_page_config(page_title="Augusto Soluções Inteligentes - Tutor AI", layout="wide")

st.title("🚀 Gerador de Aulas Multi-Agente")

with st.sidebar:
    materia = st.selectbox("Matéria", ["Física", "Matemática"])
    topico = st.text_input("Tópico da Aula", placeholder="Ex: Circuitos RLC")
    nivel = st.select_slider("Nível", ["Ensino Médio", "Técnico", "Graduação"])
    gerar = st.button("Gerar Material de Aula")

if gerar:
    payload = {"materia": materia, "topico": topico, "nivel": nivel, "foco": "Completo"}
    
    with st.spinner("Agentes trabalhando no seu material..."):
        result = asyncio.run(coordinate_lesson_plan(payload))
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📚 Teoria e Explicação")
            st.write(result["teoria"])
        with col2:
            st.subheader("📝 Exercícios Propostos")
            st.write(result["exercicios"])
            
        st.divider()
        st.subheader("📂 Formato Obsidian (Zettelkasten)")
        st.code(result["obsidian_markdown"], language="markdown")
