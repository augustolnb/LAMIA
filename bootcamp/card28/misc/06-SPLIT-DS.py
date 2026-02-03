import os
import random
import argparse

def select_random_images(pasta_origem, pasta_destino, num_imagens=300):
    """
    Seleciona aleatoriamente imagens de uma pasta, move-as para outra pasta,
    renomeia com formato 'teste_XXX.ext' e remove da origem.

    Args:
        pasta_origem (str): Pasta com as imagens originais.
        pasta_destino (str): Pasta para mover as imagens selecionadas.
        num_imagens (int): Número de imagens a selecionar (padrão: 300).
    """
    # Cria a pasta de destino, se não existir
    os.makedirs(pasta_destino, exist_ok=True)

    # Lista as imagens válidas
    extensoes_validas = ('.jpg', '.jpeg', '.png')
    imagens = [f for f in os.listdir(pasta_origem) if f.lower().endswith(extensoes_validas)]
    
    if not imagens:
        print(f"Nenhuma imagem encontrada em {pasta_origem}!")
        return
    
    if len(imagens) < num_imagens:
        print(f"Aviso: Apenas {len(imagens)} imagens disponíveis, menos que {num_imagens} solicitadas.")
        num_imagens = len(imagens)

    # Seleciona aleatoriamente
    imagens_selecionadas = random.sample(imagens, num_imagens)
    
    # Move e renomeia as imagens
    for i, imagem in enumerate(imagens_selecionadas, start=1):
        caminho_origem = os.path.join(pasta_origem, imagem)
        extensao = os.path.splitext(imagem)[1].lower()  # Mantém a extensão original
        novo_nome = f"teste_{i:03d}{extensao}"
        caminho_destino = os.path.join(pasta_destino, novo_nome)

        try:
            os.rename(caminho_origem, caminho_destino)
            print(f"Movido e renomeado: {imagem} -> {novo_nome}")
        except Exception as e:
            print(f"Erro ao mover {imagem}: {e}")

    print(f"\nConcluído! {len(imagens_selecionadas)} imagens movidas para {pasta_destino}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seleciona e move imagens aleatoriamente.")
    parser.add_argument('--pasta_origem', type=str, required=True,
                        help="Caminho da pasta com as imagens originais")
    parser.add_argument('--pasta_destino', type=str, required=True,
                        help="Caminho da pasta para mover as imagens selecionadas")
    parser.add_argument('--num_imagens', type=int, default=300,
                        help="Número de imagens a selecionar (padrão: 300)")
    args = parser.parse_args()

    select_random_images(args.pasta_origem, args.pasta_destino, args.num_imagens)