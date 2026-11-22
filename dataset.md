# Dataset

- **Source** : RDD2022 sur Figshare — https://ndownloader.figshare.com/files/38030910
- **Version / pays utilisés** : RDD2022 — sous-ensembles **Czech** (2 829 images train) et **Japan** (10 506 images train), soit 13 335 images au total.
- **Licence** : À vérifier sur la page Figshare officielle de RDD2022 (non recopiée car le lien direct télécharge l'archive sans afficher la fiche licence).
- **Citation** : Arya et al., *RDD2022: A multi-national image dataset for automatic Road Damage Detection*

## Classes retenues
`pothole` (classe `0`, issue de `D40`) et `pothole_repair` (classe `1`, issue de `D44`) — **raison du choix** : cibler directement les nids-de-poule actifs (`D40`) et les chaussées déjà réparées (`D44`) afin de distinguer les défauts à traiter des zones rapiécées et limiter les confusions avec les réparations existantes.

## Split

| Ensemble | Images | Images sans défaut | Instances |
|---|---|---|---|
| Train | 9 334 | 6 117 | 4 554 (1 738 pothole + 2 816 pothole_repair) |
| Val | 2 667 | 1 748 | 1 240 (450 pothole + 790 pothole_repair) |
| Test | 1 334 | 874 | 641 (252 pothole + 389 pothole_repair) |

## Conversion
Annotations d'origine (format **PASCAL VOC XML**) converties au format **YOLO** avec `src/convert_and_split.py`.

Vérification visuelle : voir `results/verification_boites.png`