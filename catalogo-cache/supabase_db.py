import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
_client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
TABELA = "produtos"


def listar(categoria=None, busca=None):
    consulta = _client.table(TABELA).select("*").order("id")
    if categoria:
        consulta = consulta.eq("categoria", categoria)
    if busca:
        consulta = consulta.ilike("nome", f"%{busca}%")
    return consulta.execute().data


def criar(nome, categoria, preco, estoque):
    dados = {"nome": nome, "categoria": categoria,
             "preco": preco, "estoque": estoque}
    return _client.table(TABELA).insert(dados).execute().data[0]


def atualizar(id, campos: dict):
    return _client.table(TABELA).update(campos).eq("id", id).execute().data


def deletar(id):
    _client.table(TABELA).delete().eq("id", id).execute()
