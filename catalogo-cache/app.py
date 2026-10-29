import streamlit as st
import pandas as pd
import servico
import redis_cache as cache

CATEGORIAS = ["Eletrônicos", "Livros", "Roupas", "Casa"]

st.set_page_config(page_title="Catálogo de Produtos", layout="wide")
st.title("Catálogo de Produtos")
st.caption("Supabase (banco) + Redis (cache)")

aba1, aba2, aba3, aba4 = st.tabs(
    ["Catálogo", "Cadastrar", "Editar / Excluir", "Painel Redis"])

with aba1:
    col_cat, col_busca = st.columns(2)
    filtro = col_cat.selectbox("Categoria", ["Todas"] + CATEGORIAS)
    busca = col_busca.text_input(
        "Buscar por nome", placeholder="ex.: notebook")
    categoria = None if filtro == "Todas" else filtro
    dados, origem, ms = servico.listar_produtos(categoria, busca)
    c1, c2 = st.columns(2)
    c1.metric("Origem dos dados", origem)
    c2.metric("Tempo de resposta", f"{ms:.1f} ms")
    st.dataframe(pd.DataFrame(dados))

with aba2:
    with st.form("novo", clear_on_submit=True):
        nome = st.text_input("Nome")
        cat = st.selectbox("Categoria", CATEGORIAS)
        preco = st.number_input("Preço", min_value=0.0,
                                step=1.0, format="%.2f")
        estoque = st.number_input("Estoque", min_value=0, step=1)
        if st.form_submit_button("Cadastrar"):
            if nome.strip():
                servico.criar_produto(nome.strip(), cat, preco, int(estoque))
                st.success("Produto cadastrado! Cache invalidado.")
            else:
                st.error("Informe o nome.")

with aba3:
    produtos = servico.listar_sem_cache()
    if produtos:
        escolhido = st.selectbox(
            "Produto", produtos, format_func=lambda p: f"{p['id']} - {p['nome']}"
        )
        nome = st.text_input("Nome", escolhido["nome"], key="e_nome")
        cat = st.selectbox(
            "Categoria", CATEGORIAS,
            index=CATEGORIAS.index(
                escolhido["categoria"]) if escolhido["categoria"] in CATEGORIAS else 0,
            key="e_cat",
        )
        preco = st.number_input("Preço", value=float(
            escolhido["preco"]), step=1.0, key="e_preco")
        estoque = st.number_input("Estoque", value=int(
            escolhido["estoque"]), step=1, key="e_est")
        b1, b2 = st.columns(2)
        if b1.button("Salvar alterações"):
            servico.atualizar_produto(
                escolhido["id"],
                {"nome": nome, "categoria": cat,
                    "preco": preco, "estoque": int(estoque)},
            )
            st.success("Atualizado! Cache invalidado.")
            st.rerun()
        if b2.button("Excluir"):
            servico.deletar_produto(escolhido["id"])
            st.warning("Excluído! Cache invalidado.")
            st.rerun()
    else:
        st.info("Nenhum produto cadastrado.")

with aba4:
    hits, misses, chaves = cache.estatisticas()
    total = hits + misses
    c1, c2, c3 = st.columns(3)
    c1.metric("Cache hits", hits)
    c2.metric("Cache misses", misses)
    c3.metric("Taxa de acerto", f"{(hits / total * 100) if total else 0:.0f}%")
    st.subheader("Chaves no Redis (com TTL)")
    st.dataframe(pd.DataFrame(chaves))
    if st.button("Limpar cache"):
        cache.invalidar_listas()
        st.rerun()
