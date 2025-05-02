# Speed tests on several materials

./tests.sh

## Input files

* input/texte1_ij.jpg: ArianeGroup pseudo letter
* input/texte2_ij.jpg: Le Canard article papers with 2 columns
* input/texte3_ij.jpg: Le Monde article
* input/texte4_ij.jpg: article readforme with 2 columns
* input/texte5_ij.jpg: article 'Harald Bénoliel' with multi-columns
* input/texte6_ij.jpg: sum-up of Exofinger protocol
* input/texte7_ij.jpg: readforme introduction with 2 columns

with i:

* 0 : from a scanner, resolution: 2550x3508, couleurs
* 1 : from a rasberry Pi cam v 1.0, resolution: 1944x2592, n&b
* 2 : from a rasberry Pi cam v 2.1, resolution: 2550x3508, n&b ou couleurs

with j:

* 0 : portrait
* 1 : landscape

## Results

Execution time

| Filename  | PC (sec)| Raspi4 (sec) | Raspi3 (sec) |
|:---------:|:-------:|:------------:|:------------:|
|texte1_00.jpg| - | 5.36 | - |
|texte1_20.jpg| 1.06 | 5.8 | 10.69 |
|texte2_00.jpg| 2.76 | 13.62 |  26.43 |
|texte3_00.jpg| 1.86 | 10.09 | 20.53 |
|texte3_10.jpg| 2.26 | 12.18 | - |
|texte3_20.jpg| 2.51 | 13.17 | 25.10  |
|texte4_00.jpg| 2.67 | 13.79 | 26.54 |
|texte4_20.jpg| 2.46 | 12.38 | 23.42 |
|texte5_00.jpg| 3.72 | 17.95 | 35.07 |
|texte5_20.jpg| 3.31| 16.53 | 32.49 |
|texte6_00.jpg| 3.19 | 15.94 | 30.65 |
|texte6_20.jpg| - | - | - |
|texte7_00.jpg| 1.01 | 5.16 | 9.75 |
