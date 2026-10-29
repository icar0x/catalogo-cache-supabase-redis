# Catálogo de Produtos — Supabase + Redis

Aplicação web de catálogo de produtos com CRUD completo, que usa o **Supabase** como banco de dados e o **Redis** como cache das consultas, com interface gráfica feita em **Streamlit**.

Trabalho Prático — Integração com Supabase e Redis (Projeto de Banco de Dados — UNIFSA).

## Problema que o projeto resolve

Em um catálogo, a listagem de produtos é consultada o tempo todo, mas os dados mudam pouco. Sem cache, cada abertura da tela ou troca de filtro dispara uma nova consulta ao banco na nuvem (rede + banco), o que deixa a resposta lenta e sobrecarrega o banco com consultas repetidas.

## Objetivo e funcionalidades

Objetivo: demonstrar a integração funcional entre interface, banco de dados (Supabase) e cache (Redis), justificando tecnicamente o papel de cada um.

Funcionalidades:

- **Catálogo**: lista os produtos, com **filtro por categoria** e **busca por nome**, e mostra de onde vieram os dados (Supabase ou Redis) e o tempo de resposta em milissegundos.
- **Cadastrar**: cria novos produtos.
- **Editar / Excluir**: atualiza ou remove produtos.
- **Painel Redis**: mostra cache hits, cache misses, taxa de acerto e as chaves em cache com o TTL restante. Também permite limpar o cache.

## Tecnologias utilizadas

- Python 3
- Streamlit (interface gráfica)
- Supabase (PostgreSQL na nuvem) — biblioteca `supabase-py`
- Redis Cloud — biblioteca `redis-py`
- python-dotenv e pandas

## Estrutura do projeto

```
├── app.py            # Interface (Streamlit)
├── servico.py        # Regras: cache-aside entre Supabase e Redis
├── supabase_db.py    # Acesso ao Supabase (CRUD)
├── redis_cache.py    # Acesso ao Redis (cache e contadores)
├── schema.sql        # Criação da tabela e dados de exemplo
├── requirements.txt
└── .env.example      # Modelo das variáveis de ambiente
```

## Instalação, configuração e execução

**1. Clonar o repositório e criar o ambiente virtual**

```bash
git clone <URL-DO-REPOSITORIO>
cd <PASTA-DO-PROJETO>
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

**2. Configurar o Supabase**

1. Crie um projeto em [supabase.com](https://supabase.com).
2. No **SQL Editor**, execute o conteúdo de `schema.sql` (cria a tabela `produtos` e insere dados de exemplo).
3. Em **Project Settings → API Keys**, copie a **Project URL** e a chave **anon / publishable**.

**3. Configurar o Redis**

1. Crie um database gratuito no [Redis Cloud](https://redis.io/try-free).
2. Copie o endpoint (host:porta) e a senha do usuário `default`.
3. Monte a URL: `redis://default:SENHA@HOST:PORTA`.

**4. Variáveis de ambiente**

Copie `.env.example` para `.env` e preencha (o `.env` está no `.gitignore` e nunca deve ser publicado):

```
SUPABASE_URL=https://xxxxxxxx.supabase.co
SUPABASE_KEY=sua_chave_anon_ou_publishable
REDIS_URL=redis://default:SENHA@HOST:PORTA
```

**5. Executar**

```bash
streamlit run app.py
```



## Integração com o Supabase

O Supabase é a **fonte da verdade** dos dados. Toda a comunicação com o banco está isolada em `supabase_db.py`, usando o cliente oficial `supabase-py`:

- `listar(categoria, busca)` — `SELECT` com filtro opcional por categoria (`eq`) e busca parcial por nome, sem diferenciar maiúsculas de minúsculas (`ilike`, equivalente a `WHERE nome ILIKE '%termo%'`). É a consulta usada no catálogo.
- `criar(...)` — `INSERT` de novo produto.
- `atualizar(id, campos)` — `UPDATE` de um produto.
- `deletar(id)` — `DELETE` de um produto.

Os dados ficam na tabela `produtos` (id, nome, categoria, preço, estoque, data de criação). É possível conferir cada operação no **Table Editor** do Supabase.

## Onde e como o Redis foi utilizado

O Redis é usado como **cache das consultas do catálogo** (listagem, filtro por categoria e busca por nome), no padrão **cache-aside**, implementado em `servico.py` (lógica) e `redis_cache.py` (acesso ao Redis).

Cada combinação de filtro e busca é uma consulta diferente e gera uma **chave própria** no Redis. O termo da busca é normalizado (sem espaços nas pontas e em minúsculas), então "Notebook" e "notebook" usam a mesma chave. Exemplos:

| Consulta do usuário | Chave no Redis |
|---|---|
| Todas as categorias, sem busca | `produtos:lista:todas` |
| Categoria "Livros" | `produtos:lista:Livros` |
| Busca por "notebook" | `produtos:lista:todas:busca:notebook` |

**Como funciona:**

1. Ao consultar o catálogo, a aplicação procura primeiro no Redis, usando a chave da consulta.
2. **Cache hit:** se encontrou, devolve os dados direto do Redis, sem consultar o Supabase.
3. **Cache miss:** se não encontrou, consulta o Supabase, guarda o resultado no Redis com **TTL de 60 segundos** (`SETEX`) e devolve os dados.
4. **Invalidação:** ao cadastrar, editar ou excluir um produto, as chaves de lista são removidas (`DEL`), para o cache nunca mostrar dados desatualizados.
5. **Métricas:** contadores `stats:hits` e `stats:misses` (`INCR`) alimentam o Painel Redis.

**Por que o Redis foi escolhido:**

- Armazena dados em memória, com leitura muito rápida.
- Tem expiração nativa (TTL), o que evita cache velho para sempre.
- Reduz o número de consultas repetidas ao banco.
- Oferece contadores atômicos (`INCR`) para as métricas.

**Benefício observado:** na interface, a origem dos dados e o tempo de resposta aparecem a cada consulta. A primeira vez que uma consulta é feita (por exemplo, buscar "notebook"), ela vai ao Supabase. Se a mesma consulta se repete, é atendida pelo Redis, sem acessar o banco, com tempo de resposta menor. Como o Redis Cloud também é remoto, parte do tempo é de rede; com o Redis próximo da aplicação, o ganho tende a ser maior.



## Vídeo demonstrativo

Link do vídeo: https://canva.link/ehkriebfwblzw61

## Autor

Ícaro — Engenharia de Software, UNIFSA
GitHub: [icar0x](https://github.com/icar0x)
