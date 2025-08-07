import os
import cv2
import numpy as np
import re
import argparse

# Variáveis globais para interação com o mouse
drawing = False
ix, iy = -1, -1
fx, fy = -1, -1
roi_confirmada = None
img_display = None
scale_factor = 1.0

def redimensionar_imagem(img, janela_largura=800, janela_altura=600):
    """
    Redimensiona a imagem para caber em uma janela de tamanho fixo, mantendo a proporção.
    
    Args:
        img: Imagem OpenCV.
        janela_largura, janela_altura: Dimensões fixas da janela (ex.: 800x600).
    
    Returns:
        Imagem redimensionada, fator de escala.
    """
    h, w = img.shape[:2]
    scale = min(janela_largura / w, janela_altura / h, 1.0)
    if scale == 1.0:
        return img, 1.0
    new_w, new_h = int(w * scale), int(h * scale)
    img_resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return img_resized, scale

def mouse_callback(event, x, y, flags, param):
    """Callback para desenhar uma caixa QUADRADA com o mouse."""
    global drawing, ix, iy, fx, fy, roi_confirmada, img_display, scale_factor
    img_display = param['image'].copy()

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        fx, fy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            fx, fy = x, y
            lado = max(abs(x - ix), abs(y - iy))
            if x >= ix:
                fx = ix + lado
            else:
                fx = ix - lado
            if y >= iy:
                fy = iy + lado
            else:
                fy = iy - lado
            cv2.rectangle(img_display, (ix, iy), (fx, fy), (0, 0, 255), 2)
            cv2.imshow('Imagem', img_display)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        lado = max(abs(x - ix), abs(y - iy))
        if x >= ix:
            fx = ix + lado
        else:
            fx = ix - lado
        if y >= iy:
            fy = iy + lado
        else:
            fy = iy - lado
        roi_confirmada = (
            int(min(ix, fx) / scale_factor),
            int(min(iy, fy) / scale_factor),
            int(max(ix, fx) / scale_factor),
            int(max(iy, fy) / scale_factor)
        )
        cv2.rectangle(img_display, (ix, iy), (fx, fy), (0, 0, 255), 2)
        cv2.imshow('Imagem', img_display)

