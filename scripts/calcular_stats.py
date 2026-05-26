name: Atualizar Estatísticas Sortudo

on:
  # Roda toda segunda-feira às 9h (horário de Brasília = 12h UTC)
  schedule:
    - cron: '0 12 * * 1'

  # Permite rodar manualmente pelo botão no GitHub
  workflow_dispatch:

jobs:
  atualizar:
    runs-on: ubuntu-latest

    steps:
      # Passo 1: Baixa o repositório
      - name: Baixar repositório
        uses: actions/checkout@v4

      # Passo 2: Instala o Python
      - name: Instalar Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      # Passo 3: Roda o script que calcula as frequências
      - name: Calcular estatísticas reais
        run: python scripts/calcular_stats.py

      # Passo 4: Salva o arquivo stats.json atualizado no repositório
      - name: Salvar stats.json atualizado
        run: |
          git config user.name "Sortudo Bot"
          git config user.email "sortudo-bot@users.noreply.github.com"
          git add stats.json
          git diff --staged --quiet || git commit -m "📊 Estatísticas atualizadas em $(date '+%d/%m/%Y')"
          git push
