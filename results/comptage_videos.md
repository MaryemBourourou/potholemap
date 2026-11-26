# Comptage sur vidéos et essais de filtres

Ce document présente l'évaluation du pipeline de détection et de suivi de **PotholeMap** sur vidéo routière, en comparant le comptage manuel de référence, les détections image par image (sans suivi) et les défauts uniques retenus après suivi et filtrage.

---

## 1. Comparaison des comptages (Main vs Sans suivi vs Avec suivi)

| Vidéo / Séquence | Durée (s) | Comptage manuel (réf.) | Détections sans suivi (image par image) | Pistes brutes (avec suivi) | Défauts uniques retenus (après filtrage) | Écart avec la réf. |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Séquence test Space HF** | `57.4` | `Non relevé` | `13` *(potholes)* | `14` | **8** *(0 pothole, 8 pothole_repair)* | `...` |


### Analyse des écarts
* **Détections sans suivi vs Pistes brutes :** sur la séquence de `57.4 s`, **13** détections de nids-de-poule ont été relevées image par image sans suivi, tandis que le suivi multi-images a produit **14** pistes brutes au total (incluant les détections de zones réparées).
* **Pistes brutes vs Défauts uniques :** sur **14** pistes brutes, **8** ont été gardées après filtrage (soit **6** écartées), aboutissant à **0** nid-de-poule unique et **8** zones réparées uniques (`pothole_repair`).
* **Rappel sur la gravité :** la gravité affichée est un indicateur relatif, et non une mesure physique en centimètres.

---

## 2. Essais de paramètres de filtrage

Pour limiter à la fois les faux positifs (bruit sur la chaussée, ombres) et les doublons (*ID switches*), les réglages suivants ont été évalués :

| Essai | `conf` (seuil détection) | `stride` (1 image / N) | `min_frames` (durée min. piste) | `min_conf` (confiance max min.) | Défauts uniques obtenus | Observation |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Essai 1 (sensible)** | `0.10` | `1` | `3` | `0.30` | `...` | Plus de pistes conservées, risque accru de bruit et temps de calcul plus long |
| **Essai 2 (strict)** | `0.25` | `3` | `8` | `0.50` | `...` | Filtrage plus sévère, risque de perdre des pistes courtes ou peu marquées |
| **Essai 3 (retenu)** | **`0.15`** | **`2`** | **`5`** | **`0.40`** | **8** *(0 pothole, 8 pothole_repair)* | **14** pistes brutes → **8** gardées sur `57.4 s` : bon compromis stabilité / rapidité |

---

## 3. Justification des paramètres retenus

* **`conf = 0.15` :** seuil suffisamment bas à la détection pour préserver la continuité du suivi d'une image à l'autre.
* **`stride = 2` :** traitement d'une image sur deux, réduisant le temps d'exécution tout en conservant un suivi fiable sur une vidéo de `57.4 s`.
* **`min_frames = 5` :** exige qu'une piste soit présente sur au moins 5 images traitées, écartant les détections trop brèves (sur **14** pistes brutes, **8** ont été conservées).
* **`min_conf = 0.40` :** filtre les pistes dont la confiance maximale n'atteint pas ce seuil minimal.