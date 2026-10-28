# Downloader de Currículos - Escola em Site

Automação em Python para baixar e organizar currículos diretamente do painel administrativo da plataforma Escola em Site.

Os arquivos são salvos e renomeados automaticamente no formato:
```text
<Nome do Candidato> - <Cargo>.<extensão>
```

---

## 🚀 Como Usar

### 1. Pré-requisitos
Certifique-se de ter o Python 3 e a biblioteca `requests` instalados:
```bash
pip install requests
```

### 2. Executar
Para rodar com a pasta padrão (`~/Downloads/curriculos`):
```bash
python3 baixar_curriculos.py
```

Ao iniciar, escolha uma opção:

1. Usar o `MIN_ID` salvo automaticamente na execução anterior.
2. Informar o primeiro ID que o programa deve baixar.

Para especificar uma pasta de destino diferente:
```bash
python3 baixar_curriculos.py /caminho/para/pasta
```

---

## ⚙️ Configurações Rápidas

As opções principais ficam no topo de [`baixar_curriculos.py`](baixar_curriculos.py):

* **`MIN_ID`**: atualizado automaticamente para `(último ID baixado + 1)` a cada execução. Use a opção 2 para baixar novamente a partir de outro ID.
* **`DEFAULT_OUTPUT_DIR`** (`~/Downloads/curriculos`): diretório padrão onde os currículos serão salvos.

---

## ⚡ Recursos da Automação

* **Controle Automático de ID:** a cada execução concluída, o `MIN_ID` no script é atualizado automaticamente para `(último ID + 1)`, evitando que você precise mexer nele manualmente.
* **Sem Duplicados:** descarta envios repetidos de um mesmo candidato/cargo ou mesmo arquivo.
* **Sanitização de Nomes:** substitui barras (`/`) e caracteres inválidos por `-` para não gerar erros no sistema de arquivos.
* **Download Rápido:** downloads simultâneos em paralelo (10 workers).
