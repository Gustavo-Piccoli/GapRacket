# GapRacket

Um brinquedo de física extremamente simples: uma raquete controlada pelo mouse, presa por um elástico a uma bolinha. A bolinha quica na raquete e nas bordas da tela, com gravidade, arrasto do meio e um elástico de mola com amortecimento. Sem pontuação, sem vitória ou derrota — o foco é mover a raquete e brincar com os parâmetros físicos em tempo real.

## Instalação

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

> O projeto usa [`pygame-ce`](https://pyga.me/) (fork binário-compatível do `pygame`), porque o `pygame` ainda não publica wheel para versões muito recentes do Python. Ambos se importam como `pygame`.

## Como rodar

```bash
python main.py
```

## Controles

- **Mouse**: move a raquete livremente pela tela (eixos X e Y). A velocidade do movimento do mouse é transferida como "tacada" quando a raquete toca a bolinha.
- **ESC** ou **P**: pausa/retoma o jogo e mostra/esconde o menu de configurações. A raquete e a bolinha ficam congeladas enquanto pausado.
- No menu de pausa, arraste os sliders com o mouse para ajustar cada parâmetro em tempo real.

## Parâmetros configuráveis

| Parâmetro | Afeta |
|---|---|
| Coeficiente elástico (`elastic_k`) | Força da mola do elástico |
| Comprimento natural do elástico (`natural_length`) | Distância de repouso do elástico |
| Coeficiente de amortecimento do elástico (`damping`) | Perda de energia da oscilação do elástico |
| Massa da bolinha (`ball_mass`) | Inércia da bolinha, peso da gravidade |
| Gravidade (`gravity`) | Força constante para baixo |
| Coeficiente de restituição (`restitution`) | "Quique" nas colisões bolinha↔raquete e bolinha↔paredes |
| Viscosidade do meio (`viscosity`) | Arrasto/resistência sobre a bolinha — tem presets de vácuo, ar, água e mel |
| Raio da bolinha (`ball_radius`) | Tamanho da bolinha e área de colisão |
| Tamanho da raquete (`paddle_radius`) | Tamanho da raquete e área de colisão |

## Gerar um executável (.exe) para Windows

```bash
pip install -r requirements-build.txt
python scripts/generate_icon.py          # gera assets/icon.ico a partir das cores do jogo
pyinstaller --onefile --windowed --name GapRacket --icon assets/icon.ico --paths src main.py
```

O executável fica em `dist/GapRacket.exe` (standalone, não precisa de Python instalado). Para criar um atalho na área de trabalho com o ícone do jogo, no PowerShell:

```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$([Environment]::GetFolderPath('Desktop'))\GapRacket.lnk")
$Shortcut.TargetPath = "$PWD\dist\GapRacket.exe"
$Shortcut.IconLocation = "$PWD\assets\icon.ico"
$Shortcut.Save()
```

`dist/` e `build/` (artefatos gerados pelo PyInstaller) não são versionados.

## Testes

As funções de física (`src/gapracket/physics.py`, `simulation.py`, `entities.py`, `config.py`) são puras e têm testes automatizados. A janela gráfica (`game.py`, `pause_menu.py`) foi verificada só por scripts automatizados que chamam os métodos diretamente (sem interação real de mouse/teclado); jogue algumas partidas antes de confiar 100% na experiência interativa (mouse nos dois eixos, ESC/P, arrastar os sliders, os presets, tacadas rápidas, sliders nos extremos).

```bash
pytest
```
