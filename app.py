"""
Interface Streamlit — Agent Innovation
Rodar: streamlit run app.py
"""

import streamlit as st
from datetime import datetime
from agent_innovation import (
    analisar_tecnologia, priorizar_tecnologia,
    validar_url, estimar_custo, cache_get,
    DOCUMENTOS_PROCESSO, MODELO, CUSTOS
)

st.set_page_config(page_title="Radar Tecnológico — Namu", page_icon="🔭")

st.title("🔭 Radar Tecnológico — Namu")
st.caption(f"Modelo: `{MODELO}` · Web Search ativo")

if DOCUMENTOS_PROCESSO:
    st.caption(f"📄 {len(DOCUMENTOS_PROCESSO):,} chars de documentos de processo carregados")

st.divider()

nome = st.text_input("Nome da tecnologia", placeholder="Ex: QuickPose.ai")
url_ancora = st.text_input("URL âncora (opcional)", placeholder="https://...")

if nome:
    cached = cache_get(nome, url_ancora)
    if cached:
        st.info("📦 Resultado em cache — avaliação sem custo.")

    if url_ancora:
        url_ok, url_msg = validar_url(url_ancora)
        if url_ok:
            st.success(f"✅ {url_msg}")
        else:
            st.warning(f"⚠️ {url_msg} — a avaliação continuará só com busca web.")

    if not cached:
        est = estimar_custo(nome, url_ancora)
        st.caption(
            f"💰 Custo estimado: **${est['custo_total']:.2f}** "
            f"(~{est['tokens_input']:,} tokens input · "
            f"~{est['tokens_output']:,} tokens output · "
            f"~3 buscas web)"
        )

# ── Etapa 1: Triagem ──
if st.button("🚀 Avaliar", disabled=not nome, type="primary"):
    with st.spinner("Claude analisando com busca web..."):
        resultado = analisar_tecnologia(nome, url_ancora)
    st.session_state["resultado_triagem"] = resultado
    st.session_state["nome_tech"] = nome

if "resultado_triagem" in st.session_state:
    st.divider()
    st.subheader("📋 Triagem")
    st.markdown(st.session_state["resultado_triagem"])

    # Download triagem
    cabecalho = (
        f"# Radar Tecnológico — {st.session_state['nome_tech']}\n"
        f"*Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} "
        f"via {MODELO} + Web Search*\n"
        f"*Revisar antes de usar*\n\n---\n\n"
    )
    nome_md = (
        f"radar_{st.session_state['nome_tech'].lower().replace(' ', '_')}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    )
    st.download_button(
        "💾 Baixar triagem .md",
        data=cabecalho + st.session_state["resultado_triagem"],
        file_name=nome_md,
        mime="text/markdown",
    )

    # ── Etapa 2: Priorização ──
    st.divider()

    custos_modelo = CUSTOS.get(MODELO, CUSTOS["claude-haiku-4-5-20251001"])
    custo_prio = round((2000 / 1_000_000) * custos_modelo["input"]
                       + (2000 / 1_000_000) * custos_modelo["output"], 2)

    cached_prio = cache_get(f"prio|{st.session_state['nome_tech']}", "")
    if cached_prio:
        st.info("📦 Priorização em cache — sem custo.")
    else:
        st.caption(f"💰 Custo estimado da priorização: **${custo_prio:.2f}** (sem web search)")

    if st.button("📊 Priorizar (TAM/SAM/SOM)", type="secondary"):
        with st.spinner("Claude gerando scoring..."):
            scoring = priorizar_tecnologia(
                st.session_state["nome_tech"],
                st.session_state["resultado_triagem"]
            )
        st.session_state["resultado_priorizacao"] = scoring

    if "resultado_priorizacao" in st.session_state:
        st.subheader("📊 Priorização")
        st.markdown(st.session_state["resultado_priorizacao"])

        nome_prio = (
            f"scoring_{st.session_state['nome_tech'].lower().replace(' ', '_')}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        )
        st.download_button(
            "💾 Baixar scoring .md",
            data=f"# Priorização — {st.session_state['nome_tech']}\n\n"
                 + st.session_state["resultado_priorizacao"],
            file_name=nome_prio,
            mime="text/markdown",
        )
