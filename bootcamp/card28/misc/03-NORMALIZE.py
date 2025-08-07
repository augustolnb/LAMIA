import os
import cv2
import numpy as np
import argparse
import re

def normalizar_imagens(pasta_entrada, pasta_saida):
    """
    Normaliza imagens para 128x128 em escala de cinza, com índice inicial informado pelo usuário.
    
    Args:
        pasta_entrada (str): Pasta com as imagens originais (inclui subpastas).
        pasta_saida (str): Pasta para salvar as imagens normalizadas.
    """
    # Cria a pasta de saída
    os.makedirs(pasta_saida, exist_ok=True)

    # Lista todas as imagens (incluindo subpastas)
    extensoes_validas = ('.jpg', '.jpeg', '.png')
    imagens = []
    for root, _, arquivos in os.walk(pasta_entrada):
        for arquivo in arquivos:
            if arquivo.lower().endswith(extensoes_validas):
                imagens.append(os.path.join(root, arquivo))
    
    if not imagens:
        print("Nenhuma imagem encontrada na pasta!")
        return

    ### ALTERAÇÃO ###: Ordena imagens pelo número extraído do nome
    def extrair_indice(caminho_arquivo):
        nome_arquivo = os.path.basename(caminho_arquivo)
        match = re.search(r'\d+', nome_arquivo)
        return int(match.group()) if match else float('inf')
    imagens.sort(key=extrair_indice)

    ### ALTERAÇÃO ###: Exibe os últimos 5 arquivos da pasta de entrada
    print("\nÚltimos 5 arquivos da pasta de entrada:")
    for caminho_imagem in imagens[-5:]:
        nome_arquivo = os.path.basename(caminho_imagem)
        match = re.search(r'\d+', nome_arquivo)
        indice = int(match.group()) if match else "N/A"
        print(f"{indice}: {nome_arquivo}")

    ### ALTERAÇÃO ###: Exibe os últimos 5 arquivos da pasta de saída
    print("\nÚltimos 5 arquivos da pasta de saída:")
    arquivos_saida = []
    for root, _, arquivos in os.walk(pasta_saida):
        for arquivo in arquivos:
            if arquivo.lower().endswith(extensoes_validas):
                arquivos_saida.append(os.path.join(root, arquivo))
    arquivos_saida.sort(key=extrair_indice)
    if arquivos_saida:
        for caminho_arquivo in arquivos_saida[-5:]:
            nome_arquivo = os.path.basename(caminho_arquivo)
            match = re.search(r'\d+', nome_arquivo)
            indice = int(match.group()) if match else "N/A"
            print(f"{indice}: {nome_arquivo}")
    else:
        print("Nenhum arquivo encontrado na pasta de saída.")

    ### ALTERAÇÃO ###: Solicita o índice inicial ao usuário
    while True:
        try:
            indice_inicial = int(input("\nDigite o número da imagem para começar (1 a {}): ".format(len(imagens))))
            if 1 <= indice_inicial <= len(imagens):
                break
            print("Índice inválido! Escolha um número entre 1 e {}.".format(len(imagens)))
        except ValueError:
            print("Entrada inválida! Digite um número inteiro.")

    # Ajusta o índice para começar do zero (para slicing)
    indice_inicial -= 1
    imagens = imagens[indice_inicial:]
    print(f"\nIniciando a partir da imagem: {os.path.basename(imagens[0])}")

    ### ALTERAÇÃO ###: Pergunta ao usuário se deseja visualizar as imagens
    while True:
        visualizar = input("Deseja visualizar as imagens normalizadas? (s/n): ").strip().lower()
        if visualizar in ['s', 'n']:
            break
        print("Resposta inválida! Digite 's' para sim ou 'n' para não.")

    # Processa as imagens
    for caminho_imagem in imagens:
        # Carrega a imagem
        img = cv2.imread(caminho_imagem)
        if img is None:
            print(f"Erro ao carregar {caminho_imagem}")
            continue

        # Redimensiona para 128x128
        img_resized = cv2.resize(img, (128, 128), interpolation=cv2.INTER_AREA)

        # Converte para escala de cinza
        img_gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)

        # Normaliza os valores para [0, 1]
        img_normalized = img_gray.astype(float) / 255.0

        # Converte de volta para uint8 para exibição e salvamento
        img_display = (img_normalized * 255).astype(np.uint8)

        # Salva a imagem processada
        nome_arquivo = os.path.basename(caminho_imagem)
        caminho_saida = os.path.join(pasta_saida, nome_arquivo)
        cv2.imwrite(caminho_saida, img_display)

        if visualizar == 's':
            cv2.imshow('Imagem Normalizada (128x128, Escala de Cinza)', img_display)
            print(f"Exibindo: {nome_arquivo} (pressione 'n' para próxima, 'q' para sair)")
            while True:
                key = cv2.waitKey(0) & 0xFF
                if key == ord('n'):  # Próxima imagem
                    break
                elif key == ord('q'):  # Sair
                    cv2.destroyAllWindows()
                    print(f"Processamento concluído! Imagens salvas em: {pasta_saida}")
                    return
            cv2.destroyWindow('Imagem Normalizada (128x128, Escala de Cinza)')
        else:
            print(f"Imagem processada e salva: {caminho_saida}")

    if visualizar == 'n':
        print(f"Processamento concluído! Imagens salvas em: {pasta_saida}")
    else:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    ### ALTERAÇÃO ###: Configura o parser de argumentos sem índice inicial
    parser = argparse.ArgumentParser(description="Normaliza imagens para 128x128 em escala de cinza.")
    parser.add_argument('--pasta_entrada', type=str, required=True, 
                        help="Caminho da pasta com as imagens originais (inclui subpastas)")
    parser.add_argument('--pasta_saida', type=str, required=True, 
                        help="Caminho da pasta para salvar as imagens normalizadas")
    args = parser.parse_args()

    ### ALTERAÇÃO ###: Chama a função sem índice inicial
    normalizar_imagens(args.pasta_entrada, args.pasta_saida)