📦 Warehouse ClickHouse – ETL
=============================

📌 Visão Geral
--------------

Este repositório contém a infraestrutura e o ETL responsável por sincronizar dados do **MySQL (RDS)** para o **ClickHouse**, de forma **incremental, segura e idempotente**.

O pipeline foi projetado para:

*   Rodar localmente (desenvolvimento/teste)
    
*   Rodar em servidor (AWS / EC2)
    
*   Suportar dados em tempo real (especialmente projects)
    
*   Evitar reprocessamento e loops infinitos
    

🏗️ Arquitetura
---------------
```
MySQL (RDS)
   │
   │  (SSH Tunnel opcional)
   ▼
ETL (Python)
   │
   │  incremental (watermark)
   ▼
ClickHouse (Warehouse)
```

🧱 Componentes
--------------

### Containers

*   **clickhouse**
    
    *   Banco analítico
        
    *   Inicializa schema via sql/\*.sql
        
*   **etl**
    
    *   Executa jobs Python
        
    *   Conecta no MySQL (direto ou via SSH)
        
    *   Persiste watermark no ClickHouse
        

📂 Estrutura do Projeto
-----------------------
```
warehouse-clickhouse/
├── docker-compose.yml
├── .env.example
├── README.md
├── sql/
│ ├── 001_create_db.sql
│ ├── 010_users.sql
│ ├── 020_organizations.sql
│ ├── 030_contracts.sql
│ ├── 040_etl_watermark.sql
│ └── 050_projects.sql
└── etl/
├── Dockerfile
├── requirements.txt
└── src/
├── main.py
├── test_conn.py
├── config.py
├── jobs/
│ ├── users.py
│ ├── organizations.py
│ └── projects.py
└── lib/
├── mysql.py
├── clickhouse.py
└── watermark.py
```


## ⚙️ Configuração (.env)

Exemplo (`.env.example`):


Configurações (.env)

```env
# ===== SSH (bastion / jumpbox) =====
USE_SSH_TUNNEL=1
SSH_HOST=xxx.xxx.xxx.xxx
SSH_PORT=22
SSH_USER=usuario
SSH_KEY_PATH=/keys/id_rsa

# ===== Source MySQL =====
DB_HOST=xxxxxxxx.rds.amazonaws.com
DB_PORT=3306
DB_USER=usuario
DB_PASSWORD=senha

# ===== ClickHouse =====
CH_HOST=clickhouse
CH_PORT=8123
CH_USER=warehouse
CH_PASSWORD=warehouse_pass
CH_DB=warehouse

# ===== ETL =====
BATCH_SIZE=5000

# Projects: janela fixa para evitar loop infinito
PROJECTS_LAG_MINUTES=3
```




📌 **Importante**

*   FORCE\_LAST\_RUN\_AT **não é usado em produção**
    
*   O estado do ETL é controlado exclusivamente pelo etl\_watermark
    

🚀 Subindo o ambiente
---------------------

`   docker compose up -d   `

Verificar containers:

`   docker compose ps   `

🔍 Teste de conectividade
-------------------------

`   docker compose exec etl bash -lc "python /app/src/test_conn.py"   `

Saída esperada:

*   ✅ MySQL OK (direto ou via SSH)
    
*   ✅ ClickHouse OK
    

▶️ Executando os jobs
---------------------

### Organizations (full refresh)

`   docker compose exec etl bash -lc "python /app/src/main.py organizations"   `

*   Tabela pequena (~<50k linhas)
    
*   Atualizada completamente a cada execução
    

### Users (incremental)

`   docker compose exec etl bash -lc "python /app/src/main.py users"   `

Incremental baseado em:

*   last\_login\_at
    
*   id (desempate)
    

### Projects (incremental com cutoff)

`   docker compose exec etl bash -lc "python /app/src/main.py projects"   `

Características:

*   Dados **live**
    
*   Incremental por updated\_at
    
*   Cutoff baseado em PROJECTS\_LAG\_MINUTES
    
*   Evita loop infinito mesmo com projetos sendo atualizados em tempo real
    

🧠 Watermark (estado do ETL)
----------------------------

O estado de cada job é salvo em:

`   warehouse.etl_watermark   `

Campos:

*   job
    
*   last\_run\_at
    
*   last\_id
    
*   updated\_at
    

Consulta útil:

`   SELECT *  FROM warehouse.etl_watermark  ORDER BY updated_at DESC;   `

♻️ Reset completo (ambiente local)
----------------------------------

⚠️ **Apenas para desenvolvimento**

`   docker compose down -v  docker compose up -d   `

Isso remove:

*   dados do ClickHouse
    
*   watermark
    
*   estado completo do warehouse
    

🧩 Observações de Design
------------------------

*   ClickHouse **não usa primary key**
    
*   Dados históricos são acumulados (append-only)
    
*   Incrementalidade garantida via watermark
    
*   Segurança contra perda de dados com lag configurável
    

📌 Próximos passos (produção)
-----------------------------

*   Agendar execução via cron ou systemd
    
*   Rodar os jobs em sequência:
    
`   python main.py organizations && \  python main.py users && \  python main.py projects   `