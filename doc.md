# Projeto Laboratório de Sistemas de Controle II
##Introdução
Este projeto tem como objetivo implementar um controlador PID para um sistema de controle de posição de uma bola em um balanço.Atualmente, existem diversos projetos de referência e pesquisas de estado da arte relacionados ao controle de posição de uma bola em um balanço utilizando controladores PID e técnicas avançadas de controle. Um exemplo clássico é o sistema "Ball and Beam", amplamente utilizado em laboratórios de automação e controle para demonstração de técnicas de controle PID, controle robusto e controle adaptativo. Além disso, há trabalhos acadêmicos que exploram o uso de controladores baseados em inteligência artificial, como redes neurais e lógica fuzzy, para melhorar o desempenho do sistema.

Projetos similares podem ser encontrados em plataformas como Arduino e Raspberry Pi, onde a implementação do controle é feita com sensores ultrassônicos e motores servo, permitindo a replicação do experimento em ambientes educacionais. Pesquisas recentes também abordam o uso de técnicas de identificação de sistemas e controle preditivo para aprimorar a resposta dinâmica e a precisão do posicionamento da bola.

Esses projetos servem como base para o desenvolvimento de soluções mais avançadas e podem ser consultados em artigos científicos, repositórios de código aberto e teses de pós-graduação na área de engenharia de controle.

## Objetivo
Implementar um controlador PID para um sistema de controle de posição de uma bola em um balanço.

## Descrição do Sistema
O sistema consiste em uma bola que pode ser movida horizontalmente por meio de um motor. O objetivo é controlar a posição da bola usando um controlador PID.

## Diagrama de Blocos (fazer em tikZ)

Entrada (cm)                          Saída
------------>(+ -)-->|PID|--> |Servo| ------>
               /\                        |
                |                        |
                +----|Sensor Ultra|<-----+
## Interface de Controle e Configuração do Sistema
Usamos Python tanto para a configuração de uma Interface de Controle e Configuração do Sistema quanto para a implementação do controlador PID. Usamos as bibliotecas Streamlit para a Interface e Telemetrix para a comunicação com o hardware. A comunicação entre os dispositivos é realizada através de um protocolo de comunicação serial, permitindo a troca de dados em tempo real entre o controlador e o hardware. Enquanto que a comunicação entre os programas é realizada via API REST.

## Modelagem
Este processo envolve a análise do sistema físico, a seleção de parâmetros de controle e a implementação do algoritmo PID. A modelagem é realizada usando técnicas de análise de sistemas dinâmicos, como equações diferenciais e transferências de Laplace. No entanto devido a instabilidade natural do sistema e o alto ruído presente no sinal de feedback, devido ao sensor ultrassonico, foi impossibilitado a aquisição de dados para a modelagem.

## Implementação do Controlador PID
A implementação do controlador PID é realizada usando Python. O controlador é configurado com os parâmetros de ganho proporcional, integral e derivativo. O controlador é então usado para controlar a posição da bola em um balanço. Os parametrôs foram ajustados de forma empirica devido ao ruído presente no sinal de feedback.

## Melhorias futuras
Poderiamos usar um melhor sensor de distância no projeto, como um sensor de laser ou um sensor de câmera, para melhorar a precisão e a estabilidade do sistema. Além disso, poderíamos implementar uma estratégia de controle mais avançada, como um controlador de posição PID com feedback de posição e velocidade, para melhorar ainda mais a estabilidade e a precisão do sistema.

## Resultados
Após a implementação do controlador PID, o sistema foi testado em diferentes condições de operação. Os resultados mostraram que o sistema não teve a capacidade de controlar a posição da bola com precisão e estabilidade. Isso foi devido ao ruído presente no sinal de feedback, mas foi possível observar que o sistema foi capaz de manter a posição da bola em torno do ponto de equilíbrio.

## Conclusão
Este projeto demonstrou que é possível controlar a posição de uma bola em um balanço usando um controlador PID. No entanto, devido ao ruído presente no sinal de feedback, o sistema não foi capaz de controlar a posição da bola com precisão e estabilidade. Para melhorar o desempenho do sistema, é necessário usar um melhor sensor de distância e posteriormente implementar uma estratégia de controle mais avançada.

## Referências
[1] Control Systems Engineering, Nise, 2010.
