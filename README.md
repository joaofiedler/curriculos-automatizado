# Downloader de Currículos - Escola em Site

Automação em Python para baixar e organizar currículos diretamente do painel administrativo da plataforma Escola em Site.

Os arquivos são salvos e renomeados automaticamente no formato:
```text
<Nome do Candidato> - <Cargo>.<extensão>
```

---

## 🚀 Como Usar no Windows

1. Baixe `BaixarCurriculos.exe`.
2. Abra o arquivo. O Windows pode pedir confirmação na primeira execução.
3. Escolha o modo automático ou informe o primeiro ID.

O programa cria `Downloads/curriculos`, salva os currículos nessa pasta e guarda o próximo ID em `proximo_id.txt`. A pessoa só precisa manter o `.exe`.

Ao iniciar, escolha uma opção:

1. Usar o `MIN_ID` salvo automaticamente na execução anterior.
2. Informar o primeiro ID que o programa deve baixar.

## Gerar o executável

O workflow `Gerar executável do Windows` gera um único `.exe` de 32 bits para Windows 7, 8.1, 10 e 11. Abra a aba **Actions** do GitHub, execute o workflow e baixe o artefato `BaixarCurriculos-Windows`.

---

## ⚙️ Configurações Rápidas

As opções principais ficam no topo de [`baixar_curriculos.py`](baixar_curriculos.py):

* **`MIN_ID`**: primeiro ID usado quando ainda não existe `proximo_id.txt`. Use a opção 2 para baixar novamente a partir de outro ID.
* **`DEFAULT_OUTPUT_DIR`** (`~/Downloads/curriculos`): diretório padrão onde os currículos serão salvos.

---

## ⚡ Recursos da Automação

* **Controle Automático de ID:** o programa salva `(último ID + 1)` em `proximo_id.txt`. Se algum download falhar, ele repete a partir da primeira falha na próxima execução.
* **Sem Duplicados:** descarta envios repetidos de um mesmo candidato/cargo ou mesmo arquivo.
* **Sanitização de Nomes:** substitui barras (`/`) e caracteres inválidos por `-` para não gerar erros no sistema de arquivos.
* **Download Rápido:** downloads simultâneos em paralelo (10 workers).
