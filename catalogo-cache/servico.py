import time
import supabase_db as db
import redis_cache as cache


def listar_produtos(categoria=None, busca=None):
    inicio = time.perf_counter()
    busca = (busca or "").strip().lower() or None

    dados = cache.get_lista(categoria, busca)
    if dados is not None:
        cache.registrar("hits")
        return dados, "Redis (cache)", (time.perf_counter() - inicio) * 1000

    dados = db.listar(categoria, busca)
    cache.set_lista(categoria, dados, busca)
    cache.registrar("misses")
    return dados, "Supabase (banco)", (time.perf_counter() - inicio) * 1000


def listar_sem_cache():
    return db.listar()


def criar_produto(nome, categoria, preco, estoque):
    db.criar(nome, categoria, preco, estoque)
    cache.invalidar_listas()


def atualizar_produto(id, campos):
    db.atualizar(id, campos)
    cache.invalidar_listas()


def deletar_produto(id):
    db.deletar(id)
    cache.invalidar_listas()
