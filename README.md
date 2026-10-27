# Orbital Globe Lab — controle por movimento

Globo 3D com **Three.js**, conexões geográficas, exploração automática, rotas animadas, painel de telemetria e **controle pela webcam em Python**, sem aranhas.

## Gestos

- **Mão aberta em movimento:** gira o globo.
- **Polegar e indicador em pinça:** abrir os dedos aproxima; fechar afasta.
- **Mão fechada:** pausa os comandos gestuais.
- **Sem mão detectada:** o controle gestual aguarda; rotação automática pode continuar.
- Mouse, toque e botões de zoom continuam disponíveis.

O Python usa OpenCV e MediaPipe para obter os 21 pontos da mão. A imagem da webcam permanece **somente no seu computador**. O navegador recebe apenas valores de movimento via WebSocket local, sem transmitir imagens.

## 1. Instalar Python 3.11 no Windows

Se aparecer o erro "Python não foi encontrado", instale no PowerShell:

~~~powershell
winget install --id Python.Python.3.11 -e
~~~

Feche e abra o PowerShell e confirme:

~~~powershell
py -3.11 --version
~~~

Alternativa: instalador oficial em https://www.python.org/downloads/.

## 2. Preparar o projeto

Abra a pasta do repositório no PowerShell e execute:

~~~powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
~~~

## 3. Abrir globo e webcam

~~~powershell
.\.venv\Scripts\python.exe app.py
~~~

O Python abre o navegador em http://127.0.0.1:8000 e uma janela com a webcam mostrando os pontos dos dedos. **Pressione Q ou ESC na janela da câmera** para sair.

Para tentar outra webcam:

~~~powershell
.\.venv\Scripts\python.exe app.py --camera 1
~~~

No Windows, habilite o acesso à câmera em Configurações → Privacidade e segurança → Câmera e feche aplicativos que estejam utilizando a câmera.

## 4. Modo sem webcam

Com Node.js instalado:

~~~powershell
npx --yes serve . -l 8000
~~~

Abra http://localhost:8000. O painel mostrará "Webcam desconectada" porque o servidor estático não possui o serviço Python, mas todas as funções manuais do globo permanecem disponíveis.

## Funcionalidades

- Globo WebGL com rotação e zoom por mouse ou toque
- Marcadores, coordenadas clicáveis e arcos de conexão
- Exploração automática, pausa, seleção de destinos e limpeza das rotas
- Partículas luminosas, som opcional e telemetria
- Controle gestual por Python + MediaPipe + OpenCV
- Configurações locais persistentes, interface responsiva e FPS
- Respeita a preferência por movimento reduzido

## Arquivos

- index.html — interface
- styles.css — design responsivo
- src/main.js — globo 3D e comunicação por WebSocket
- app.py — servidor local e rastreamento da mão
- requirements.txt — dependências Python

## Observações

- Three.js e a textura terrestre são carregados pela internet, com textura de reserva para falhas no download da imagem.
- O Python **não roda automaticamente no GitHub Pages**. O controle por webcam só funciona ao executar app.py localmente.
- As rotas são simulações visuais, não dados de tráfego geográfico em tempo real.
- Mantenha a mão bem iluminada e totalmente visível para melhorar o rastreamento.
