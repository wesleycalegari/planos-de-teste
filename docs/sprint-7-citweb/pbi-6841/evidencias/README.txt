Coloque capturas/screenshots aqui por CT:
  CT-PBI-6841-001 ... CT-PBI-6841-005

Pastas CT-PBI-xxxx-xxx são reconhecidas por claude-contexto/scripts/injetar_evidencias.py.

Após os testes, no index.html pai altere por cenário:
  div.ct-block ... data-status="pendente"|"aprovado"|"reprovado"|"bloqueado"|"na"

Fixture local (somente evidência estrutural, não é HML CitNet):
  fixture-conversor-ct02.html — abrir ou capturar com Playwright/Chromium.

Exemplo CT-02 já executado neste branch:
  python claude-contexto/scripts/injetar_evidencias.py "plano de teste sprint/PBI-6841-conversor-hdi-yelum-rcv/index.html"
    --ct CT-PBI-6841-002 --status aprovado --obs "..."
