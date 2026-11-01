# Dashboard de Temperatura — Recife

Dashboard simples que mostra a temperatura atual, a condição do tempo e a previsão de 5 dias para Recife (PE).

Os dados são atualizados automaticamente a cada hora por um GitHub Action.

## Publicar no GitHub Pages

1. Os arquivos já estão neste repositório.
2. Vá em **Settings → Pages**.
3. Em **Build and deployment**, escolha **Deploy from a branch**.
4. Branch: `main`, pasta: `/ (root)`.
5. Salve. O site ficará disponível em alguns minutos em  
   `https://joaomartins234.github.io/temperatura-recife/`

## Atualização automática

O workflow `.github/workflows/atualizar.yml` roda a cada hora e também pode ser disparado manualmente:

- Vá em **Actions → Atualizar temperatura → Run workflow**.

## Dados do INMET (opcional)

A temperatura atual tenta vir do INMET quando há token. A previsão e a condição sempre vêm do Open-Meteo (sem chave).

1. Solicite o token em [portal.inmet.gov.br](https://portal.inmet.gov.br).
2. Em **Settings → Secrets and variables → Actions**, crie o secret `INMET_TOKEN`.
3. A estação padrão é `A301` (Recife). Confirme em [mapas.inmet.gov.br](https://mapas.inmet.gov.br) e, se necessário, crie a variable `INMET_ESTACAO`.
4. Se a primeira execução com token cair no Open-Meteo, verifique o log da Action e ajuste o endpoint no script se preciso.

## Estrutura

- `index.html` — dashboard
- `temperatura.json` — dados (gerado pelo script)
- `scripts/atualizar_temperatura.py` — gera o JSON
- `.github/workflows/atualizar.yml` — agendamento

---

Martins Engenharia  
Atualizado automaticamente via GitHub Actions.
