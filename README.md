# final-industrial

## Requisitos

1. Monitoramento em tempo real das grandezas do processo (20
pontos):

   - [X] (8 pontos) Comunicação MODBUS com o CLP da planta
   - [X] (5 pontos) Tensão da rede, corrente RMS, potência de entrada, velocidade
     da esteira, rotação do motor, frequência do inversor, temperatura do estator
   - [X] (7 pontos) Gráficos: Cores (RGB) e Peso do objeto.
<!--  -->
1. Capacidade de atuação no sistema (12 pontos):

   - [X] (2 pontos) Ligar/desligar o processo
   - [X] (1 pontos) Ligar/desligar o atuador da esteira principal (inserção de novos objetos)
   - [X] (1 pontos) Mudança na frequência de operação do motor
   - [X] (8 pontos) Mudança nos filtros do Classificador
<!--  -->
3. Interface gráfica que represente de forma fidedigna o processo (28 pontos):

   - [X] (8 pontos) Imagem representativa da planta
   - [X] (7 pontos) Pelo menos uma animação no supervisório (deslocamento do objeto
     na esteira, classificação, etc)
   - [X] (2 pontos) Menu de configurações
   - [X] (2 pontos) Mecanismos para atuação no processo (ver item 2)
   - [X] (2 pontos) Separação de telas (monitoramento em tempo real e busca de dados históricos)
   - [X] (7 pontos) Deverá utilizar o framework kivyMD
<!--  -->
4. (7 pontos) Módulo de busca de dados históricos (15 pontos):

   - [X] (6 pontos) Armazenamento das principais informações do processo
   - [X] (6 pontos) Permitir a busca de dados históricos das informações do processo
   - [X] (3 pontos) Deverá ser implementado utilizando a técnica ORM com o SQLAlchemy
