#!/usr/bin/env python3
"""Baixa currículos da plataforma Escola em Site a partir de um ID inicial."""

import os
import re
import sys
import urllib.parse
from html import unescape
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

LOGIN_URL = "https://plataformaescolaemsite.com.br/login/acesso"
CURRICULOS_URL = "https://plataformaescolaemsite.com.br/curriculos"
DEFAULT_OUTPUT_DIR = os.path.expanduser("~/Downloads/curriculos")
MIN_ID = 4104
CHECKPOINT_FILE = "proximo_id.txt"

def load_min_id(output_dir: str) -> int:
    """Lê o próximo ID salvo ou usa o valor inicial do programa."""
    try:
        with open(os.path.join(output_dir, CHECKPOINT_FILE), encoding="utf-8") as f:
            min_id = int(f.read().strip())
        return min_id if min_id > 0 else MIN_ID
    except (OSError, ValueError):
        return MIN_ID

def save_min_id(output_dir: str, min_id: int):
    """Guarda o próximo ID fora do executável."""
    with open(os.path.join(output_dir, CHECKPOINT_FILE), "w", encoding="utf-8") as f:
        f.write(str(min_id))
    print(f"[+] Próximo ID automático: {min_id}")

def choose_min_id(automatic_min_id: int) -> int:
    """Permite usar o checkpoint automático ou informar o primeiro ID."""
    while True:
        print("\nEscolha o modo de download:")
        print(f"1) Baixar automaticamente a partir do ID {automatic_min_id}")
        print("2) Informar manualmente o primeiro ID")
        choice = input("Opção: ").strip()

        if choice == "1":
            return automatic_min_id
        if choice == "2":
            first_id = input("Primeiro ID para baixar: ").strip()
            if first_id.isdigit() and int(first_id) > 0:
                return int(first_id)
            print("[!] Digite um ID inteiro maior que zero.")
            continue
        print("[!] Escolha 1 ou 2.")

def sanitize_filename(text: str) -> str:
    """Remove ou substitui caracteres inválidos para nomes de arquivos."""
    # Substitui barras por hífen para não criar subpastas
    text = re.sub(r'[/\\:*?\"<>|]', '-', text)
    # Remove múltiplos espaços em branco
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_extension(url: str, content_type: str = "") -> str:
    """Extrai a extensão correta do arquivo."""
    # Tenta obter pelo final da URL
    path = urllib.parse.urlparse(url).path
    filename = os.path.basename(path)
    if '.' in filename:
        ext = '.' + filename.split('.')[-1].strip().lower()
        if ext in ['.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg']:
            return ext
    
    # Se a URL não tiver uma extensão limpa, infere pelo Content-Type
    if "pdf" in content_type.lower():
        return ".pdf"
    elif "wordprocessingml" in content_type.lower() or "docx" in content_type.lower():
        return ".docx"
    elif "msword" in content_type.lower():
        return ".doc"
    elif "png" in content_type.lower():
        return ".png"
    elif "jpeg" in content_type.lower() or "jpg" in content_type.lower():
        return ".jpg"
    
    return ".pdf"

def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    min_id = choose_min_id(load_min_id(output_dir))
    print(f"[*] Pasta de destino: {output_dir}")
    print(f"[*] Filtrando apenas currículos com ID >= {min_id}")

    session = requests.Session()

    # 1. Login
    print("[*] Realizando login...")
    login_resp = session.post(
        LOGIN_URL,
        data={"usuario": "curriculo", "senha": "curriculo"},
        timeout=15
    )
    if login_resp.status_code != 200:
        print(f"[!] Erro ao conectar no login: status {login_resp.status_code}")
        return

    # 2. Carrega a tabela de currículos
    print("[*] Obtendo lista de currículos...")
    resp = session.get(CURRICULOS_URL, timeout=30)
    if resp.status_code != 200:
        print(f"[!] Erro ao carregar página de currículos: status {resp.status_code}")
        return

    # 3. Parsing das linhas da tabela
    # Padrão: <td>ID</td> <td>Nome</td> <td>Whats</td> <td>Email</td> <td>Cargo</td> <td><a href="URL">...</td>
    pattern = re.compile(
        r'<tr>\s*<td>(\d+)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td><a href=\"(.*?)\"[^>]*>.*?</a></td>\s*<td>(.*?)</td>',
        re.DOTALL
    )
    rows = pattern.findall(resp.text)
    print(f"[*] Total de registros encontrados no site: {len(rows)}")

    # Filtra a partir do ID escolhido
    candidates = []
    for r in rows:
        cand_id = int(r[0])
        if cand_id >= min_id:
            nome = sanitize_filename(unescape(r[1]))
            cargo = sanitize_filename(unescape(r[4]))
            url = r[5].strip()
            data_cad = r[6].strip()
            candidates.append({
                "id": cand_id,
                "nome": nome,
                "cargo": cargo,
                "url": url,
                "data_cad": data_cad
            })

    print(f"[*] Currículos novos com ID >= {min_id}: {len(candidates)}")
    if not candidates:
        print(f"[*] Nenhum currículo novo com ID >= {min_id} encontrado no momento.")
        return
    max_site_id = max(c["id"] for c in candidates)

    # Ignora registros duplicados (mesmo nome + cargo ou mesma URL de arquivo)
    unique_candidates = []
    seen_keys = set()
    for cand in candidates:
        key = (cand["nome"].lower(), cand["cargo"].lower())
        if key not in seen_keys and cand["url"] not in seen_keys:
            seen_keys.add(key)
            seen_keys.add(cand["url"])
            cand["clean_base_name"] = f"{cand['nome']} - {cand['cargo']}"
            unique_candidates.append(cand)

    print(f"[*] Currículos únicos para baixar (sem duplicados): {len(unique_candidates)}")
    candidates = unique_candidates

    # 4. Download concorrente (rápido e eficiente)
    print("[*] Iniciando downloads...")
    sucessos = 0
    falhas = 0
    failed_ids = []

    def download_candidate(cand):
        url = cand["url"]
        # Codifica URLs com espaços ou caracteres especiais
        encoded_url = urllib.parse.quote(url, safe=':/?&=')
        try:
            r = session.get(encoded_url, timeout=20)
            if r.status_code == 200:
                ext = get_extension(url, r.headers.get("Content-Type", ""))
                filepath = os.path.join(output_dir, f"{cand['clean_base_name']}{ext}")
                with open(filepath, "wb") as f:
                    f.write(r.content)
                return True, cand["id"], cand["clean_base_name"], None
            else:
                return False, cand["id"], cand["clean_base_name"], f"HTTP {r.status_code}"
        except Exception as e:
            return False, cand["id"], cand["clean_base_name"], str(e)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(download_candidate, cand): cand for cand in candidates}
        for future in as_completed(futures):
            ok, cid, name, err = future.result()
            if ok:
                sucessos += 1
                print(f"[OK] [ID {cid}] {name}")
            else:
                falhas += 1
                failed_ids.append(cid)
                print(f"[FALHA] [ID {cid}] {name} -> {err}")

    print("\n" + "="*50)
    print(f"Download concluído!")
    print(f"Salvos com sucesso: {sucessos}")
    if falhas:
        print(f"Falhas (arquivos inacessíveis no servidor): {falhas}")
    print(f"Arquivos salvos em: {output_dir}")

    # Repete a partir da primeira falha para não perder nenhum currículo.
    save_min_id(output_dir, min(failed_ids) if failed_ids else max_site_id + 1)

    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[!] O programa encontrou um erro: {e}")
    finally:
        if getattr(sys, "frozen", False):
            input("\nPressione Enter para fechar...")
