Système de régulation d'un anneau chauffant Celestron (type C8) à base d'un arduino nano (V3)
=============================================================================================

Ce projet à pour but d'assurer la régulation en température des anneaux chauffants Celestron en urilisant leur sonde de température intégrée.
La sonde de température est une thermistance NTC10K et au vu des temépratures de fonctionnement visées (plutot en hiver), les formules de type steinhart simplifiées ne sont pas adaptées var souvent fournies pour une plage de température entre 25°C et 85°C
On utilisera donc la formule de steinhart-hart valable sur toute plage de température et nécessitant les 3 coefficents A , B et C.
![image](https://github.com/user-attachments/assets/fdafac64-3cde-4b5e-a884-0318a2c7d04a) https://fr.wikipedia.org/wiki/Relation_de_Steinhart-Hart
Cette page wikipédia fournit un code python permettant à partir de 3 mesures de référence de déterminer vos coefficients.
Pour mon anneau :
#define COEFA -0.0005832612868399646

#define COEFB 0.0004757002048313418

#define COEFC -5.705419094644155e-07


A vérifier avec votre matériel.

La régulation est faite avec un aservissement PID fournissant une sortie PMW afin d'attaquer un module MOSFET pour faire varier la puissance de chauffe de la résistance de l'anneau.
Les paramètres de l'asservissement PID sont à renseigner dans celle lige de code :
double Kp=80, Ki=2, Kd=5;

Le montage doit être alimenté en 12V (pour l'anneau chauffant) et du coup, un "buck converter" est utilisé pour l'alimentation 5V de l'arduino nano, evitant de devoir brancher l'usb en dehors de la programmation / debug.

Voici le schema :
![Schematic_ArduDewRing_2025-01-04](https://github.com/user-attachments/assets/86b4d2e3-259c-4b84-9b6a-969513d49328)

Le PCB :
![PCB_PCB_ArduDewRing_2025-01-04](https://github.com/user-attachments/assets/d0534c7c-d148-40f8-9264-90c69c90cd5c)

Les fichiers Gerber :
[Gerber_ArduDewRing_PCB_ArduDewRing_2025-01-04.zip](https://github.com/user-attachments/files/18311245/Gerber_ArduDewRing_PCB_ArduDewRing_2025-01-04.zip)

Et une photo du prototype ... A ce jour, j'attend les PCB, le projet est tout neuf mais testé sur platine d'essai.
![1736101971722](https://github.com/user-attachments/assets/10be5ab0-a420-4b10-8341-86ba13789231)

Ce projet est libre d'utilisation pour un usage privé mais aucune utilisation dans un but commercial n'est permise.





