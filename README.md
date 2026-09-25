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

Para especificar uma pasta de destino diferente:
```bash
python3 baixar_curriculos.py /caminho/para/pasta
```

---

## ⚙️ Configurações Rápidas

As opções principais ficam no topo de [`baixar_curriculos.py`](baixar_curriculos.py):

* **`MIN_ID`** (`3526`): baixa apenas os currículos com ID igual ou superior ao informado.
* **`DEFAULT_OUTPUT_DIR`** (`~/Downloads/curriculos`): diretório padrão onde os currículos serão salvos.

---

## ⚡ Recursos da Automação

* **Filtro de ID:** ignora registros antigos abaixo do ID definido.
* **Sem Duplicados:** descarta envios repetidos de um mesmo candidato/cargo ou mesmo arquivo.
* **Sanitização de Nomes:** substitui barras (`/`) e caracteres inválidos por `-` para não gerar erros no sistema de arquivos.
* **Download Rápido:** downloads simultâneos em paralelo (10 workers).
