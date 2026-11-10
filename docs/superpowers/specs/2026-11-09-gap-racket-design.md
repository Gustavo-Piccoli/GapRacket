# GapRacket — Design

Data: 2026-11-09

## Objetivo

Jogo/brinquedo de física extremamente simples em Python: uma raquete controlada pelo mouse, presa por um elástico a uma bolinha. A bolinha quica na raquete e nas bordas da tela. Sem pontuação, sem vitória/derrota — o foco é brincar com os parâmetros físicos em tempo real através de um menu de pausa.

## Escopo

Um único jogo local, sem rede, sem persistência de save. Rodado com `python main.py`. Biblioteca gráfica: Pygame puro (sem lib de UI adicional).

## Arquitetura

Módulos em `src/gapracket/`:

- `config.py` — dataclass `PhysicsConfig` com todos os parâmetros ajustáveis, cada um com valor default, mínimo, máximo e step (usados tanto pela simulação quanto pelos sliders do menu).
- `physics.py` — funções puras (sem estado, fáceis de testar): força do elástico (mola + damping), gravidade, arrasto do meio (viscosidade), integração de movimento (Euler semi-implícito), colisão bolinha↔raquete e bolinha↔paredes da tela.
- `entities.py` — classes `Ball` (posição, velocidade, raio, massa) e `Paddle` (posição, velocidade derivada do movimento do mouse, tamanho).
- `pause_menu.py` — overlay desenhado em Pygame com um slider por parâmetro de `PhysicsConfig`, incluindo um slider de "viscosidade do meio" com marcadores/presets (vácuo, ar, água, mel) que apenas ajustam o valor do slider de arrasto para um valor pré-definido.
- `game.py` — loop principal: captura eventos, atualiza física (quando não pausado), desenha cena, alterna pause/resume.
- `main.py` — ponto de entrada: cria a janela Pygame e inicia `game.py`.

## Física

Todas as forças são somadas e integradas a cada frame (Euler semi-implícito: atualiza velocidade primeiro, depois posição).

**Elástico (mola + damping)**, ligando a raquete à bolinha:
```
dir = (pos_raquete - pos_bolinha) normalizado
dist = |pos_raquete - pos_bolinha|
se dist <= comprimento_natural:
    F_elastico = 0   # frouxo — comporta-se como um elástico de borracha
                     # de verdade, não como uma haste rígida que também
                     # empurra quando comprimida
senão:
    F_elastico = k * (dist - comprimento_natural) * dir
               - c * (v_bolinha - v_raquete) projetada em dir
```
- `k` = coeficiente elástico (configurável)
- `comprimento_natural` = distância de repouso (configurável)
- `c` = coeficiente de amortecimento do elástico (configurável)

**Gravidade:**
```
F_gravidade = (0, massa_bolinha * g)
```
- `g` = gravidade (configurável)
- `massa_bolinha` = massa da bolinha (configurável)

**Arrasto do meio (viscosidade):**
```
F_arrasto = -viscosidade * v_bolinha
```
- `viscosidade` = coeficiente de arrasto linear (configurável); presets no menu (vácuo=0, ar, água, mel) apenas setam esse valor.

**Colisão bolinha↔raquete:**
- Detectada por distância (círculo-retângulo ou círculo-círculo, dependendo da forma final da raquete).
- Reflete a componente normal da velocidade relativa (bolinha em relação à raquete) multiplicada pelo coeficiente de restituição configurável.
- A velocidade da raquete (derivada do deslocamento do mouse entre frames) soma um "empurrão" à bolinha no momento do impacto, para que mover o mouse rápido dê uma tacada mais forte.

**Colisão bolinha↔paredes:**
- Ao atingir qualquer borda da tela, inverte a componente de velocidade perpendicular à parede, multiplicada pelo mesmo coeficiente de restituição.

## Parâmetros configuráveis (menu de pausa)

| Parâmetro | Afeta |
|---|---|
| Coeficiente elástico (k) | Força da mola do elástico |
| Comprimento natural do elástico | Distância de repouso do elástico |
| Coeficiente de amortecimento do elástico (c) | Perda de energia da oscilação do elástico |
| Massa da bolinha | Inércia da bolinha, peso da gravidade |
| Gravidade (g) | Força constante para baixo |
| Coeficiente de restituição | "Quique" nas colisões bolinha↔raquete e bolinha↔paredes |
| Viscosidade do meio | Arrasto/resistência do ar/água/etc sobre a bolinha (com presets vácuo/ar/água/mel) |
| Raio da bolinha | Tamanho da bolinha, área de colisão |
| Tamanho da raquete | Tamanho da raquete, área de colisão |

Cada parâmetro tem um slider no overlay de pausa, com valor numérico exibido ao lado.

## Controles

- Mover o mouse → move a raquete livremente em X e Y.
- Tecla `ESC` ou `P` → pausa/retoma o jogo e mostra/esconde o overlay de configurações.
- Overlay de pausa: sliders ajustáveis por clique e arraste do mouse.

## Estrutura de arquivos

```
GapRacket/
├── src/
│   └── gapracket/
│       ├── __init__.py
│       ├── config.py
│       ├── physics.py
│       ├── entities.py
│       ├── pause_menu.py
│       └── game.py
├── tests/
│   └── test_physics.py
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
└── docs/superpowers/specs/2026-11-09-gap-racket-design.md
```

## Testes

Testes unitários (`pytest`) cobrindo as funções puras de `physics.py`: cálculo da força elástica (mola + damping), força de gravidade, força de arrasto, um passo de integração, e as reflexões de velocidade nas colisões (bolinha↔raquete e bolinha↔paredes). Não há teste automatizado da janela gráfica — verificação visual manual roda o jogo e confere o comportamento.

## Fora de escopo

- Pontuação, vitória/derrota, múltiplos níveis.
- Persistência de configurações entre execuções.
- Suporte a múltiplas bolinhas/raquetes.
- Multiplayer ou rede.

## Repositório

- Nome: `GapRacket`, público, na conta pessoal do GitHub do usuário.
- README com instruções de instalação (`pip install -r requirements.txt`) e execução (`python main.py`), e explicação dos parâmetros configuráveis.
- Licença MIT.
- `.gitignore` padrão Python (`__pycache__/`, `.venv/`, etc).
