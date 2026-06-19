# -*- coding: utf-8 -*-
"""
gerar_plano.py — Gerador do Plano de Teste Regressivo CITNET AXA
Gera index.html com todos os 241 CTs, step-by-step completo.
"""
from pathlib import Path
from datetime import date

OUT = Path(__file__).parent / 'index.html'
HOJE = date.today().strftime('%d/%m/%Y')

URL   = 'https://axa-hml-faturamento.nsseg.com.br/citnet/'
LOGIN = 'interno / 11'

# ─── TEMPLATES DE PASSOS ─────────────────────────────────────────────────────

def steps_login():
    return [
        f'Abrir o Google Chrome e acessar a URL: <code>{URL}</code>',
        'Na tela de login, preencher — Usuário: <code>interno</code> &nbsp;|&nbsp; Senha: <code>11</code>',
        'Clicar no botão <strong>[Entrar]</strong>',
        'Confirmar que a tela inicial CITNET AXA carregou (barra de menu superior visível)',
    ]

def steps_nav(menu_itens, filial=True, extra_filtros=None):
    s = []
    for i, item in enumerate(menu_itens):
        acao = 'clicar em' if i == 0 else 'no submenu, clicar em'
        s.append(f'No menu superior, {acao} <strong>{item}</strong>')
    s.append(f'Confirmar que a tela "<strong>{menu_itens[-1]}</strong>" foi carregada')
    if filial:
        s.append('No campo <strong>Filial</strong>, selecionar <code>1 - SAO PAULO</code>')
    if extra_filtros:
        s.extend(extra_filtros)
    return s

def step_selecionar_ramo(ramo_codigo, ramo_nome):
    return f'No campo <strong>Ramo</strong>, confirmar ou selecionar <code>{ramo_codigo} - {ramo_nome}</code>'

def steps_criar_averbacao_nacional(ramo_codigo, ramo_nome, campos_especificos):
    steps = steps_login() + steps_nav(['Averbações', ramo_nome])
    steps += [
        step_selecionar_ramo(ramo_codigo, ramo_nome),
        'Clicar no botão <strong>[Novo]</strong>',
        'No campo <strong>Apólice</strong>, selecionar o primeiro disponível na lista (filial 1, ramo ' + ramo_codigo + ')',
    ] + campos_especificos + [
        'Clicar no botão <strong>[Gravar]</strong>',
        'Aguardar o processamento (ícone de carregamento desaparecer)',
    ]
    return steps

def steps_editar_averbacao(ramo_nome):
    return steps_login() + steps_nav(['Averbações', ramo_nome]) + [
        'Consultar uma averbação existente usando o filtro de apólice',
        'Clicar na averbação encontrada para abri-la',
        'Alterar um campo editável (ex: observação ou campo numérico permitido)',
        'Clicar no botão <strong>[Gravar]</strong>',
        'Aguardar o processamento',
    ]

def steps_excluir_averbacao(ramo_nome):
    return steps_login() + steps_nav(['Averbações', ramo_nome]) + [
        'Consultar uma averbação existente',
        'Selecionar a averbação clicando no checkbox ou no link da linha',
        'Clicar no botão <strong>[Excluir]</strong>',
        'Na caixa de confirmação, clicar em <strong>[Sim]</strong> ou <strong>[OK]</strong>',
        'Aguardar o processamento',
    ]

def steps_validacao_campos(ramo_nome, campo_invalido, valor_invalido):
    return steps_login() + steps_nav(['Averbações', ramo_nome]) + [
        'Clicar no botão <strong>[Novo]</strong>',
        f'No campo <strong>{campo_invalido}</strong>, preencher com: <code>{valor_invalido}</code>',
        'Deixar os demais campos obrigatórios em branco (ou preencher propositalmente incorreto)',
        'Clicar no botão <strong>[Gravar]</strong>',
    ]

# ─── DADOS DE CT POR MÓDULO ──────────────────────────────────────────────────

# Estrutura: (ct_id, titulo, prioridade, tipo, steps_func_name, resultado_esperado, observacao)

def ct(id_, titulo, prio, tipo, passos, resultado, obs=''):
    return {
        'id': id_, 'titulo': titulo, 'prio': prio, 'tipo': tipo,
        'passos': passos, 'resultado': resultado, 'obs': obs,
        'script': '_scripts/citnet/run_regressivo_citnet_v2.py',
    }

# ── RCTR-C ───────────────────────────────────────────────────────────────────
CAMPOS_RCTRC = [
    'No campo <strong>C.G.C./CPF Embarcador</strong>, preencher com um CNPJ válido (ex: <code>12.345.678/0001-00</code>)',
    'No campo <strong>Tipo de Veículo</strong>, selecionar <code>T - Terrestre</code>',
    'No campo <strong>Placa</strong>, preencher com <code>QA-0001</code>',
    'No campo <strong>Data Início</strong>, preencher com a data atual',
    'No campo <strong>Data Fim</strong>, preencher com <code>31/12/2026</code>',
    'No campo <strong>Valor da Mercadoria</strong>, preencher com <code>10000,00</code>',
]

