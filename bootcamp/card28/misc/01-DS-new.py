import os
import argparse
import re

def renomear_imagens(pasta_entrada, pasta_saida, prefixo):
    """
    Renomeia arquivos de imagem em uma pasta, com índice inicial informado pelo usuário.

    Args:
        pasta_entrada (str): Pasta com as imagens originais.
        pasta_saida (str): Pasta para salvar as imagens renomeadas.
        prefixo (str): Prefixo para os nomes dos arquivos (ex.: 'cheia').
    """
    # Cria a pasta de saída, se não existir
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)

    # Lista os arquivos de imagem na pasta de entrada
    extensoes_validas = ('.jpg', '.jpeg', '.png')
    arquivos_entrada = [f for f in os.listdir(pasta_entrada) if f.lower().endswith(extensoes_validas)]
    if not arquivos_entrada:
        print("Nenhuma imagem encontrada na pasta de entrada!")
        return

    # Ordena os arquivos de entrada alfabeticamente
    arquivos_entrada.sort()

    # Lista os arquivos na pasta de saída
    arquivos_saida = [f for f in os.listdir(pasta_saida) if f.startswith(f'{prefixo}_') and f.endswith('.jpg')]
    
    # Ordena os arquivos de saída pelo número extraído do nome
    def extrair_indice(nome_arquivo):
        match = re.search(r'_(\d{3})\.jpg$', nome_arquivo)
        return int(match.group(1)) if match else float('inf')
    arquivos_saida.sort(key=extrair_indice)

    ### ALTERAÇÃO ###: Exibe os últimos 5 elementos da pasta de entrada
    print("\nÚltimos 5 arquivos da pasta de entrada:")
    for i, arquivo in enumerate(arquivos_entrada[-5:], start=len(arquivos_entrada)-4 if len(arquivos_entrada) >= 5 else 1):
        print(f"{i}: {arquivo}")

    ### ALTERAÇÃO ###: Exibe os últimos 5 elementos da pasta de saída
    print("\nÚltimos 5 arquivos da pasta de saída:")
    if arquivos_saida:
        for arquivo in arquivos_saida[-5:]:
            match = re.search(r'_(\d{3})\.jpg$', arquivo)
            if match:
                indice = int(match.group(1))
                print(f"{indice}: {arquivo}")
    else:
        print("Nenhum arquivo encontrado na pasta de saída.")

    ### ALTERAÇÃO ###: Solicita o índice inicial ao usuário
    while True:
        try:
            indice_inicial = int(input("\nDigite o índice inicial para a renomeação (ex.: 43): "))
            if indice_inicial > 0:
                break
            print("O índice deve ser um número positivo!")
        except ValueError:
            print("Entrada inválida! Digite um número inteiro.")

    # Ordena os arquivos de entrada para renomeação
    arquivos_entrada.sort()

    # Renomeia os arquivos
    for i, arquivo in enumerate(arquivos_entrada, start=indice_inicial):
        # Gera o novo nome com o índice formatado (ex.: cheia_043.jpg)
        novo_nome = f"{prefixo}_{i:03d}.jpg"
        caminho_antigo = os.path.join(pasta_entrada, arquivo)
        caminho_novo = os.path.join(pasta_saida, novo_nome)

        # Verifica se o novo nome já existe
        if os.path.exists(caminho_novo):
            print(f"Aviso: '{novo_nome}' já existe! Pulando {arquivo}.")
            continue

        # Copia o arquivo para o novo caminho
        try:
            os.rename(caminho_antigo, caminho_novo)
            print(f"Renomeado: {arquivo} -> {novo_nome}")
        except Exception as e:
            print(f"Erro ao renomear {arquivo}: {e}")

if __name__ == "__main__":
    ### ALTERAÇÃO ###: Configura o parser de argumentos sem indice_inicial
    parser = argparse.ArgumentParser(description="Renomeia imagens com um índice inicial informado pelo usuário.")
    parser.add_argument('--pasta_entrada', type=str, required=True, 
                        help="Caminho da pasta com as imagens originais")
    parser.add_argument('--pasta_saida', type=str, required=True, 
                        help="Caminho da pasta para salvar as imagens renomeadas")
    parser.add_argument('--prefixo', type=str, default='cheia', 
                        help="Prefixo para os nomes dos arquivos (padrão: 'cheia')")

    args = parser.parse_args()

    ### ALTERAÇÃO ###: Executa a renomeação sem indice_inicial
    renomear_imagens(args.pasta_entrada, args.pasta_saida, args.prefixo)
