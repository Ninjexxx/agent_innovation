"""
Interface Streamlit — Agent Innovation
Rodar: streamlit run app.py
"""

import streamlit as st
from datetime import datetime
from agent_innovation import (
    analisar_tecnologia, mapear_tecnologias,
    validar_url, estimar_custo, cache_get,
    DOCUMENTOS_PROCESSO, MODELO_TRIAGEM, MODELO_MAPEAMENTO, CUSTOS
)

st.set_page_config(page_title="Esteira de Inovação — Namu", page_icon="🔭")

st.title("🔭 Esteira de Inovação — Namu")
st.caption(f"Triagem: `{MODELO_TRIAGEM}` · Mapeamento: `{MODELO_MAPEAMENTO}` · Web Search ativo")

if DOCUMENTOS_PROCESSO:
    st.caption(f"📄 {len(DOCUMENTOS_PROCESSO):,} chars de documentos de processo carregados")

st.divider()

aba_mapeamento, aba_triagem = st.tabs(["🗺️ Mapeamento", "🔍 Triagem"])

# ── Aba 1: Mapeamento ──
with aba_mapeamento:
    st.caption("Busca tecnologias open-source testáveis por categoria via Claude + Web Search.")

    categoria = st.text_input(
        "Categoria",
        placeholder="Ex: rPPG, skin lesion detection deep learning, food recognition"
    )

    if categoria:
        cached_map = cache_get(f"map|{categoria}", "")
        if cached_map:
            st.info("📦 Mapeamento em cache — sem custo.")
        else:
            custos_haiku = CUSTOS[MODELO_MAPEAMENTO]
            custo_map = round(
                (2000 / 1_000_000) * custos_haiku["input"]
                + (2000 / 1_000_000) * custos_haiku["output"]
                + 0.10 * 3, 2
            )
            st.caption(f"💰 Custo estimado: **${custo_map:.2f}** ({MODELO_MAPEAMENTO} · ~3 buscas web)")

    if st.button("🗺️ Mapear", disabled=not categoria, type="primary"):
        with st.spinner("Claude buscando tecnologias open-source..."):
            resultado_map = mapear_tecnologias(categoria)
        st.session_state["resultado_mapeamento"] = resultado_map
        st.session_state["categoria_map"] = categoria

    if "resultado_mapeamento" in st.session_state:
        st.divider()
        st.subheader(f"🗺️ Mapeamento: {st.session_state['categoria_map']}")
        st.markdown(st.session_state["resultado_mapeamento"])

        nome_map = (
            f"mapeamento_{st.session_state['categoria_map'].lower().replace(' ', '_')}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        )
        st.download_button(
            "💾 Baixar mapeamento .md",
            data=f"# Mapeamento Open-Source — {st.session_state['categoria_map']}\n\n"
                 + st.session_state["resultado_mapeamento"],
            file_name=nome_map,
            mime="text/markdown",
        )

# ── Aba 2: Triagem ──
with aba_triagem:
    nome = st.text_input("Nome da tecnologia", placeholder="Ex: QuickPose.ai")
    url_ancora = st.text_input("URL âncora (opcional)", placeholder="https://...")

    modelo_triagem = st.selectbox(
        "Modelo",
        options=list(CUSTOS.keys()),
        index=list(CUSTOS.keys()).index(MODELO_TRIAGEM),
        format_func=lambda m: f"{m} ({'barato' if 'haiku' in m else 'qualidade'})"
    )

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
            est = estimar_custo(nome, url_ancora, modelo_triagem)
            st.caption(
                f"💰 Custo estimado: **${est['custo_total']:.2f}** "
                f"(~{est['tokens_input']:,} tokens input · "
                f"~{est['tokens_output']:,} tokens output · "
                f"~3 buscas web)"
            )

    if st.button("🚀 Avaliar", disabled=not nome, type="primary"):
        with st.spinner("Claude analisando com busca web..."):
            resultado = analisar_tecnologia(nome, url_ancora, modelo_triagem)
        st.session_state["resultado_triagem"] = resultado
        st.session_state["nome_tech"] = nome
        st.session_state["modelo_usado"] = modelo_triagem

    if "resultado_triagem" in st.session_state:
        st.divider()
        st.subheader("📋 Triagem")
        st.markdown(st.session_state["resultado_triagem"])

        cabecalho = (
            f"# Radar Tecnológico — {st.session_state['nome_tech']}\n"
            f"*Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} "
            f"via {st.session_state.get('modelo_usado', MODELO_TRIAGEM)} + Web Search*\n"
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