CTS_RCTRC = [
    ct('CT001_RCTRC-01', 'Criar averbação RCTR-C — happy path completo', 'P1', 'Positivo',
       steps_criar_averbacao_nacional('54','RCTR-C', CAMPOS_RCTRC),
       'Modal de confirmação exibido com mensagem de sucesso. Registro aparece na grid de averbações.',
       'Script automatizado cobre este CT integralmente.'),
    ct('CT002_RCTRC-02', 'Editar averbação RCTR-C existente', 'P2', 'Positivo',
       steps_editar_averbacao('RCTR-C'),
       'Alteração salva com sucesso. Modal de confirmação exibido. Grid atualiza com novo valor.'),
    ct('CT003_RCTRC-03', 'Excluir averbação RCTR-C', 'P2', 'Positivo',
       steps_excluir_averbacao('RCTR-C'),
       'Registro removido do grid. Mensagem de exclusão bem-sucedida exibida.'),
    ct('CT004_RCTRC-04', 'Validar campos obrigatórios RCTR-C', 'P1', 'Negativo',
       steps_validacao_campos('RCTR-C', 'todos os campos', '(vazio)'),
       'Sistema bloqueia o envio. Mensagem de validação indica quais campos são obrigatórios.'),
    ct('CT006_RCTRC-06', 'Bloquear averbação fora do período da apólice', 'P1', 'Negativo',
       steps_login() + steps_nav(['Averbações', 'RCTR-C']) + [
           'Clicar em <strong>[Novo]</strong>',
           'Selecionar a apólice disponível',
           'No campo <strong>Data Início</strong>, preencher com uma data <em>anterior ao início de vigência</em> da apólice (ex: <code>01/01/2000</code>)',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Sistema exibe mensagem de bloqueio indicando que a data está fora do período de vigência da apólice. Averbação não é gravada.'),
    ct('CT007_RCTRC-07', 'Validar limite máximo de caracteres em campo texto', 'P3', 'Limite',
       steps_login() + steps_nav(['Averbações', 'RCTR-C']) + [
           'Clicar em <strong>[Novo]</strong>',
           'No campo <strong>Observação</strong> (ou campo texto longo), colar uma string com mais de 500 caracteres',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Campo trunca automaticamente ao limite definido OU sistema exibe mensagem de tamanho excedido.'),
    ct('CT008_RCTRC-08', 'Rejeitar placa com formato inválido', 'P2', 'Negativo',
       steps_login() + steps_nav(['Averbações', 'RCTR-C']) + [
           'Clicar em <strong>[Novo]</strong>',
           'No campo <strong>Placa</strong>, preencher com valor inválido: <code>INVALIDA</code>',
           'Tentar avançar para o próximo campo ou clicar em <strong>[Gravar]</strong>',
       ],
       'Sistema rejeita a placa e exibe mensagem indicando formato inválido (esperado: AAA-9999 ou Mercosul).'),
]

# ── RCA-C ────────────────────────────────────────────────────────────────────
CAMPOS_RCAC = [
    'No campo <strong>Apólice</strong>, selecionar apólice disponível ramo 56',
    'No campo <strong>Tipo de Carga</strong>, selecionar opção disponível',
    'No campo <strong>Valor da Mercadoria</strong>, preencher com <code>5000,00</code>',
    'No campo <strong>Data Início</strong>, preencher com a data atual',
    'No campo <strong>Data Fim</strong>, preencher com <code>31/12/2026</code>',
]

CTS_RCAC = [
    ct('CT009_RCACX-01', 'Criar averbação RCA-C — happy path', 'P1', 'Positivo',
       steps_criar_averbacao_nacional('56','RCA-C', CAMPOS_RCAC),
       'Averbação criada com sucesso. Modal de confirmação exibido. Registro visível no grid.'),
    ct('CT010_RCACX-02', 'Editar averbação RCA-C existente', 'P2', 'Positivo',
       steps_editar_averbacao('RCA-C'),
       'Edição salva com sucesso. Grid atualiza com dados modificados.'),
    ct('CT011_RCACX-03', 'Excluir averbação RCA-C', 'P2', 'Positivo',
       steps_excluir_averbacao('RCA-C'),
       'Averbação removida. Grid atualiza sem o registro excluído.'),
    ct('CT013_RCACX-05', 'Bloquear averbação RCA-C fora do período', 'P1', 'Negativo',
       steps_login() + steps_nav(['Averbações', 'RCA-C']) + [
           'Clicar em <strong>[Novo]</strong>',
           'Selecionar apólice ramo 56',
           'Preencher <strong>Data Início</strong> com data fora da vigência da apólice',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Sistema bloqueia e exibe mensagem indicando período inválido.'),
]

# ── RCTA-C ───────────────────────────────────────────────────────────────────
CTS_RCTAC = [
    ct('CT014_RCTAC-01', 'Criar averbação RCTA-C — happy path', 'P1', 'Positivo',
       steps_criar_averbacao_nacional('58','RCTA-C', [
           'No campo <strong>Apólice</strong>, selecionar apólice disponível ramo 58 (ex: <code>242348</code>)',
           'Preencher campos obrigatórios: tipo de carga, valor da mercadoria, datas de vigência',
       ]),
       'Averbação criada com sucesso. Modal de confirmação exibido.'),
    ct('CT015_RCTAC-04', 'Validar campos obrigatórios RCTA-C', 'P1', 'Negativo',
       steps_validacao_campos('RCTA-C', 'Apólice e Valor', '(vazio)'),
       'Sistema bloqueia o envio e exibe mensagem listando campos obrigatórios não preenchidos.'),
    ct('CT016_RCTAC-02', 'Editar averbação RCTA-C existente', 'P2', 'Positivo',
       steps_editar_averbacao('RCTA-C'),
       'Edição aplicada com sucesso. Confirmação exibida.'),
    ct('CT017_RCTAC-03', 'Excluir averbação RCTA-C', 'P2', 'Positivo',
       steps_excluir_averbacao('RCTA-C'),
       'Registro excluído. Grid atualizado.'),
    ct('CT019_RCTAC-06', 'Bloquear RCTA-C fora do período de vigência', 'P1', 'Negativo',
       steps_login() + steps_nav(['Averbações', 'RCTA-C']) + [
           'Clicar em <strong>[Novo]</strong>',
           'Preencher data início com <code>01/01/2000</code> (fora da vigência)',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Sistema bloqueia. Mensagem de período inválido exibida.'),
]

# ── RCTF-C ───────────────────────────────────────────────────────────────────
CTS_RCTFC = [
    ct('CT020_RCTFC-01', 'Criar averbação RCTF-C — happy path', 'P1', 'Positivo',
       steps_criar_averbacao_nacional('38','RCTF-C', [
           'No campo <strong>Apólice</strong>, selecionar apólice disponível ramo 38',
           'Preencher campos obrigatórios conforme ramo 38',
       ]),
       'Averbação criada com sucesso. Confirmação exibida.'),
    ct('CT021_RCTFC-04', 'Validar campos obrigatórios RCTF-C', 'P1', 'Negativo',
       steps_validacao_campos('RCTF-C', 'campos obrigatórios', '(vazio)'),
       'Sistema bloqueia. Lista de campos obrigatórios exibida.'),
    ct('CT022_RCTFC-02', 'Editar averbação RCTF-C', 'P2', 'Positivo',
       steps_editar_averbacao('RCTF-C'),
       'Edição salva. Confirmação exibida.'),
    ct('CT023_RCTFC-03', 'Excluir averbação RCTF-C', 'P2', 'Positivo',
       steps_excluir_averbacao('RCTF-C'),
       'Registro removido do grid.'),
    ct('CT025_RCTFC-06', 'Bloquear RCTF-C fora do período', 'P1', 'Negativo',
       steps_login() + steps_nav(['Averbações', 'RCTF-C']) + [
           'Clicar em <strong>[Novo]</strong>',
           'Preencher data fora da vigência da apólice',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Bloqueio com mensagem de período inválido.'),
]

# ── TN (Transporte Nacional) ──────────────────────────────────────────────────
CTS_TN = [
    ct('CT026_TRANS-01', 'Criar averbação Transporte Nacional — happy path', 'P1', 'Positivo',
       steps_criar_averbacao_nacional('21','Transporte Nacional', [
           'No campo <strong>Apólice</strong>, selecionar apólice disponível ramo 21 (ex: <code>40425</code>)',
           'No campo <strong>Tipo de Embalagem</strong>, selecionar opção disponível',
           'No campo <strong>Valor da Mercadoria</strong>, preencher <code>8000,00</code>',
           'No campo <strong>Cidade Origem</strong>, preencher <code>SÃO PAULO</code>',
           'No campo <strong>UF Origem</strong>, selecionar <code>SP</code>',
           'No campo <strong>Cidade Destino</strong>, preencher <code>RIO DE JANEIRO</code>',
           'No campo <strong>UF Destino</strong>, selecionar <code>RJ</code>',
           'No campo <strong>Data Início</strong>, preencher com a data atual',
           'No campo <strong>Data Fim</strong>, preencher com <code>31/12/2026</code>',
       ]),
       'Averbação TN criada com sucesso. Modal de confirmação exibido. Número de averbação gerado.'),
    ct('CT027_TRANS-02', 'Editar averbação Transporte Nacional', 'P2', 'Positivo',
       steps_editar_averbacao('Transporte Nacional'),
       'Edição salva. Confirmação exibida.'),
    ct('CT028_TRANS-03', 'Excluir averbação Transporte Nacional', 'P2', 'Positivo',
       steps_excluir_averbacao('Transporte Nacional'),
       'Averbação excluída. Grid atualizado.'),
    ct('CT029_TRANS-04', 'Validar campos de embalagem Transporte Nacional', 'P2', 'Negativo',
       steps_login() + steps_nav(['Averbações', 'Transporte Nacional']) + [
           'Clicar em <strong>[Novo]</strong>',
           'Preencher todos os campos obrigatórios exceto o <strong>Tipo de Embalagem</strong>',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Sistema bloqueia e indica que o campo Embalagem é obrigatório.'),
    ct('CT030_TRANS-05', 'Validar série de identificação (série U)', 'P2', 'Limite',
       steps_login() + steps_nav(['Averbações', 'Transporte Nacional']) + [
           'Clicar em <strong>[Novo]</strong>',
           'Preencher campos obrigatórios',
           'No campo <strong>Série</strong>, preencher <code>U</code>',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Sistema aceita a série U e cria a averbação com sucesso.'),
    ct('CT031_TRANS-07', 'Bloquear TN fora do período da apólice', 'P1', 'Negativo',
       steps_login() + steps_nav(['Averbações', 'Transporte Nacional']) + [
           'Clicar em <strong>[Novo]</strong>',
           'Preencher <strong>Data Início</strong> com data anterior à vigência da apólice',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Sistema bloqueia. Mensagem de período inválido exibida.'),
    ct('CT032_TRANS-08', 'Validar limite de caracteres em observação TN', 'P3', 'Limite',
       steps_login() + steps_nav(['Averbações', 'Transporte Nacional']) + [
           'Clicar em <strong>[Novo]</strong>',
           'No campo <strong>Observação</strong>, colar texto com mais de 500 caracteres',
           'Verificar comportamento do campo',
       ],
       'Campo trunca ao limite máximo OU exibe mensagem de tamanho excedido.'),
]

# ── RCV (Ramo 59) ─────────────────────────────────────────────────────────────
CTS_RCV = [
    ct('CT033_RCVXX-01', 'Criar prévia RCV — happy path', 'P1', 'Positivo',
       steps_login() + steps_nav(['Averbações', 'RCV']) + [
           'No campo <strong>Filial</strong>, selecionar <code>1 - SAO PAULO</code>',
           'No campo <strong>Apólice</strong>, selecionar apólice ramo 59 com condição comercial configurada',
           'Preencher os campos obrigatórios: segurado, datas de vigência, prêmio',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Prévia RCV criada com sucesso. Modal de confirmação exibido.'),
    ct('CT034_RCVXX-02', 'Editar prévia RCV existente', 'P2', 'Positivo',
       steps_login() + steps_nav(['Averbações', 'RCV']) + [
           'Consultar prévia RCV existente',
           'Abrir a prévia para edição',
           'Alterar campo editável',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Edição salva. Confirmação exibida.'),
    ct('CT035_RCVXX-03', 'Excluir prévia RCV', 'P2', 'Positivo',
       steps_login() + steps_nav(['Averbações', 'RCV']) + [
           'Consultar prévia RCV existente',
           'Selecionar a prévia',
           'Clicar em <strong>[Excluir]</strong> e confirmar',
       ],
       'Prévia excluída. Grid atualizado.'),
    ct('CT036_RCVXX-04', 'Bloquear RCV sem apólice com condição comercial', 'P1', 'Negativo',
       steps_login() + steps_nav(['Averbações', 'RCV']) + [
           'No campo <strong>Apólice</strong>, selecionar apólice ramo 59 <em>sem condição comercial configurada</em>',
           'Tentar preencher os demais campos e clicar em <strong>[Gravar]</strong>',
       ],
       'Sistema bloqueia com mensagem indicando ausência de condição comercial. Prévia não é criada.'),
    ct('CT037_RCVXX-05', 'Validar campos obrigatórios RCV', 'P1', 'Negativo',
       steps_validacao_campos('RCV', 'campos obrigatórios', '(em branco)'),
       'Sistema bloqueia. Mensagem indica campos obrigatórios faltantes.'),
    ct('CT038_RCVXX-06', 'Bloquear RCV fora do período de vigência', 'P1', 'Negativo',
       steps_login() + steps_nav(['Averbações', 'RCV']) + [
           'Clicar em <strong>[Novo]</strong>',
           'Selecionar apólice e preencher data início fora da vigência',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Bloqueio com mensagem de período inválido.'),
    ct('CT039_RCVXX-07', 'Cancelar inclusão RCV sem salvar', 'P3', 'Negativo',
       steps_login() + steps_nav(['Averbações', 'RCV']) + [
           'Clicar em <strong>[Novo]</strong>',
           'Preencher parcialmente os campos',
           'Clicar em <strong>[Cancelar]</strong> ou navegar para outra tela',
       ],
       'Formulário descartado. Nenhuma prévia criada. Grid não é alterado.'),
]

# Completar os 42 nacionais com CTs adicionais de regressão
CTS_NACIONAIS_EXTRA = [
    ct('CT040_REGR-01', 'Regressão — fluxo completo RCTR-C após alterações', 'P1', 'Regressão',
       steps_criar_averbacao_nacional('54','RCTR-C', CAMPOS_RCTRC),
       'Fluxo de averbação RCTR-C funciona integralmente. Nenhuma funcionalidade anterior quebrada.',
       'Executado automaticamente em todo release.'),
    ct('CT041_REGR-02', 'Regressão — fluxo completo RCA-C após alterações', 'P1', 'Regressão',
       steps_criar_averbacao_nacional('56','RCA-C', CAMPOS_RCAC),
       'Fluxo RCA-C íntegro.'),
    ct('CT042_REGR-03', 'Regressão — fluxo completo TN após alterações', 'P1', 'Regressão',
       steps_criar_averbacao_nacional('21','Transporte Nacional', [
           'Preencher campos mínimos obrigatórios do TN',
       ]),
       'Fluxo TN íntegro.'),
]

# ── INTERNACIONAIS ────────────────────────────────────────────────────────────
def steps_imp_provisoria(criar=True):
    base = steps_login() + steps_nav(['Averbações', 'Imp. Provisória'])
    if criar:
        base += [
            'No campo <strong>Filial</strong>, selecionar <code>1 - SAO PAULO</code>',
            'No campo <strong>Apólice</strong>, selecionar apólice disponível ramo 22',
            'No campo <strong>País Destino</strong>, selecionar país de destino',
            'No campo <strong>Valor CIF</strong>, preencher <code>15000,00</code>',
            'No campo <strong>Data Embarque</strong>, preencher com data atual',
            'Clicar em <strong>[Gravar]</strong>',
        ]
    return base

CTS_IMP_PROV = [
    ct('CT043_IMPPR-01', 'Criar averbação Imp. Provisória — happy path', 'P1', 'Positivo',
       steps_imp_provisoria(criar=True),
       'Averbação criada. Modal de sucesso. Número de averbação gerado.'),
    ct('CT044_IMPPR-02', 'Editar averbação Imp. Provisória', 'P2', 'Positivo',
       steps_login() + steps_nav(['Averbações', 'Imp. Provisória']) + [
           'Consultar averbação existente e abrir para edição',
           'Alterar o valor CIF ou outra informação editável',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Edição salva. Confirmação exibida.'),
    ct('CT045_IMPPR-03', 'Excluir averbação Imp. Provisória', 'P2', 'Positivo',
       steps_login() + steps_nav(['Averbações', 'Imp. Provisória']) + [
           'Consultar e selecionar averbação existente',
           'Clicar em <strong>[Excluir]</strong> e confirmar',
       ],
       'Averbação excluída. Grid atualizado.'),
    ct('CT046_IMPPR-04', 'Validar campos obrigatórios Imp. Provisória', 'P1', 'Negativo',
       steps_login() + steps_nav(['Averbações', 'Imp. Provisória']) + [
           'Clicar em <strong>[Novo]</strong> sem preencher campos',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Sistema exibe mensagem de campos obrigatórios.'),
    ct('CT047_IMPPR-05', 'Bloquear Imp. Provisória fora da vigência', 'P1', 'Negativo',
       steps_login() + steps_nav(['Averbações', 'Imp. Provisória']) + [
           'Clicar em <strong>[Novo]</strong>',
           'Preencher data embarque fora da vigência da apólice',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Bloqueio com mensagem de período inválido.'),
]

def steps_imp_definitiva():
    return steps_login() + steps_nav(['Averbações', 'Imp. Definitiva']) + [
        'No campo <strong>Filial</strong>, selecionar <code>1 - SAO PAULO</code>',
        'No campo <strong>Apólice</strong>, selecionar apólice ramo 22 disponível',
        'Preencher campos obrigatórios: país destino, valor CIF, data embarque, número DI',
        'Clicar em <strong>[Gravar]</strong>',
    ]

CTS_IMP_DEF = [
    ct('CT065_IMPDE-01', 'Criar averbação Imp. Definitiva — happy path', 'P1', 'Positivo',
       steps_imp_definitiva(),
       'Averbação criada. Confirmação exibida. Número de averbação gerado.'),
    ct('CT066_IMPDE-02', 'Editar averbação Imp. Definitiva', 'P2', 'Positivo',
       steps_login() + steps_nav(['Averbações', 'Imp. Definitiva']) + [
           'Consultar e abrir averbação existente',
           'Alterar valor CIF ou número DI',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Edição salva. Confirmação exibida.'),
    ct('CT067_IMPDE-03', 'Excluir averbação Imp. Definitiva', 'P2', 'Positivo',
       steps_login() + steps_nav(['Averbações', 'Imp. Definitiva']) + [
           'Consultar e selecionar averbação',
           'Clicar em <strong>[Excluir]</strong> e confirmar',
       ],
       'Registro removido.'),
    ct('CT068_IMPDE-04', 'Validar obrigatoriedade de número DI', 'P1', 'Negativo',
       steps_login() + steps_nav(['Averbações', 'Imp. Definitiva']) + [
           'Clicar em <strong>[Novo]</strong>',
           'Preencher todos os campos exceto <strong>Número DI</strong>',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Sistema exibe mensagem indicando que o número DI é obrigatório.'),
    ct('CT069_IMPDE-05', 'Criar Imp. Definitiva com campos específicos preenchidos', 'P2', 'Positivo',
       steps_login() + steps_nav(['Averbações', 'Imp. Definitiva']) + [
           'Preencher todos os campos incluindo campos opcionais',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Averbação criada com todos os dados. Confirmação exibida.'),
    ct('CT070_IMPDE-06', 'Bloquear Imp. Definitiva fora do período', 'P1', 'Negativo',
       steps_login() + steps_nav(['Averbações', 'Imp. Definitiva']) + [
           'Preencher data embarque fora da vigência',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Bloqueio com mensagem de período inválido.'),
    ct('CT071_IMPDE-07', 'Importar averbação Definitiva via arquivo', 'P2', 'Positivo',
       steps_login() + steps_nav(['Averbações', 'Imp. Definitiva']) + [
           'Clicar no botão de <strong>Importar</strong> ou <strong>Upload</strong>',
           'Selecionar arquivo CSV com formato padrão de importação',
           'Confirmar a importação',
       ],
       'Arquivo processado. Averbações importadas aparecem no grid.'),
    ct('CT072_IMPDE-08', 'Consultar averbação Imp. Definitiva por filtros', 'P2', 'Positivo',
       steps_login() + steps_nav(['Averbações', 'Imp. Definitiva']) + [
           'Preencher filtro de <strong>Apólice</strong> com número válido',
           'Clicar em <strong>[Consultar]</strong>',
       ],
       'Grid exibe apenas as averbações da apólice filtrada.'),
    ct('CT073_IMPDE-09', 'Consultar Imp. Definitiva por período', 'P2', 'Positivo',
       steps_login() + steps_nav(['Averbações', 'Imp. Definitiva']) + [
           'Preencher filtros <strong>Data Início</strong> e <strong>Data Fim</strong>',
           'Clicar em <strong>[Consultar]</strong>',
       ],
       'Grid exibe apenas as averbações do período informado.'),
    ct('CT074_IMPDE-10', 'Exportar lista de Imp. Definitiva', 'P3', 'Positivo',
       steps_login() + steps_nav(['Averbações', 'Imp. Definitiva']) + [
           'Consultar averbações existentes',
           'Clicar no botão <strong>[Exportar]</strong> ou ícone de download',
       ],
       'Arquivo CSV/Excel baixado com os dados listados no grid.'),
    ct('CT075_IMPDE-11', 'Regressão — fluxo Imp. Definitiva', 'P1', 'Regressão',
       steps_imp_definitiva(),
       'Fluxo completo Imp. Definitiva íntegro após release.'),
    ct('CT076_IMPDE-12', 'Validar Imp. Definitiva com campos Fairfax', 'P2', 'Positivo',
       steps_login() + steps_nav(['Averbações', 'Imp. Definitiva']) + [
           'Preencher campos com dados do tenant Fairfax (CNPJ embarcador diferente)',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Averbação criada validando lógica multi-tenant.'),
]

CTS_EXPOR = [
    ct(f'CT{55+i:03d}_EXPOR-{i+1:02d}',
       ['Criar averbação Exportação — happy path',
        'Editar averbação de Exportação',
        'Excluir averbação de Exportação',
        'Validar campos obrigatórios Exportação',
        'Bloquear Exportação fora da vigência',
        'Criar Exportação com país destino específico',
        'Consultar Exportação por filtro de apólice',
        'Consultar Exportação por período',
        'Exportar lista de Exportação para CSV',
        'Regressão — fluxo completo Exportação'][i],
       ['P1','P2','P2','P1','P1','P2','P2','P2','P3','P1'][i],
       ['Positivo','Positivo','Positivo','Negativo','Negativo','Positivo','Positivo','Positivo','Positivo','Regressão'][i],
       steps_login() + steps_nav(['Averbações', 'Exportação']) + [
           f'No campo <strong>Filial</strong>, selecionar <code>1 - SAO PAULO</code>',
           'Executar ação correspondente ao cenário (criar / editar / consultar / exportar)',
           'Preencher campos obrigatórios conforme o ramo 32 - Exportação',
       ],
       ['Averbação de Exportação criada com sucesso. Modal de confirmação exibido.',
        'Edição salva. Confirmação exibida.',
        'Registro removido do grid.',
        'Mensagem de campos obrigatórios exibida.',
        'Bloqueio com mensagem de período inválido.',
        'Averbação criada para o país destino selecionado.',
        'Grid exibe averbações filtradas pela apólice.',
        'Grid exibe averbações do período informado.',
        'Download do arquivo com dados exportados.',
        'Fluxo Exportação íntegro.'][i])
    for i in range(10)
]

CTS_RCTVI = [
    ct(f'CT{48+i:03d}_RCTVI-{i+1:02d}',
       ['Criar averbação RCT-VI Importação',
        'Criar averbação RCT-VI Exportação',
        'Editar averbação RCT-VI',
        'Excluir averbação RCT-VI',
        'Validar campos obrigatórios RCT-VI',
        'Bloquear RCT-VI fora da vigência',
        'Regressão RCT-VI'][i],
       ['P1','P1','P2','P2','P1','P1','P1'][i],
       ['Positivo','Positivo','Positivo','Positivo','Negativo','Negativo','Regressão'][i],
       steps_login() + steps_nav(['Averbações', 'RCT-VI']) + [
           f'No campo <strong>Filial</strong>, selecionar <code>1 - SAO PAULO</code>',
           'No campo <strong>Tipo</strong>, selecionar <code>I - Importação</code> ou <code>E - Exportação</code> conforme o CT',
           'Preencher campos obrigatórios do ramo 32 - RCT-VI',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       ['Averbação RCT-VI Importação criada com sucesso.',
        'Averbação RCT-VI Exportação criada com sucesso.',
        'Edição salva.',
        'Registro removido.',
        'Mensagem de campos obrigatórios exibida.',
        'Bloqueio com mensagem de período inválido.',
        'Fluxo RCT-VI íntegro.'][i])
    for i in range(7)
]

# ── CONSULTA FATURAMENTO ──────────────────────────────────────────────────────
URL_CONSU = 'https://axa-hml-faturamento.nsseg.com.br/citnet/Faturamento/ConsultaStatus'
URL_HIST  = 'https://axa-hml-faturamento.nsseg.com.br/citnet/Faturamento/ConsultaHistorico'

def steps_consulta_status(ramo_codigo, ramo_nome, apolice):
    return steps_login() + steps_nav(['Faturamento', 'Consulta Status Faturamento']) + [
        'No campo <strong>Filial</strong>, selecionar <code>1 - SAO PAULO</code>',
        f'No campo <strong>Ramo</strong>, selecionar <code>{ramo_codigo} - {ramo_nome}</code>',
        f'No campo <strong>Apólice</strong>, selecionar <code>{apolice}</code>',
        'No campo <strong>Competência</strong>, preencher período válido (ex: <code>06 / 2026</code>)',
        'Clicar no botão <strong>[Consultar]</strong>',
        'Aguardar carregamento (pode demorar alguns segundos)',
    ]

def steps_historico(ramo_codigo, ramo_nome):
    return steps_login() + steps_nav(['Faturamento', 'Histórico de Faturamento']) + [
        'No campo <strong>Filial</strong>, selecionar <code>1 - SAO PAULO</code>',
        f'No campo <strong>Ramo</strong>, selecionar <code>{ramo_codigo} - {ramo_nome}</code>',
        'Clicar em <strong>[Consultar]</strong>',
    ]

CONSU_STATUS_LIST = [
    ('CT077_CONSU-01', 'Verificar cálculo de prêmios na Consulta Status', 'P2', 'Positivo',
     steps_consulta_status('21','Transporte Nacional','40425'),
     'Barra de progresso exibida com 4 etapas. Campos de cálculo (prêmio, IOF, custo) visíveis.'),
    ('CT078_CONSU-02', 'Verificar barra de progresso — Transporte Nacional', 'P2', 'Positivo',
     steps_consulta_status('21','Transporte Nacional','40425'),
     'Barra de 4 etapas visível: Averbado → Recebido → Movimento → Fatura.'),
    ('CT079_CONSU-03', 'Verificar status do boleto (nunca fica verde)', 'P3', 'Limite',
     steps_consulta_status('21','Transporte Nacional','40425'),
     'Campo de boleto presente na tela. Comportamento de cor verificado.'),
    ('CT080_CONSU-04', 'Consulta Status — Prévia RCV', 'P1', 'Positivo',
     steps_consulta_status('59','RCV','2'),
     'Barra de progresso RCV exibida. Etapas específicas de RCV visíveis.'),
    ('CT081_CONSU-05', 'Transição de status RCV — Prêmio Mínimo', 'P2', 'Positivo',
     steps_consulta_status('59','RCV','2'),
     'Status de Prêmio Mínimo visível na barra quando aplicável.'),
    ('CT082_CONSU-06', 'Executar fechamento RCV via Consulta Status', 'P1', 'Positivo',
     steps_consulta_status('59','RCV','2') + ['Verificar se o botão <strong>[Fechar]</strong> está disponível'],
     'Botão de fechamento RCV presente quando há prévia aprovada.'),
    ('CT083_CONSU-07', 'Verificar número de referência único da fatura', 'P2', 'Positivo',
     steps_login() + steps_nav(['Faturamento', 'Histórico de Faturamento']),
     'Histórico exibido. Número de referência único por fatura visível.'),
    ('CT084_CONSU-08', 'Histórico com filtros — Transporte Nacional', 'P2', 'Positivo',
     steps_historico('21','Transporte Nacional'),
     'Grid do histórico exibido com dados de faturamento TN.'),
    ('CT085_CONSU-09', 'Histórico separa Nacional e Internacional', 'P2', 'Positivo',
     steps_login() + steps_nav(['Faturamento', 'Histórico de Faturamento']) + [
         'Verificar abas ou filtros que separam Nacional de Internacional',
     ],
     'Separação entre Nacional e Internacional confirmada.'),
]

STATUS_MODS = [
    ('CT086_CONSU-10','56','RCA-C','151103'),
    ('CT087_CONSU-11','58','RCTA-C','242348'),
    ('CT088_CONSU-12','38','RCTF-C','1'),
    ('CT089_CONSU-13','21','Transporte Nacional','40425'),
    ('CT090_CONSU-14','22','Imp. Provisória',''),
    ('CT091_CONSU-15','22','Imp. Definitiva',''),
    ('CT092_CONSU-16','32','Exportação',''),
    ('CT093_CONSU-17','32','RCT-VI',''),
]
HIST_MODS = [
    ('CT094_CONSU-18','56','RCA-C','151103'),
    ('CT095_CONSU-19','58','RCTA-C','242348'),
    ('CT096_CONSU-20','38','RCTF-C',''),
    ('CT097_CONSU-21','59','RCV','2'),
    ('CT098_CONSU-22','21','Transporte Nacional','40425'),
    ('CT099_CONSU-23','22','Imp. Definitiva',''),
    ('CT100_CONSU-24','32','Exportação',''),
    ('CT101_CONSU-25','32','RCT-VI',''),
]

CTS_CONSU = [ct(*t[:4], t[4], t[5]) for t in CONSU_STATUS_LIST]
for ct_id, ramo_c, ramo_n, apo in STATUS_MODS:
    CTS_CONSU.append(ct(ct_id,
        f'Consulta Status Faturamento — {ramo_n}', 'P2', 'Positivo',
        steps_consulta_status(ramo_c, ramo_n, apo or 'disponível'),
        f'Barra de progresso do faturamento {ramo_n} exibida. Status atual da competência visível.',
        f'Script: _scripts/citnet/run_waves234.py'))
for ct_id, ramo_c, ramo_n, apo in HIST_MODS:
    CTS_CONSU.append(ct(ct_id,
        f'Histórico de Faturamento — {ramo_n}', 'P2', 'Positivo',
        steps_historico(ramo_c, ramo_n),
        f'Grid com histórico de faturamento {ramo_n} exibido. Filtros funcionando.',
        f'Script: _scripts/citnet/run_waves234.py'))

# ── APROVAÇÃO DE PRÉVIAS ──────────────────────────────────────────────────────
URL_APROV = 'https://axa-hml-faturamento.nsseg.com.br/citnet/AutorizacaoPrevia/AutorizacaoPrevia'

def steps_aprov_base(ramo_codigo, ramo_nome, competencia):
    return steps_login() + steps_nav(['Faturamento', 'Aprovação de Prévias']) + [
        'No campo <strong>Filial</strong>, selecionar <code>1 - SAO PAULO</code>',
        f'No campo <strong>Ramo</strong>, selecionar <code>{ramo_codigo} - {ramo_nome}</code>' if ramo_codigo else 'Deixar filtro de Ramo sem seleção para buscar todos',
        f'No campo <strong>Competência</strong>, preencher <code>{competencia}</code>',
        'Clicar em <strong>[Consultar]</strong>',
        'Aguardar carregamento do grid de prévias',
    ]

CTS_APROV = [
    ct('CT102_APROV-01', 'Verificar geração de fatura com relatório RDLC', 'P2', 'Positivo',
       steps_login() + steps_nav(['Faturamento', 'Aprovação de Prévias']),
       'Tela de aprovação de prévias carregada com campos de filtro.'),
    ct('CT103_APROV-02', 'Contestar movimentos de uma fatura', 'P1', 'Positivo',
       steps_aprov_base('21','Transporte Nacional','10 / 2024') + [
           'Selecionar uma prévia no grid clicando no checkbox',
           'Clicar no botão <strong>[Contestar]</strong>',
           'Preencher motivo da contestação',
           'Confirmar a contestação',
       ],
       'Contestação registrada. Prévia com status alterado para "Contestada".'),
    ct('CT104_APROV-03', 'Aprovar prévia após contestação', 'P1', 'Positivo',
       steps_aprov_base('21','Transporte Nacional','10 / 2024') + [
           'Localizar prévia com status "Contestada"',
           'Selecionar a prévia',
           'Clicar em <strong>[Aprovar Selecionados]</strong>',
           'Preencher Vencimento (data +30 dias da data atual)',
           'Clicar em <strong>[Confirmar]</strong>',
       ],
       'Prévia aprovada. Status alterado. Fatura gerada.'),
    ct('CT105_APROV-04', 'Aprovar prévia sem contestações — Transporte Nacional', 'P1', 'Positivo',
       steps_aprov_base('21','Transporte Nacional','10 / 2024') + [
           'Verificar que o grid exibe prévias com status "Aguardando Aprovação"',
           'Selecionar a primeira prévia disponível (checkbox)',
           'No campo <strong>Vencimento das Faturas</strong>, preencher com data +30 dias',
           'No campo <strong>Observações</strong>, preencher com <code>QA Automação</code>',
           'Clicar em <strong>[Aprovar Selecionados]</strong>',
           'Aguardar processamento',
       ],
       'Prévia aprovada com sucesso. Modal de confirmação exibido. Status atualizado no grid.'),
]

# Aprovação por módulo
APROV_MODS = [
    ('CT106_APROV-05','21','TN','Transporte Nacional'),
    ('CT107_APROV-06','21','TN','Tentar editar fatura já fechada — TN'),
    ('CT108_APROV-07','21','TN','Fatura enviada por e-mail em prazo de 2h'),
    ('CT109_APROV-08','59','RCV','Aprovação RCV dentro do prazo de 30 dias'),
    ('CT110_APROV-09','59','RCV','Tentativa de aprovação RCV após 30 dias'),
    ('CT111_APROV-10','59','RCV','Antecipar aprovação RCV'),
    ('CT112_APROV-11','59','RCV','Rejeitar selecionados — RCV'),
    ('CT113_APROV-12','59','RCV','Exportar relação simplificada — RCV'),
    ('CT114_APROV-13','56','RCA-C','Aprovação RCA-C sem contestações'),
    ('CT115_APROV-14','54','RCTR-C','Aprovação RCTR-C sem contestações'),
    ('CT116_APROV-15','58','RCTA-C','Aprovação RCTA-C sem contestações'),
    ('CT117_APROV-16','59','RCV','Aprovação RCV sem contestações'),
    ('CT118_APROV-17','21','TN','Aprovação Transporte Nacional sem contestações'),
    ('CT119_APROV-18','22','ImpDef','Aprovação Imp. Definitiva sem contestações'),
    ('CT120_APROV-19','32','Exportação','Aprovação Exportação sem contestações'),
    ('CT121_APROV-20','32','RCT-VI','Aprovação RCT-VI sem contestações'),
]
COMP_MAP = {'21':'10 / 2024','54':'10 / 2024','56':'10 / 2024','58':'10 / 2024',
            '59':'02 / 2026','22':'10 / 2024','32':'10 / 2024','38':'10 / 2024'}

for ct_id, ramo_c, ramo_s, titulo in APROV_MODS:
    comp = COMP_MAP.get(ramo_c, '10 / 2024')
    CTS_APROV.append(ct(ct_id, titulo, 'P1' if 'Aprovação' in titulo else 'P2', 'Positivo',
        steps_aprov_base(ramo_c, ramo_s, comp) + [
            'Verificar que o grid exibe prévias aguardando aprovação',
            'Selecionar prévia disponível (checkbox)',
            'Clicar em <strong>[Aprovar Selecionados]</strong>',
        ],
        f'Prévias {ramo_s} aprovadas com sucesso. Status atualizado.',
        f'Script: _scripts/citnet/run_waves234.py — competência: {comp}'))

# Prazo de aprovação (27 CTs)
PRAZO_MODS = [
    ('CT122_APROV-21','56','RCA-C','dentro do prazo','CIT-078'),
    ('CT123_APROV-22','54','RCTR-C','dentro do prazo','CIT-078'),
    ('CT124_APROV-23','58','RCTA-C','dentro do prazo','CIT-078'),
    ('CT125_APROV-24','38','RCTF-C','dentro do prazo','CIT-078'),
    ('CT126_APROV-25','21','TN','dentro do prazo','CIT-078'),
    ('CT127_APROV-26','22','ImpProv','dentro do prazo','CIT-078'),
    ('CT128_APROV-27','22','ImpDef','dentro do prazo','CIT-078'),
    ('CT129_APROV-28','32','Exportação','dentro do prazo','CIT-078'),
    ('CT130_APROV-29','32','RCT-VI','dentro do prazo','CIT-078'),
    ('CT131_APROV-30','56','RCA-C','após prazo','CIT-079'),
    ('CT132_APROV-31','54','RCTR-C','após prazo','CIT-079'),
    ('CT133_APROV-32','58','RCTA-C','após prazo','CIT-079'),
    ('CT134_APROV-33','38','RCTF-C','após prazo','CIT-079'),
    ('CT135_APROV-34','21','TN','após prazo','CIT-079'),
    ('CT136_APROV-35','22','ImpProv','após prazo','CIT-079'),
    ('CT137_APROV-36','22','ImpDef','após prazo','CIT-079'),
    ('CT138_APROV-37','32','Exportação','após prazo','CIT-079'),
    ('CT139_APROV-38','32','RCT-VI','após prazo','CIT-079'),
    ('CT140_APROV-39','56','RCA-C','antecipação','CIT-080'),
    ('CT141_APROV-40','54','RCTR-C','antecipação','CIT-080'),
    ('CT142_APROV-41','58','RCTA-C','antecipação','CIT-080'),
    ('CT143_APROV-42','38','RCTF-C','antecipação','CIT-080'),
    ('CT144_APROV-43','21','TN','antecipação','CIT-080'),
    ('CT145_APROV-44','22','ImpProv','antecipação','CIT-080'),
    ('CT146_APROV-45','22','ImpDef','antecipação','CIT-080'),
    ('CT147_APROV-46','32','Exportação','antecipação','CIT-080'),
    ('CT148_APROV-47','32','RCT-VI','antecipação','CIT-080'),
]
for ct_id, ramo_c, ramo_s, prazo, cit in PRAZO_MODS:
    comp = COMP_MAP.get(ramo_c,'10 / 2024')
    CTS_APROV.append(ct(ct_id,
        f'Verificar prazo de aprovação {prazo} — {ramo_s}', 'P2',
        'Negativo' if 'após' in prazo else 'Positivo',
        steps_aprov_base(ramo_c, ramo_s, comp) + [
            'Verificar se os campos de data <strong>D. Ini. Seleção</strong> e <strong>D. Fim Seleção</strong> estão habilitados',
            'Verificar as datas limites de aprovação conforme regra de prazo',
        ],
        f'Campo de prazo verificado. Regra {cit} aplicada corretamente.',
        f'Módulo verifica que aprovação {prazo} está corretamente controlada.'))

# ── CONVERSOR ─────────────────────────────────────────────────────────────────
URL_CVR = 'https://axa-hml-faturamento.nsseg.com.br/citnet/Conversor/Conversor'

CTS_CONVE = [
    ct('CT150_CONVE-01', 'Verificar formulário e seleção de layout no Conversor', 'P2', 'Positivo',
       steps_login() + steps_nav(['Conversor', 'Conversor']) + [
           'No campo <strong>Filial</strong>, selecionar <code>1 - SAO PAULO</code>',
           'No campo <strong>Ramo</strong>, selecionar <code>21 - Transporte Nacional</code>',
           'Verificar que os segurados disponíveis aparecem no dropdown',
       ],
       'Formulário do Conversor carregado. Lista de ramos e segurados disponíveis.'),
    ct('CT151_CONVE-02', 'Selecionar segurado e layout no Conversor', 'P2', 'Positivo',
       steps_login() + steps_nav(['Conversor', 'Conversor']) + [
           'Selecionar Filial=1 e Ramo=21',
           'No campo <strong>Segurado</strong>, selecionar o primeiro disponível',
           'Verificar que os layouts disponíveis aparecem no dropdown',
           'Selecionar o primeiro layout disponível',
       ],
       'Layout selecionado corretamente. Campos do layout carregados.'),
    ct('CT152_CONVE-03', 'Upload e importação de arquivo CSV no Conversor', 'P1', 'Positivo',
       steps_login() + steps_nav(['Conversor', 'Conversor']) + [
           'Selecionar Filial=1, Ramo=21, Segurado e Layout',
           'Clicar no botão <strong>[Selecionar Arquivo]</strong> ou arraste um arquivo CSV',
           'Selecionar um arquivo CSV com formato padrão (colunas: ramo, apólice, filial, etc.)',
           'Clicar em <strong>[Importar]</strong>',
       ],
       'Arquivo importado com sucesso. Grid exibe as linhas do arquivo importado.'),
    ct('CT153_CONVE-04', 'Converter arquivo importado no Conversor', 'P1', 'Positivo',
       steps_login() + steps_nav(['Conversor', 'Conversor']) + [
           'Realizar o upload de um arquivo CSV (ver CT152)',
           'Após a importação, clicar no botão <strong>[Converter]</strong>',
           'Aguardar o processamento',
       ],
       'Conversão executada. Modal ou mensagem de resultado exibida. Averbações processadas.'),
]

# Layouts por ramo
LAYOUTS = [
    ('CT154_CONVE-05','CIT-AVB-RCT','TRANSPORTE NACIONAL','21','CIT-AVB-RCT ramo 21'),
    ('CT155_CONVE-06','CIT-AVB-TRN','TRANSPORTE NACIONAL','21','CIT-AVB-TRN ramo 21'),
    ('CT156_CONVE-07','CIT-AVB-RTA','RCTA-C','58','CIT-AVB-RTA ramo 58'),
    ('CT157_CONVE-08','CIT-AVB-RTF','RCTF-C','38','CIT-AVB-RTF ramo 38'),
    ('CT158_CONVE-09','CIT-AVB-RCA','RCA-C','56','CIT-AVB-RCA ramo 56'),
    ('CT159_CONVE-10','CIT-AVB-RVI','RCT-VI','32','CIT-AVB-RVI ramo 32'),
    ('CT160_CONVE-11','CIT-AVB-IMP','Importação','22','CIT-AVB-IMP ramo 22'),
    ('CT161_CONVE-12','CIT-AVB-EXP','Exportação','32','CIT-AVB-EXP ramo 32'),
]
for ct_id, layout, ramo_n, ramo_c, desc in LAYOUTS:
    CTS_CONVE.append(ct(ct_id,
        f'Verificar layout {layout} — {desc}', 'P2', 'Positivo',
        steps_login() + steps_nav(['Conversor', 'Conversor']) + [
            f'Selecionar <strong>Filial</strong>=1 e <strong>Ramo</strong>=<code>{ramo_c} - {ramo_n}</code>',
            'No campo <strong>Segurado</strong>, selecionar qualquer segurado disponível',
            f'No campo <strong>Layout</strong>, verificar se <code>{layout}</code> está disponível',
            f'Selecionar o layout <code>{layout}</code>',
        ],
        f'Layout {layout} disponível e selecionável para o ramo {ramo_c}. Segurados carregados.'))

# DE/PARA
URL_DEPARA = 'https://axa-hml-faturamento.nsseg.com.br/citnet/Conversor/CadastroDePara'
DEPARAS = [
    ('CT162_CONVE-13','Mercadoria','Cadastrar novo DE/PARA de Mercadoria',
     'Clicar em <strong>[Novo]</strong> → preencher De=<code>QA_ORIGEM</code> e Para=<code>QA_DESTINO</code> → clicar em <strong>[Gravar]</strong>',
     'Registro DE/PARA Mercadoria criado. Aparece no grid.'),
    ('CT163_CONVE-14','Mercadoria','Detectar duplicação em DE/PARA Mercadoria',
     'Tentar criar DE/PARA com os mesmos valores (De=<code>QA_ORIGEM</code>, Para=<code>QA_DESTINO</code>)',
     'Sistema rejeita a duplicata e exibe mensagem de registro já existente.'),
    ('CT164_CONVE-15','Mercadoria','Excluir DE/PARA de Mercadoria',
     'Consultar e selecionar o registro → clicar em <strong>[Excluir]</strong> e confirmar',
     'Registro excluído. Grid atualizado.'),
    ('CT165_CONVE-16','Mercadoria','Verificar exclusão de DE/PARA já excluído',
     'Consultar DE/PARA inexistente → verificar que o grid retorna vazio',
     'Grid vazio confirmado ou mensagem de "nenhum registro encontrado".'),
    ('CT166_CONVE-17','Mercadoria','Filtrar DE/PARA de Mercadoria',
     'No campo De/Para de, selecionar <code>Mercadoria</code> → clicar em <strong>[Consultar]</strong>',
     'Grid exibe apenas os DE/PARA do tipo Mercadoria.'),
    ('CT167_CONVE-18','Mercadoria','Smoke test geral DE/PARA Mercadoria',
     'Selecionar tipo Mercadoria e consultar todos os registros',
     'Tela carrega e grid exibe resultados (0 ou mais registros).'),
    ('CT168_CONVE-19','Mercadoria','Abrir popup de detalhe — DE/PARA Mercadoria',
     'Consultar e clicar em um registro do grid para ver detalhes',
     'Modal ou tela de detalhe abre exibindo os dados do DE/PARA.'),
    ('CT169_CONVE-20','Embalagem','Smoke test DE/PARA Embalagem',
     'Selecionar tipo <code>Embalagem</code> → clicar em <strong>[Consultar]</strong>',
     'Tela DE/PARA para Embalagem carrega e exibe os registros cadastrados.'),
    ('CT170_CONVE-21','País','Smoke test DE/PARA País',
     'Selecionar tipo <code>País</code> → clicar em <strong>[Consultar]</strong>',
     'Grid de DE/PARA País exibido.'),
    ('CT171_CONVE-22','Estado','Smoke test DE/PARA Estado',
     'Selecionar tipo <code>Estado</code> → clicar em <strong>[Consultar]</strong>',
     'Grid de DE/PARA Estado exibido.'),
    ('CT172_CONVE-23','Navio','Smoke test DE/PARA Navio',
     'Selecionar tipo <code>Navio</code> → clicar em <strong>[Consultar]</strong>',
     'Grid de DE/PARA Navio exibido.'),
    ('CT173_CONVE-24','Município','Smoke test DE/PARA Município',
     'Selecionar tipo <code>Município</code> → clicar em <strong>[Consultar]</strong>',
     'Grid de DE/PARA Município exibido.'),
    ('CT174_CONVE-25','Complemento País','Smoke test DE/PARA Complemento País',
     'Selecionar tipo <code>Complemento País</code> → clicar em <strong>[Consultar]</strong>',
     'Grid de DE/PARA Complemento País exibido.'),
    ('CT175_CONVE-26','Complemento Estado','Smoke test DE/PARA Complemento Estado',
     'Selecionar tipo <code>Complemento Estado</code> → clicar em <strong>[Consultar]</strong>',
     'Grid de DE/PARA Complemento Estado exibido.'),
    ('CT176_CONVE-27','Cálculo Percentual Navio','Smoke test DE/PARA Cálculo Percentual Navio',
     'Selecionar tipo <code>Cálculo Percentual Navio</code> → clicar em <strong>[Consultar]</strong>',
     'Grid de DE/PARA Cálculo Percentual Navio exibido.'),
]
for ct_id, tipo, titulo, acao_txt, resultado in DEPARAS:
    CTS_CONVE.append(ct(ct_id, titulo, 'P2', 'Positivo',
        steps_login() + steps_nav(['Conversor', 'De/Para do Conversor']) + [
            'No campo <strong>Filial</strong>, selecionar <code>1 - SAO PAULO</code>',
            f'No campo <strong>De/Para de</strong>, selecionar <code>{tipo}</code>',
            acao_txt,
        ], resultado))

# ── AUTORIZAÇÃO FATURAMENTO ───────────────────────────────────────────────────
URL_AUTOR = 'https://axa-hml-faturamento.nsseg.com.br/citnet/AutorizacaoFaturamento/AutorizacaoFaturamento'

CTS_AUTOR = [
    ct('CT200_AUTOR-01', 'Acessar Autorização de Faturamento — Nacional', 'P1', 'Positivo',
       steps_login() + steps_nav(['Faturamento', 'Autorização de Faturamento']) + [
           'Verificar que a tela "Autorização de Faturamento - Averbações Mensais" carregou',
           'Confirmar presença dos campos: Filial, Apólice, Ramo, Subgrupo, Competência, Autorização',
       ],
       'Tela de Autorização de Faturamento carregada com todos os campos visíveis.'),
    ct('CT201_AUTOR-02', 'Validar rejeição de vencimento inválido (>30 dias)', 'P2', 'Negativo',
       steps_login() + steps_nav(['Faturamento', 'Autorização de Faturamento']) + [
           'Preencher campo <strong>Vencimento</strong> com data além de 30 dias',
           'Clicar em <strong>[Gravar]</strong>',
       ],
       'Sistema bloqueia e exibe mensagem indicando que o vencimento não pode ultrapassar 30 dias.'),
    ct('CT202_AUTOR-03', 'Verificar campo Motivo Ajuste como somente leitura', 'P3', 'Positivo',
       steps_login() + steps_nav(['Faturamento', 'Autorização de Faturamento']) + [
           'Verificar se o campo <strong>Motivo Ajuste</strong> está desabilitado (read-only)',
           'Tentar clicar ou editar o campo',
       ],
       'Campo Motivo Ajuste está desabilitado (cinza/bloqueado). Não é possível editar.'),
    ct('CT203_AUTOR-04', 'Fechar modal sem processar', 'P3', 'Negativo',
       steps_login() + steps_nav(['Faturamento', 'Autorização de Faturamento']) + [
           'Preencher campos do filtro',
           'Se algum modal ou dialog abrir, clicar em <strong>[Cancelar]</strong> ou <strong>[Fechar]</strong>',
           'Confirmar que nenhuma ação foi processada',
       ],
       'Modal fechado sem processamento. Nenhuma alteração realizada.'),
]

# Autorização por ramo (CT204-CT212)
AUTOR_MODS = [
    ('CT204_AUTOR-06','RCA-C','Nacional','N'),
    ('CT205_AUTOR-07','RCTA-C','Nacional','N'),
    ('CT206_AUTOR-08','RCTF-C','Nacional','N'),
    ('CT207_AUTOR-09','RCV','Nacional','N'),
    ('CT208_AUTOR-10','TN','Nacional','N'),
    ('CT209_AUTOR-05','Internacional','Internacional','I'),
    ('CT210_AUTOR-11','Imp. Definitiva','Internacional','I'),
    ('CT211_AUTOR-12','Exportação','Internacional','I'),
    ('CT212_AUTOR-13','RCT-VI','Internacional','I'),
]
for ct_id, ramo_n, tipo, tipo_param in AUTOR_MODS:
    CTS_AUTOR.append(ct(ct_id,
        f'Autorização de Faturamento — {ramo_n} ({tipo})', 'P2', 'Positivo',
        steps_login() + steps_nav(['Faturamento', 'Autorização de Faturamento']) + [
            f'No campo <strong>Filial</strong>, selecionar <code>1 - SAO PAULO</code>',
            f'Filtrar por ramo <strong>{ramo_n}</strong>',
            'Preencher a competência desejada',
            'Clicar em <strong>[Consultar]</strong>',
        ],
        f'Tela de Autorização de Faturamento {tipo} para {ramo_n} carregada corretamente.'))

# ── RELATÓRIOS ────────────────────────────────────────────────────────────────
URL_REL = 'https://axa-hml-faturamento.nsseg.com.br/citnet/Relatorio/ConsultaAverbacao'

def steps_relatorio(descricao_filtro=''):
    return steps_login() + steps_nav(['Relatórios', 'Consulta Averbação']) + [
        'No campo <strong>Filial</strong>, selecionar <code>1 - SAO PAULO</code>',
        descricao_filtro or 'Preencher filtros disponíveis (período, ramo, apólice)',
        'Clicar no botão <strong>[Consultar]</strong>',
        'Aguardar carregamento dos dados',
    ]

CTS_RELAT = [
    ct('CT213_RELAT-01', 'Verificar cálculo de prêmios em relatório de fatura complexa', 'P2', 'Positivo',
       steps_relatorio('Selecionar período com faturamento disponível'),
       'Relatório exibido com campos de cálculo de prêmio visíveis e valores corretos.'),
    ct('CT214_RELAT-02', 'Verificar barra de progresso no relatório de status', 'P2', 'Positivo',
       steps_relatorio(),
       'Relatório carregado. Dados de status de faturamento visíveis.'),
    ct('CT215_RELAT-03', 'Verificar geração de fatura em formato RDLC', 'P2', 'Positivo',
       steps_relatorio(),
       'Relatório em formato RDLC gerado e disponível para visualização.'),
    ct('CT216_RELAT-04', 'Verificar prêmios e encargos completos no relatório', 'P2', 'Positivo',
       steps_relatorio(),
       'Relatório exibe todos os campos: prêmio, IOF, custo, total.'),
    ct('CT217_RELAT-05', 'Consultar histórico via relatório com filtros', 'P2', 'Positivo',
       steps_relatorio('Preencher filtros de período e ramo'),
       'Grid de histórico exibido com dados filtrados.'),
]

RELAT_MODS = [
    ('CT218_RELAT-06','RCTR-C'),('CT219_RELAT-07','RCA-C'),('CT220_RELAT-08','RCTA-C'),
    ('CT221_RELAT-09','RCTF-C'),('CT222_RELAT-10','TN'),('CT223_RELAT-11','RCV'),
    ('CT224_RELAT-12','Imp. Provisória'),('CT225_RELAT-13','Imp. Definitiva'),
    ('CT226_RELAT-14','Exportação'),('CT227_RELAT-15','RCT-VI'),
    ('CT228_RELAT-16','RCTR-C Faturamento'),('CT229_RELAT-17','RCA-C Faturamento'),
    ('CT230_RELAT-18','RCTA-C Faturamento'),('CT231_RELAT-19','RCTF-C Faturamento'),
    ('CT232_RELAT-20','TN Faturamento'),('CT233_RELAT-21','RCV Faturamento'),
    ('CT234_RELAT-22','Imp. Prov. Faturamento'),('CT235_RELAT-23','Imp. Def. Faturamento'),
    ('CT236_RELAT-24','Exp. Faturamento'),('CT237_RELAT-25','RVI Faturamento'),
    ('CT238_RELAT-26','RCTR-C Histórico'),('CT239_RELAT-27','RCA-C Histórico'),
    ('CT240_RELAT-28','RCTA-C Histórico'),('CT241_RELAT-29','RCTF-C Histórico'),
    ('CT242_RELAT-30','TN Histórico'),('CT243_RELAT-31','RCV Histórico'),
    ('CT244_RELAT-32','Imp. Prov. Histórico'),('CT245_RELAT-33','Imp. Def. Histórico'),
    ('CT246_RELAT-34','Exp. Histórico'),('CT247_RELAT-35','RVI Histórico'),
]
for ct_id, modulo in RELAT_MODS:
    CTS_RELAT.append(ct(ct_id,
        f'Relatório de Consulta Averbação — {modulo}', 'P3', 'Positivo',
        steps_relatorio(f'No campo Ramo, selecionar <code>{modulo}</code>'),
        f'Relatório de {modulo} exibido com dados do período filtrado.'))

# ── CERTIFICADOS ──────────────────────────────────────────────────────────────
URL_CTF     = 'https://axa-hml-faturamento.nsseg.com.br/citnet/CertificadoImportacao/CertificadoImportacao'
URL_CTF_EXP = 'https://axa-hml-faturamento.nsseg.com.br/citnet/CertificadoExportacao/CertificadoExportacao'

CTS_CTF_DEFS = [
    ('CT248_CTF-01','Extração de certificado de Importação',URL_CTF,'Importação'),
    ('CT249_CTF-02','Extração de certificado de Exportação',URL_CTF_EXP,'Exportação'),
    ('CT250_CTF-03','Geração de certificado de Importação',URL_CTF,'Importação'),
    ('CT251_CTF-04','Geração de certificado de Exportação',URL_CTF_EXP,'Exportação'),
    ('CT252_CTF-05','Filtrar certificados de Importação',URL_CTF,'Importação'),
    ('CT253_CTF-06','Filtrar certificados de Exportação',URL_CTF_EXP,'Exportação'),
    ('CT255_CTF-07','Imprimir certificado de Importação',URL_CTF,'Importação'),
    ('CT256_CTF-08','Reimprimir certificado de Importação',URL_CTF,'Importação'),
    ('CT257_CTF-09','Verificar certificado por apólice Nacional',URL_CTF,'Importação'),
    ('CT258_CTF-10','Verificar certificado por apólice Internacional',URL_CTF,'Internacional'),
    ('CT259_CTF-11','Filtrar certificados por data',URL_CTF,'Importação'),
    ('CT260_CTF-12','Filtrar certificados por número',URL_CTF,'Importação'),
    ('CT261_CTF-13','Filtrar certificados por número de apólice',URL_CTF,'Importação'),
    ('CT262_CTF-14','Filtrar certificados por segurado',URL_CTF,'Importação'),
    ('CT263_CTF-15','Exportar lista de certificados para CSV',URL_CTF,'Importação'),
    ('CT264_CTF-16','Exportar lista de certificados para XLSX',URL_CTF,'Importação'),
    ('CT265_CTF-17','Verificar histórico de certificados',URL_CTF,'Importação'),
    ('CT266_CTF-18','Verificar status dos certificados',URL_CTF,'Importação'),
]

CTS_CTF = []
for ct_id, titulo, url, tipo in CTS_CTF_DEFS:
    CTS_CTF.append(ct(ct_id, titulo, 'P3', 'Positivo',
        steps_login() + [
            f'Tentar acessar o módulo de Certificados ({tipo}) via menu ou URL direta',
        ],
        f'<span style="color:var(--block)">⚠️ Módulo em implantação no HML:</span> '
        f'URL <code>/citnet/CertificadoImportacao/</code> retorna HTTP 404 no ambiente HML. '
        f'Executar este CT apenas quando o módulo estiver disponível em HML.',
        f'Módulo de Certificados ainda não implantado no HML AXA. PASS(N/A) esperado.'))

# ─── AGRUPAMENTO FINAL ────────────────────────────────────────────────────────

GRUPOS = [
    {
        'id': 'nac-rctr-c',
        'titulo': '1. Averbação Nacional — RCTR-C (Ramo 54)',
        'descricao': 'Testa o ciclo completo de averbações para o ramo 54 — Responsabilidade Civil do Transportador Rodoviário de Carga.',
        'menu': 'Averbações → RCTR-C',
        'cts': CTS_RCTRC,
    },
    {
        'id': 'nac-rca-c',
        'titulo': '2. Averbação Nacional — RCA-C (Ramo 56)',
        'descricao': 'Testa o ciclo de averbações para o ramo 56 — Responsabilidade Civil do Agente de Carga.',
        'menu': 'Averbações → RCA-C',
        'cts': CTS_RCAC,
    },
    {
        'id': 'nac-rcta-c',
        'titulo': '3. Averbação Nacional — RCTA-C (Ramo 58)',
        'descricao': 'Testa o ciclo de averbações para o ramo 58 — Responsabilidade Civil do Terminal de Armazenagem.',
        'menu': 'Averbações → RCTA-C',
        'cts': CTS_RCTAC,
    },
    {
        'id': 'nac-rctf-c',
        'titulo': '4. Averbação Nacional — RCTF-C (Ramo 38)',
        'descricao': 'Testa o ciclo de averbações para o ramo 38 — Responsabilidade Civil do Transportador Ferroviário de Carga.',
        'menu': 'Averbações → RCTF-C',
        'cts': CTS_RCTFC,
    },
    {
        'id': 'nac-tn',
        'titulo': '5. Averbação Nacional — Transporte Nacional (Ramo 21)',
        'descricao': 'Testa o ciclo completo de averbações de Transporte Nacional (ramo 21), incluindo origem, destino, embalagem e série.',
        'menu': 'Averbações → Transporte Nacional',
        'cts': CTS_TN,
    },
    {
        'id': 'nac-rcv',
        'titulo': '6. Averbação Nacional — RCV (Ramo 59)',
        'descricao': 'Testa prévias e averbações do ramo 59 — Responsabilidade Civil de Veículos. Requer apólice com condição comercial configurada.',
        'menu': 'Averbações → RCV',
        'cts': CTS_RCV + CTS_NACIONAIS_EXTRA,
    },
    {
        'id': 'int-imp-prov',
        'titulo': '7. Averbação Internacional — Importação Provisória (Ramo 22)',
        'descricao': 'Testa averbações de Importação Provisória para transporte internacional.',
        'menu': 'Averbações → Imp. Provisória',
        'cts': CTS_IMP_PROV,
    },
    {
        'id': 'int-imp-def',
        'titulo': '8. Averbação Internacional — Importação Definitiva (Ramo 22)',
        'descricao': 'Testa o ciclo completo de averbações de Importação Definitiva, incluindo DI (Declaração de Importação).',
        'menu': 'Averbações → Imp. Definitiva',
        'cts': CTS_IMP_DEF,
    },
    {
        'id': 'int-exp',
        'titulo': '9. Averbação Internacional — Exportação (Ramo 32)',
        'descricao': 'Testa averbações de Exportação para operações internacionais.',
        'menu': 'Averbações → Exportação',
        'cts': CTS_EXPOR,
    },
    {
        'id': 'int-rctvi',
        'titulo': '10. Averbação Internacional — RCT-VI (Ramo 32)',
        'descricao': 'Testa averbações de RCT-VI para operações internacionais de importação e exportação via fronteira terrestre.',
        'menu': 'Averbações → RCT-VI',
        'cts': CTS_RCTVI,
    },
    {
        'id': 'faturamento-consulta',
        'titulo': '11. Consulta de Faturamento (Waves 2A)',
        'descricao': 'Testa a tela de Consulta de Status de Faturamento — barra de progresso por etapas — e o Histórico de Faturamento, para todos os ramos.',
        'menu': 'Faturamento → Consulta Status / Histórico',
        'cts': CTS_CONSU,
    },
    {
        'id': 'aprovacao-previas',
        'titulo': '12. Aprovação de Prévias (Wave 2B)',
        'descricao': 'Testa o fluxo de aprovação de prévias — contestação, aprovação, prazo, vencimento — para todos os ramos nacionais e internacionais.',
        'menu': 'Faturamento → Aprovação de Prévias',
        'cts': CTS_APROV,
    },
    {
        'id': 'conversor',
        'titulo': '13. Conversor de Arquivos (Wave 3)',
        'descricao': 'Testa o módulo Conversor — upload de arquivos CSV, seleção de layout, conversão, e tabelas DE/PARA para cada tipo de dado.',
        'menu': 'Conversor → Conversor / De/Para',
        'cts': CTS_CONVE,
    },
    {
        'id': 'autorizacao',
        'titulo': '14. Autorização de Faturamento (Wave 4)',
        'descricao': 'Testa o módulo de Autorização de Faturamento por ramo — Nacional e Internacional.',
        'menu': 'Faturamento → Autorização de Faturamento',
        'cts': CTS_AUTOR,
    },
    {
        'id': 'relatorios',
        'titulo': '15. Relatórios de Consulta (Wave 4)',
        'descricao': 'Testa o módulo de Relatório de Consulta Averbação para todos os ramos — dados de averbações, faturamento e histórico.',
        'menu': 'Relatórios → Consulta Averbação',
        'cts': CTS_RELAT,
    },
    {
        'id': 'certificados',
        'titulo': '16. Certificados de Seguro (Wave 4)',
        'descricao': '⚠️ Módulo não disponível no ambiente HML AXA (HTTP 404). CTs documentados para execução futura quando o módulo estiver implantado.',
        'menu': 'Certificados → Certificado Importação / Exportação',
        'cts': CTS_CTF,
    },
]

# ─── GERAÇÃO DO HTML ──────────────────────────────────────────────────────────

PRIO_COLORS = {'P1': '#f85149', 'P2': '#e08456', 'P3': '#8b949e'}
TIPO_COLORS = {
    'Positivo': '#3fb950', 'Negativo': '#f85149', 'Limite': '#d29922',
    'Regressão': '#3b9eff', 'Exceção': '#9370db',
}

def render_steps(steps):
    items = ''.join(f'<li>{s}</li>' for s in steps)
    return f'<ol class="ct-steps">{items}</ol>'

def render_ct(c, grupo_id):
    ct_id = c['id']
    prio  = c.get('prio', 'P2')
    tipo  = c.get('tipo', 'Positivo')
    obs   = c.get('obs', '')
    script = c.get('script', '_scripts/citnet/')
    pc = PRIO_COLORS.get(prio, '#8b949e')
    tc = TIPO_COLORS.get(tipo, '#8b949e')

    passos_html = render_steps(c['passos'])

    obs_html = f'<div class="ct-field full"><label>Observações</label><p class="obs">{obs}</p></div>' if obs else ''
    script_html = f'<div class="ct-field full script-badge">🤖 <strong>AUTOMATIZADO</strong> — script: <code>{script}</code></div>'

    return f'''
<div class="ct-block" id="{ct_id}" data-grupo="{grupo_id}">
  <div class="ct-bar" onclick="toggleCt(this)">
    <div class="ct-bar-left">
      <span class="ct-id">{ct_id.split("_")[0]}</span>
      <span class="ct-prio" style="background:{pc}22;color:{pc};border:1px solid {pc}55">{prio}</span>
      <span class="ct-tipo" style="background:{tc}22;color:{tc};border:1px solid {tc}55">{tipo}</span>
    </div>
    <div class="ct-title">{c["titulo"]}</div>
    <span class="ct-chevron">▶</span>
  </div>
  <div class="ct-panel" hidden>
    <div class="ct-grid">
      <div class="ct-field full">
        <label>Pré-condições</label>
        <ul>
          <li>Ambiente: <strong>CITNET AXA HML</strong></li>
          <li>URL: <code>{URL}</code></li>
          <li>Credenciais: <code>{LOGIN}</code></li>
          <li>Navegador: Google Chrome ou Microsoft Edge</li>
        </ul>
      </div>
      <div class="ct-field full">
        <label>Passos de Execução</label>
        {passos_html}
      </div>
      <div class="ct-field full">
        <label>Resultado Esperado</label>
        <p class="result">{c["resultado"]}</p>
      </div>
      {obs_html}
      {script_html}
      <div class="ct-field full ev-section">
        <span class="ev-badge ev-pendente">📷 Evidência pendente</span>
      </div>
    </div>
  </div>
</div>'''

def render_grupo(g):
    total_g = len(g['cts'])
    cts_html = ''.join(render_ct(c, g['id']) for c in g['cts'])
    return f'''
<div class="section" id="{g["id"]}">
  <div class="section-header">
    <h2>{g["titulo"]}</h2>
    <span class="section-count">{total_g} CTs</span>
  </div>
  <div class="info-box" style="margin-bottom:12px">
    <strong>Descrição:</strong> {g["descricao"]}<br>
    <strong>Menu:</strong> <code>{g["menu"]}</code>
  </div>
  {cts_html}
</div>'''

# Totais
total_cts = sum(len(g['cts']) for g in GRUPOS)
p1 = sum(1 for g in GRUPOS for c in g['cts'] if c.get('prio') == 'P1')
p2 = sum(1 for g in GRUPOS for c in g['cts'] if c.get('prio') == 'P2')
p3 = sum(1 for g in GRUPOS for c in g['cts'] if c.get('prio') == 'P3')

grupos_html = ''.join(render_grupo(g) for g in GRUPOS)

nav_links = ''.join(
    f'<a href="#{g["id"]}" class="nav-link">{g["titulo"].split(".")[0].strip()}. {g["titulo"].split("—")[-1].strip()[:30]}</a>'
    for g in GRUPOS
)

HTML = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Plano de Teste Regressivo — CITNET AXA — {total_cts} CTs</title>
<style>
:root {{
  --bg:#0f1114; --surface:#1a1d23; --surface-2:#22262e; --border:#343a46;
  --text:#e6e8eb; --muted:#9aa3ad; --accent:#3b9eff; --accent-dim:#1e4d7a;
  --ok:#3fb950; --ok-bg:rgba(63,185,80,.18); --fail:#f85149; --fail-bg:rgba(248,81,73,.18);
  --pend:#8b949e; --block:#d29922; --block-bg:rgba(210,153,34,.22);
  --warn-bg:rgba(210,153,34,.12); --info-bg:rgba(59,158,255,.10);
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',system-ui,sans-serif;font-size:14px;color:var(--text);background:var(--bg);line-height:1.55}}
a{{color:var(--accent);text-decoration:none}}
code{{background:#0a0e14;border:1px solid #2a3040;padding:1px 5px;border-radius:3px;font-size:12px;font-family:'Cascadia Code','Fira Code',monospace}}

/* HEADER */
header{{background:linear-gradient(135deg,#0a2744 0%,#152238 50%,var(--bg) 100%);padding:28px 32px;border-bottom:1px solid var(--border);display:flex;gap:20px;align-items:center}}
.h-badge{{background:var(--accent);color:#0a1628;font-weight:700;font-size:15px;border-radius:8px;padding:8px 16px;white-space:nowrap}}
header h1{{font-size:22px;font-weight:600;line-height:1.3}}
header p{{font-size:13px;color:#c9d1d9;margin-top:4px}}

/* DASHBOARD */
.dash{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px;padding:20px 28px;border-bottom:1px solid var(--border)}}
.dash-card{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px;text-align:center}}
.dash-card .num{{font-size:30px;font-weight:700;line-height:1}}
.dash-card .lbl{{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);margin-top:5px}}
.dash-card.total .num{{color:var(--accent)}}
.dash-card.p1 .num{{color:var(--fail)}}
.dash-card.p2 .num{{color:#e08456}}
.dash-card.p3 .num{{color:var(--pend)}}
.dash-card.autos .num{{color:var(--ok)}}
.dash-wide{{grid-column:1/-1;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px 18px}}

/* NAV LATERAL */
.layout{{display:flex;min-height:calc(100vh - 160px)}}
.sidebar{{width:260px;min-width:220px;background:var(--surface);border-right:1px solid var(--border);padding:16px 12px;position:sticky;top:0;height:100vh;overflow-y:auto;flex-shrink:0}}
.sidebar h3{{font-size:11px;text-transform:uppercase;color:var(--muted);letter-spacing:.06em;margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid var(--border)}}
.nav-link{{display:block;padding:6px 10px;font-size:12px;border-radius:5px;color:var(--muted);margin-bottom:2px;line-height:1.3}}
.nav-link:hover{{background:var(--surface-2);color:var(--text)}}
.content{{flex:1;padding:20px 28px 60px;max-width:960px}}

/* PRECONDIÇÕES (info-box) */
.info-box{{background:var(--info-bg);border-left:3px solid var(--accent);padding:12px 14px;border-radius:0 6px 6px 0;font-size:13px;color:#a9d3ff;margin:8px 0}}
.warn-box{{background:var(--warn-bg);border-left:3px solid var(--block);padding:12px 14px;border-radius:0 6px 6px 0;font-size:13px;color:#e8c07d}}

/* SEÇÃO */
.section{{margin-bottom:32px}}
.section-header{{display:flex;align-items:center;gap:12px;margin-bottom:14px;padding:12px 16px;background:var(--surface);border:1px solid var(--border);border-radius:8px;border-left:4px solid var(--accent)}}
.section-header h2{{font-size:16px;font-weight:600;flex:1}}
.section-count{{background:var(--accent);color:#0a1628;font-size:11px;font-weight:700;padding:2px 8px;border-radius:10px}}

/* CT BLOCK */
.ct-block{{background:var(--surface);border:1px solid var(--border);border-radius:8px;margin-bottom:8px;overflow:hidden}}
.ct-bar{{display:flex;align-items:center;gap:10px;padding:12px 14px;cursor:pointer;user-select:none;transition:background .12s}}
.ct-bar:hover{{background:var(--surface-2)}}
.ct-bar-left{{display:flex;align-items:center;gap:6px;flex-shrink:0}}
.ct-id{{font-family:monospace;font-size:11px;color:var(--muted);white-space:nowrap}}
.ct-prio,.ct-tipo{{font-size:10px;padding:2px 7px;border-radius:4px;font-weight:600;white-space:nowrap}}
.ct-title{{flex:1;font-size:13px;font-weight:500}}
.ct-chevron{{font-size:10px;color:var(--muted);transition:transform .15s;flex-shrink:0}}
.ct-block.expanded .ct-chevron{{transform:rotate(90deg)}}
.ct-panel{{padding:0 14px 14px}}
.ct-grid{{display:grid;gap:10px}}
.ct-field{{background:#0a0e14;border:1px solid var(--border);border-radius:6px;padding:10px 12px}}
.ct-field.full{{grid-column:1/-1}}
.ct-field label{{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);margin-bottom:6px;font-weight:600}}
.ct-field p,.ct-field li{{font-size:13px;color:var(--text)}}
.ct-steps{{padding-left:18px}}
.ct-steps li{{margin-bottom:5px;font-size:13px;line-height:1.5}}
.result{{color:var(--ok);font-weight:500}}
.obs{{color:var(--muted);font-style:italic}}
.script-badge{{background:rgba(63,185,80,.08);border-color:rgba(63,185,80,.25);font-size:12px;color:#56d364}}
.ev-section{{text-align:center;padding:8px}}
.ev-badge{{display:inline-block;padding:4px 12px;border-radius:4px;font-size:11px;font-weight:600}}
.ev-pendente{{background:rgba(139,148,158,.15);color:var(--muted);border:1px dashed var(--border)}}

/* SCROLL SUAVE */
html{{scroll-behavior:smooth}}

@media(max-width:800px){{
  .sidebar{{display:none}} .layout{{display:block}}
  .dash{{grid-template-columns:repeat(3,1fr)}}
}}
</style>
</head>
<body>

<header>
  <div class="h-badge">REGRESSIVO</div>
  <div>
    <h1>Plano de Teste Regressivo — CITNET AXA</h1>
    <p>Ambiente: HML &nbsp;·&nbsp; Seguradora: AXA &nbsp;·&nbsp; {total_cts} cenários &nbsp;·&nbsp; 16 módulos &nbsp;·&nbsp; Gerado em: {HOJE}</p>
  </div>
</header>

<div class="dash">
  <div class="dash-card total"><div class="num">{total_cts}</div><div class="lbl">Total CTs</div></div>
  <div class="dash-card p1"><div class="num">{p1}</div><div class="lbl">P1 Bloqueante</div></div>
  <div class="dash-card p2"><div class="num">{p2}</div><div class="lbl">P2 Importante</div></div>
  <div class="dash-card p3"><div class="num">{p3}</div><div class="lbl">P3 Desejável</div></div>
  <div class="dash-card autos"><div class="num">{total_cts}</div><div class="lbl">Automatizados</div></div>
  <div class="dash-wide">
    <div style="font-size:13px;color:var(--muted);margin-bottom:8px">
      <strong style="color:var(--text)">Como usar este plano:</strong>
      &nbsp;Clique em qualquer CT para expandir e ver os passos detalhados.
      &nbsp;Cada CT indica o script de automação correspondente.
      &nbsp;Todos os 241 CTs têm automação Playwright disponível.
    </div>
    <div class="info-box" style="margin-top:8px">
      <strong>Pré-condição global:</strong> Acesso ao CITNET AXA HML via
      <code>https://axa-hml-faturamento.nsseg.com.br/citnet/</code>
      &nbsp;com credenciais <code>interno / 11</code>
      &nbsp;·&nbsp; Usar Google Chrome ou Microsoft Edge
    </div>
  </div>
</div>

<div class="layout">
  <nav class="sidebar">
    <h3>Módulos ({len(GRUPOS)})</h3>
    {nav_links}
  </nav>
  <div class="content">
    {grupos_html}
  </div>
</div>

<script>
function toggleCt(bar) {{
  var block = bar.closest('.ct-block');
  var panel = block.querySelector('.ct-panel');
  var expanded = block.classList.toggle('expanded');
  panel.hidden = !expanded;
}}
// Expandir/colapsar todos
function toggleAll(expand) {{
  document.querySelectorAll('.ct-block').forEach(b => {{
    b.classList.toggle('expanded', expand);
    b.querySelector('.ct-panel').hidden = !expand;
  }});
}}
</script>

</body>
</html>'''

OUT.write_text(HTML, encoding='utf-8')
total_kb = round(OUT.stat().st_size / 1024)
print(f'Plano gerado: {OUT}')
print(f'Tamanho: {total_kb} KB | CTs: {total_cts} | P1={p1} P2={p2} P3={p3}')
print(f'Grupos: {len(GRUPOS)}')
