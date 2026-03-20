"""
Interface Streamlit — Agent Innovation
Rodar: streamlit run app.py
"""

import streamlit as st
from datetime import datetime
from agent_innovation import (
    analisar_tecnologia, validar_url, estimar_custo, cache_get,
    DOCUMENTOS_PROCESSO, MODELO
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
    # Verifica cache
    cached = cache_get(nome, url_ancora)
    if cached:
        st.info("📦 Resultado em cache — avaliação sem custo.")

    # Validação de URL
    if url_ancora:
        url_ok, url_msg = validar_url(url_ancora)
        if url_ok:
            st.success(f"✅ {url_msg}")
        else:
            st.warning(f"⚠️ {url_msg} — a avaliação continuará só com busca web.")

    # Estimativa de custo (só se não tem cache)
    if not cached:
        est = estimar_custo(nome, url_ancora)
        st.caption(
            f"💰 Custo estimado: **${est['custo_total']:.2f}** "
            f"(~{est['tokens_input']:,} tokens input · "
            f"~{est['tokens_output']:,} tokens output · "
            f"~3 buscas web)"
        )

if st.button("🚀 Avaliar", disabled=not nome, type="primary"):
    with st.spinner("Claude analisando com busca web..."):
        resultado = analisar_tecnologia(nome, url_ancora)

    st.divider()
    st.markdown(resultado)

    # Download
    cabecalho = (
        f"# Radar Tecnológico — {nome}\n"
        f"*Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} "
        f"via {MODELO} + Web Search*\n"
        f"*Revisar antes de usar*\n\n---\n\n"
    )
    nome_arquivo = (
        f"radar_{nome.lower().replace(' ', '_')}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    )
    st.download_button(
        "💾 Baixar .md",
        data=cabecalho + resultado,
        file_name=nome_arquivo,
        mime="text/markdown",
    )
