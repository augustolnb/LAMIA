# Classificador de Embalagens de Fio Dental (Cheia ou Vazia)

## 📖 Descrição do Projeto

Este projeto apresenta uma solução de Visão Computacional proposta como trabalho final do **bootcamp de machine learning**.

O modelo implementado realiza a classificação binária de embalagens de fio dental, determinando se elas estão **cheias** ou **vazias**. 

Uma aplicação plausível seria automatizar o processo de verificação de integridade do produto em uma linha de produção ou estoque, utilizando uma Rede Neural Convolucional (CNN) treinada para a tarefa.

O sistema foi desenvolvido em Python, utilizando a biblioteca TensorFlow/Keras para a construção e treinamento do modelo, no ambiente online do Google Colab.

`[Placeholder para imagem: GIF ou imagem demonstrando o sistema em ação, classificando uma imagem de embalagem cheia e outra vazia.]`

## 🛠️ Funcionalidades

-   **Classificação Binária:** Distingue as embalagens entre cheias e vazias.
-   **Dataset Robusto:** Utiliza um dataset com mais de 4000 imagens capturadas manualmente em condições variadas.
-   **Pré-processamento Automatizado:** Inclui scripts para processar as imagens originais e prepará-las para o treinamento.
-   
## 📊 O Dataset

A base de dados do projeto é um dataset criado especificamente para este problema.

-   **Total de Imagens:** 4066
-   **Classes:** `Cheia` e `Vazia`
-   **Origem:** Fotos tiradas manualmente com um smartphone, garantindo uma variedade de ângulos, iluminações e posicionamentos.

### Etapas de Pré-processamento

Para garantir que o modelo recebesse dados adequados, as imagens originais passaram por um *pipeline* de pré-processamento dividido em três etapas principais, utilizando os scripts localizados na pasta `misc/`.

**1. Organização do Dataset (`misc/01-DS-new.py`)**

Este script foi o ponto de partida para a estruturação dos dados. Ele foi responsável por organizar as imagens originais, separando-as em suas respectivas pastas de classe (`cheia`/`vazia`) 

**2. Seleção da Região de Interesse (ROI) (`misc/02-selecionar_ROI.py`)**

As fotos originais continham muito ruído de fundo. Para que o modelo focasse exclusivamente na embalagem, este script foi utilizado para cortar a Região de Interesse (ROI) de cada imagem.

`[Placeholder para imagem: Exemplo de imagem original vs. imagem com ROI selecionado lado a lado.]`

**3. Normalização e Redimensionamento (`misc/03-NORMALIZE.py`)**

A etapa final de preparação. Este script processa as imagens cortadas para:
-   **Redimensionar:** Todas as imagens foram padronizadas para as dimensões exigidas pela entrada do modelo (128x128 pixels).
-   **Conversão da Escala de Cores:** As imagens foram todas convertidas para escala de cinza com o objetivo de otimizar e acelerar o processo de treinamento da rede neural.

`[Placeholder para imagem: Exemplo de imagem antes e depois da normalização, mostrando a mudança de tamanho e talvez um filtro de cor, se aplicado.]`

## 🧠 O Modelo de IA

O coração deste projeto é uma **Rede Neural Convolucional (CNN)**, uma arquitetura ideal para tarefas de classificação de imagens.

### Arquitetura

O modelo foi construído em Keras e possui a seguinte estrutura:

```python
# Código do modelo final extraído do notebook card28.ipynb
import tensorflow as tf

model = tf.keras.models.Sequential([
    tf.keras.layers.Input(shape=(128, 128, 1)),

    tf.keras.layers.Conv2D(32, 3, activation='relu'),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Conv2D(64, 3, activation='relu'),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Conv2D(128, 3, activation='relu'),
    tf.keras.layers.MaxPooling2D(),

    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    
    # Camada de Dropout para regularização
    tf.keras.layers.Dropout(dropout_rate),
    
    # Camada de saída com 2 neurônios (um para cada classe)
    tf.keras.layers.Dense(num_classes) 
])

optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
model.compile(optimizer=optimizer,
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

```

### Performance

Após o treinamento com os hiperparâmetros inicialmente propostos foram feitos testes utilizando a técnica de *Grid Search* para otimizar esses hiperprâmetros.
Por fim, os valores utilizados no modelo final foram:

- **Taxa de Aprendizagem (Learning Rate):** 1e-3
- **Taxa de Dropout:** 0.4
- **Épocas de Treinamento:** 13
- **Tamanho do Lote (Batch Size):** 32

A matriz de confusão abaixo ilustra o desempenho detalhado do modelo:

`[Placeholder para a imagem da Matriz de Confusão gerada pelo notebook.]`

## 🚀 Como Usar

### Pré-requisitos

-   Python 3.8+
-   pip (Python Package Installer)
-   Git

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```

2.  **Crie e ative um ambiente virtual (Recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

### Executando uma Previsão

Para classificar uma nova imagem, você pode usar o modelo treinado com um script como este:

```python
import tensorflow as tf
import numpy as np
import cv2

# Carregar o modelo treinado
# model = tf.keras.models.load_model('caminho/para/seu/modelo.h5')

# Função de predição adaptada do notebook
def prever_nova_imagem(caminho_imagem, model):
    img = cv2.imread(caminho_imagem, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Erro: Não foi possível carregar a imagem em {caminho_imagem}")
        return None, None

    img_resized = cv2.resize(img, (128, 128), interpolation=cv2.INTER_AREA)
    img_normalized = img_resized.astype("float32") / 255.0
    img_tensor = np.expand_dims(img_normalized, axis=-1)
    img_tensor = np.expand_dims(img_tensor, axis=0)

    predictions = model.predict(img_tensor)
    probabilities = tf.nn.softmax(predictions).numpy()[0]
    predicted_class_index = np.argmax(predictions, axis=1)
    
    class_names = ['empty', 'full']
    predicted_class = class_names[predicted_class_index[0]]
    
    return predicted_class, probabilities

# Exemplo de uso
# caminho_da_nova_imagem = 'caminho/para/sua/imagem.jpg'
# classe_predita, probabilidades = prever_nova_imagem(caminho_da_nova_imagem, model)

# if classe_predita:
#     print(f"A imagem é provavelmente: {classe_predita}")
#     print(f"Probabilidade de ser 'empty': {probabilidades[0]:.2f}")
#     print(f"Probabilidade de ser 'full': {probabilidades[1]:.2f}")

```

## 📁 Estrutura do Projeto

```
.
├── misc/                # Scripts de suporte para criação e pré-processamento do dataset.
│   ├── 01-DS-new.py
│   ├── 02-selecionar_ROI.py
│   └── 03-NORMALIZE.py
├── card28.ipynb         # Código com o modelo 
├── requirements.txt
└── README.md
└── dataset_dental_floss.zip
```

## ✒️ Autor

**Augusto** - `[Seu Sobrenome]`

-   **LinkedIn:** `[URL do seu LinkedIn]`
-   **GitHub:** `[URL do seu GitHub]`