def selecionar_extrair_roi(pasta_imagens, pasta_saida):
    """
    Permite selecionar ROIs QUADRADAS com o mouse e extrai as regiões recortadas,
    com opções de voltar e salvar progresso.
    
    Args:
        pasta_imagens (str): Pasta com as imagens originais.
        pasta_saida (str): Pasta para salvar as ROIs recortadas.
    """
    global drawing, ix, iy, fx, fy, roi_confirmada, img_display, scale_factor

    # Cria a pasta de saída
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Lista as imagens e armazena as coordenadas temporariamente
    coordenadas_temp = {}
    extensoes_validas = ('.jpg', '.jpeg', '.png')
    imagens_originais = [f for f in os.listdir(pasta_imagens) if f.lower().endswith(extensoes_validas)]
    if not imagens_originais:
        print("Nenhuma imagem encontrada na pasta!")
        return
    
    # Ordena imagens pelo número extraído do nome
    def extrair_indice(nome_arquivo):
        match = re.search(r'\d+', nome_arquivo)
        return int(match.group()) if match else float('inf')
    imagens_originais.sort(key=extrair_indice)

    print("\nImagens disponíveis na pasta:")
    for i, arquivo in enumerate(imagens_originais, start=1):
        print(f"{i}: {arquivo}")
    
    while True:
        try:
            indice_inicial = int(input("\nDigite o número da imagem para começar (1 a {}): ".format(len(imagens_originais))))
            if 1 <= indice_inicial <= len(imagens_originais):
                break
            print("Índice inválido! Escolha um número entre 1 e {}.".format(len(imagens_originais)))
        except ValueError:
            print("Entrada inválida! Digite um número inteiro.")

    i = indice_inicial - 1
    
    while i < len(imagens_originais):
        arquivo = imagens_originais[i]
        caminho_imagem = os.path.join(pasta_imagens, arquivo)
        img = cv2.imread(caminho_imagem)
        if img is None:
            print(f"Erro ao carregar {arquivo}")
            i += 1
            continue

        cv2.namedWindow('Imagem')
        img_display, scale_factor = redimensionar_imagem(img, janela_largura=800, janela_altura=600)
        drawing = False
        ix, iy, fx, fy = -1, -1, -1, -1
        roi_confirmada = None

        cv2.setMouseCallback('Imagem', mouse_callback, {'image': img_display})

        print(f"\nProcessando: {arquivo} ({i + 1}/{len(imagens_originais)})")
        print("Instruções: 'c' para confirmar, 'r' para reiniciar, 'q' para pular, 'b' para voltar, 's' para salvar progresso e sair.")

        while True:
            cv2.imshow('Imagem', img_display)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('c') and roi_confirmada:
                x_min, y_min, x_max, y_max = roi_confirmada
                x_min, y_min = max(0, x_min), max(0, y_min)
                x_max, y_max = min(img.shape[1], x_max), min(img.shape[0], y_max)
                coordenadas_temp[arquivo] = [x_min, y_min, x_max, y_max]
                print(f"ROI confirmada para {arquivo}.")
                break

            elif key == ord('r'):
                img_display, _ = redimensionar_imagem(img, janela_largura=800, janela_altura=600)
                drawing = False
                ix, iy, fx, fy = -1, -1, -1, -1
                roi_confirmada = None
                cv2.imshow('Imagem', img_display)

            elif key == ord('q'):
                print(f"Imagem {arquivo} pulada.")
                if arquivo in coordenadas_temp:
                    del coordenadas_temp[arquivo]
                break
            
            elif key == ord('b'):
                if i > 0:
                    print("Voltando para a imagem anterior.")
                    i -= 1
                    cv2.destroyWindow('Imagem')
                    # Remove a anotação da imagem anterior se ela existir
                    if imagens_originais[i] in coordenadas_temp:
                        del coordenadas_temp[imagens_originais[i]]
                    break
                else:
                    print("Você já está na primeira imagem.")
            
            elif key == ord('s'):
                print("Salvando progresso e saindo...")
                cv2.destroyAllWindows()
                
                # Extrai e salva as ROIs confirmadas até o momento
                for arq_salvar, coords in coordenadas_temp.items():
                    caminho_img_original = os.path.join(pasta_imagens, arq_salvar)
                    img_original = cv2.imread(caminho_img_original)
                    if img_original is None:
                        print(f"Erro ao carregar {arq_salvar} para extração")
                        continue
                    
                    x_min, y_min, x_max, y_max = coords
                    roi = img_original[y_min:y_max, x_min:x_max]
                    nome_base = os.path.splitext(arq_salvar)[0]
                    caminho_roi = os.path.join(pasta_saida, f"{nome_base}_roi.jpg")
                    cv2.imwrite(caminho_roi, roi)
                    print(f"ROI salva: {caminho_roi}")
                return
        
        # Aumenta o índice apenas se a tecla 'b' não foi pressionada
        if key != ord('b'):
            i += 1

    cv2.destroyAllWindows()
    print("Todas as imagens foram processadas.")
    
    # Extrai e salva as ROIs confirmadas no final do processo
    for arquivo_final, coords in coordenadas_temp.items():
        caminho_imagem_final = os.path.join(pasta_imagens, arquivo_final)
        img_final = cv2.imread(caminho_imagem_final)
        if img_final is None:
            print(f"Erro ao carregar {arquivo_final} para extração")
            continue
        
        x_min, y_min, x_max, y_max = coords
        roi = img_final[y_min:y_max, x_min:x_max]
        nome_base = os.path.splitext(arquivo_final)[0]
        caminho_roi = os.path.join(pasta_saida, f"{nome_base}_roi.jpg")
        cv2.imwrite(caminho_roi, roi)
        print(f"ROI salva: {caminho_roi}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seleciona e extrai ROIs quadradas de imagens.")
    parser.add_argument('--pasta_entrada', type=str, required=True,
                        help="Caminho da pasta com as imagens originais.")
    parser.add_argument('--pasta_saida', type=str, required=True,
                        help="Caminho da pasta para salvar as ROIs recortadas.")
    args = parser.parse_args()

    selecionar_extrair_roi(args.pasta_entrada, args.pasta_saida)