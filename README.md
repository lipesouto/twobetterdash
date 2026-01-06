# 📊 TwoBetter - Dashboard de Atividades Jira

Dashboard interativo em Streamlit para visualização das atividades do time.

## 🚀 Como executar localmente

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Adicionar dados
Coloque o arquivo CSV exportado do Jira na pasta `data/`:
```
jira_dashboard/
├── app.py
├── data/
│   └── seu_arquivo.csv   ← Coloque aqui
├── requirements.txt
└── README.md
```

### 3. Rodar o dashboard
```bash
streamlit run app.py
```

O dashboard carrega automaticamente o arquivo CSV mais recente da pasta `data/`.

## ☁️ Deploy no Streamlit Cloud

1. Suba o projeto para o GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte seu repositório
4. Deploy!

## 📈 KPIs Disponíveis

- **Total de Tarefas** - Quantidade total de tasks e subtasks
- **Taxa de Conclusão** - Percentual de tarefas concluídas
- **Performance por Dev** - Tarefas concluídas vs pendentes por desenvolvedor
- **Distribuição por Área** - Backend, Frontend, QA, Ops
- **Timeline de Criação** - Evolução de criação de tarefas por semana
- **Atividade Recente** - Tarefas atualizadas nos últimos 7 dias

## 🔍 Filtros Disponíveis

- Período (data de criação)
- Responsável
- Status
- Tipo (Task / Subtask)

## 📁 Como exportar do Jira

Use esta query JQL:
```jql
project = TwoBetter AND issuetype in (Task, Subtask) ORDER BY created DESC
```

Depois clique em **Export → CSV (Current fields)**

## 🔄 Atualizando dados

Para atualizar o dashboard com novos dados:
1. Exporte um novo CSV do Jira
2. Substitua o arquivo na pasta `data/`
3. O dashboard recarrega automaticamente (ou pressione `R` no browser)
