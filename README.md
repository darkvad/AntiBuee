Système de régulation d'un anneau chauffant Celestron (type C8) à base d'un arduino nano (V3)
=============================================================================================

Ce projet est libre d'utilisation pour un usage privé mais aucune utilisation dans un but commercial n'est permise.
-------------------------------------------------------------------------------------------------------------------

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
ATTENTION : Le PCB utilise un buck converter Pin inverted ce qui n'est pas forcément le cas de celui que vous aurez et qui n'était pas le cas du mien. Du coup la sérigraphie du PCB est à inverser (Out est en fait In et In est Out). J'ai réglé ce soucis avec mon buck converter en soudant les pins dessous, ce qui m'a permis de le monter comme sur l'emplacement sérigraphié pour ne pas qu'il dépasse du PCB. Vérifiez vos tension avant de souder ou mettre les composants.

![PCB_PCB_ArduDewRing_2025-01-04](https://github.com/user-attachments/assets/d0534c7c-d148-40f8-9264-90c69c90cd5c)

Les fichiers Gerber :

[Gerber_ArduDewRing_PCB_ArduDewRing_2025-01-04.zip](https://github.com/user-attachments/files/18311245/Gerber_ArduDewRing_PCB_ArduDewRing_2025-01-04.zip)

La liste des composants :

1 Arduino nano V3 par exemple https://fr.aliexpress.com/item/1005007539665675.html?spm=a2g0o.order_list.order_list_main.159.6caf5e5bU7I341&gatewayAdapt=glo2fra)
1 Buck Converter 5V ici : https://fr.aliexpress.com/item/33017156248.html?spm=a2g0o.order_list.order_list_main.114.6caf5e5bU7I341&gatewayAdapt=glo2fra
1 résistance 10 K ohms
1 ecran OLED SSD1306 en blanc au cas où vous vouliez mettre un film rouge dessus : https://fr.aliexpress.com/item/1005006373062872.html?spm=a2g0o.order_list.order_list_main.139.6caf5e5bU7I341&gatewayAdapt=glo2fra
Option Film rouge : https://fr.aliexpress.com/item/1005005637966631.html?spm=a2g0o.order_list.order_list_main.109.6caf5e5bU7I341&gatewayAdapt=glo2fra
1 Driver Mosfet 15A : https://www.amazon.fr/dp/B0BWY5B2P9?ref=ppx_yo2ov_dt_b_fed_asin_title
1 capteur de temp/hum BME 280 : https://www.amazon.fr/temp%C3%A9rature-dhumidit%C3%A9-num%C3%A9rique-pr%C3%A9cision-Interface/dp/B0DP8S6YV2/ref=sr_1_9?crid=2XVLH1F5V96W6&dib=eyJ2IjoiMSJ9.nrYpDqucI_kP7N6thFzRynl7uhsUO-UfSALdW2Zp-TIBNkmdXXHew0y9_Rr99fFFoY5-4xbWyXMddWt3CgsTNRb-WjdGGC2yzgnVFgKXM63qW2oNHVOrXX4FsuBuJNKO0zEDqDEzrPjuxsJ90zeQQKiph3Ur7jTlcXV04zo0BWkgsX8HQNZIBAt2pPME8zUCNk-5yOC_RyhFxQEpk08w_1txe8Ogu820OG8rPfiMuP_amuQuNWXGZ2R_K405AML7-b03GoS3Awn5EiQMN2psgJ4_dGMspOe3doRaSHjNa6d4AOlI7IMTi9yJNO1Npu3pDTu4qdV7FFyZkWaLrqqMB9ox5dEsOcDeA9jT_cMpjnVwphAzVYkZZIzzbZC5A5T3JFMF5tmiq89_UJqlTIM37oaiZLRAmRmqAkQss7FSEuUt4YE3C2uqCYA77NzOPybr.yccOjqGoMhdAawBIOFQ5v2NRr8-Lz1qKntZ8ac3A1Fk&dib_tag=se&keywords=bme280&qid=1738268687&sprefix=BME%2Caps%2C120&sr=8-9
1 Connecteur alim 12v par exemple https://fr.aliexpress.com/item/1005007404274787.html?spm=a2g0o.order_list.order_list_main.23.6caf5e5bU7I341&gatewayAdapt=glo2fra
1 Connecteur jack 3,5 (ou 2.5 si vous avez la rallonge male male 2.5 - 2.5) par exemple https://www.amazon.fr/dp/B01MTNOEOT?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1
1 Connecteur RCA comme ceux ci : https://www.amazon.fr/dp/B09TPL4TV5?ref=ppx_yo2ov_dt_b_fed_asin_title

PS : Les liens correspondent à ce que j'avais en stock de commandes passées ou ce que j'ai commandé pour l'occasion. Ils sont à titre indicatif , achetez où bon vous semble ;)

Et une photo du prototype ... A ce jour, j'attend les PCB, le projet est tout neuf mais testé sur platine d'essai.

![1736101971722](https://github.com/user-attachments/assets/10be5ab0-a420-4b10-8341-86ba13789231)

Voila les photos du montage :

![montage1](https://github.com/user-attachments/assets/65ccac36-21ac-4f2b-8d2d-97b409ef0054)
![montage2](https://github.com/user-attachments/assets/e56ccad6-faf8-4cc1-98dd-1c81d97fa710)
![montage3](https://github.com/user-attachments/assets/ed833d0d-bb2a-4e40-b7d2-0d191381f2a8)
![montage4](https://github.com/user-attachments/assets/e0123c9d-20ff-44b8-a1e8-697bf34ef38b)
![montage5](https://github.com/user-attachments/assets/5bc768f6-1e6d-497b-b6f7-0f034e12dcf3)
![montage6](https://github.com/user-attachments/assets/748572ba-3b81-4121-828b-c39694fa0288)
![montage7](https://github.com/user-attachments/assets/8cb4f7e1-f0de-4078-85a1-818ded59084a)


Ce projet est libre d'utilisation pour un usage privé mais aucune utilisation dans un but commercial n'est permise.





