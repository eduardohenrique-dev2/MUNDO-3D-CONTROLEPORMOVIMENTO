# Orbital Globe Lab

Aplicação 3D para explorar o globo, conectar destinos, observar rotas animadas, consultar coordenadas e monitorar indicadores locais. Focado exclusivamente no globo e em suas funcionalidades.

## Iniciar no Windows

Abra a pasta no VS Code, abra o PowerShell e execute:

```powershell
npx --yes serve . -l 8000
```

Abra http://localhost:8000 no navegador. Requer Node.js instalado, internet para Three.js e navegador compatível com WebGL.

## Recursos

- Giro e zoom do globo 3D por mouse ou toque
- Marcação de coordenadas clicando no planeta
- Destinos predefinidos e rotas curvas entre pontos
- Exploração automática e rotação automática opcionais
- Linhas com partículas, brilho e áudio opcional
- Indicadores e log de atividades (dados gerados pela simulação, não dados reais de tráfego)
- Painel responsivo e configurações salvas localmente
- Botões de pausa, limpeza, zoom e câmera

## Estrutura

index.html, styles.css e src/main.js. Sem backend.
