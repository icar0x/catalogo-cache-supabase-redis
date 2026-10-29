import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()
r = redis.from_url(os.environ["REDIS_URL"], decode_responses=True)

TTL_SEGUNDOS = 60
PREFIXO = "produtos:lista:"


def _chave(categoria, busca=None):
    chave = f"{PREFIXO}{categoria or 'todas'}"
    if busca:
        chave += f":busca:{busca}"
    return chave


def get_lista(categoria=None, busca=None):
    valor = r.get(_chave(categoria, busca))
    return json.loads(valor) if valor else None


def set_lista(categoria, dados, busca=None):
    r.setex(_chave(categoria, busca), TTL_SEGUNDOS,
            json.dumps(dados, default=str))


def invalidar_listas():
    for chave in r.scan_iter(f"{PREFIXO}*"):
        r.delete(chave)


def registrar(tipo):
    """tipo = 'hits' ou 'misses'"""
    r.incr(f"stats:{tipo}")


def estatisticas():
    hits = int(r.get("stats:hits") or 0)
    misses = int(r.get("stats:misses") or 0)
    chaves = [{"chave": k, "ttl_s": r.ttl(k)}
              for k in r.scan_iter(f"{PREFIXO}*")]
    return hits, misses, chaves
