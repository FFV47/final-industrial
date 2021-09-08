# final-industrial

## Requisitos

1. Monitoramento em tempo real das grandezas do processo (20
pontos):

   - [ ] (8 pontos) Comunicação MODBUS com o CLP da planta
   - [ ] (5 pontos) Tensão da rede, corrente RMS, potência de entrada, velocidade
     da esteira, rotação do motor, frequência do inversor, temperatura do estator
   - [ ] (8 pontos) Comunicação MODBUS com o CLP da planta
<!--  -->
1. Capacidade de atuação no sistema (12 pontos):

   - [ ] (2 pontos) Ligar/desligar o processo
   - [ ] (1 pontos) Ligar/desligar o atuador da esteira principal (inserção de novos objetos)
   - [ ] (1 pontos) Mudança na frequência de operação do motor
   - [ ] (8 pontos) Mudança nos filtros do Classificador
<!--  -->
3. Interface gráfica que represente de forma fidedigna o processo (28 pontos):

   - [ ] (8 pontos) Imagem representativa da planta
   - [ ] (7 pontos) Pelo menos uma animação no supervisório (deslocamento do objeto
     na esteira, classificação, etc)
   - [ ] (2 pontos) Menu de configurações
   - [ ] (2 pontos) Mecanismos para atuação no processo (ver item 2)
   - [ ] (2 pontos) Separação de telas (monitoramento em tempo real e busca de dados históricos)
   - [ ] (7 pontos) Deverá utilizar o framework kivyMD
<!--  -->
4. (7 pontos) Módulo de busca de dados históricos (15 pontos):

   - [ ] (6 pontos) Armazenamento das principais informações do processo
   - [ ] (6 pontos) Permitir a busca de dados históricos das informações do processo
   - [ ] (3 pontos) Deverá ser implementado utilizando a técnica ORM com o SQLAlchemy