**Integrantes**: César Henrique, Lucas Ekroth, Paulo Rangel
# Projeto Ball-Beam com controle PID
## Objetivo
O objetivo deste projeto é desenvolver um sistema de controle PID para estabilizar uma bola em uma viga, utilizando um motor de servo para ajustar a posição da viga. O sistema deve ser capaz de manter a bola em uma posição desejada, mesmo com perturbações externas.
![[Pasted image 20250617190904.png]]
## Materiais
- 1 Arduino Uno
- 1 Motor de servo
- 1 Sensor de Distância (ultrassônico ou infravermelho)
- 1 Bola pequena (de preferência leve)
- 2 Viga (pode ser de madeira ou plástico)
## Software de Controle
- Arduino IDE
- Python, com comunicação via firmata (ou telemetrix)
- Streamlit para desenvolver o IHM

## Passos de Desenvolvimento
1. Desenvolver o prototipo para adquirir os dados
2. Identificar o Sistema do Ball-Beam
3. Simular o sistema afim de testar alguns parametros de PID
4. Implementar
5. Ajuste fino

## Referências
- [Documentação Streamlit](https://docs.streamlit.io/)
- [Documentação Firmata](https://docs.arduino.cc/libraries/firmata/)
- [Documentação Telemetrix](https://mryslab.github.io/telemetrix/)
- [Documentação pyFirmata](https://pyfirmata.readthedocs.io/en/latest/)
- [Projeto de Referência](https://github.com/LaVolpe12/PID-Demonstrator-BallnBeam)
- [Wolfram Ball And Beam Control Document](https://reference.wolfram.com/language/MicrocontrollerKit/workflow/BallAndBeamControl)
- Saad, M., & Khalallah, M. (2017). Design and implementation of an embedded ball-beam controller using PID algorithm. *Universal Journal of Control and Automation*, 5(4), 63-70.
