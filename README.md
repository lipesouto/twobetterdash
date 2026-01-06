# 📊 TwoBetter - Dashboard de Atividades Jira

Dashboard interativo em Streamlit para visualização das atividades do time.

## 🚀 Como executar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Rodar o dashboard
```bash
streamlit run app.py
```

### 3. Acessar no navegador
O Streamlit vai abrir automaticamente em `http://localhost:8501`

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

## ⚠️ Observação

O CSV atual não contém campos de **horas trabalhadas** ou **story points**. 
Para adicionar essas métricas, exporte esses campos do Jira:
- Original Estimate
- Time Spent
- Story Points
