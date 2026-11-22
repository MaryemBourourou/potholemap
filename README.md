# PotholeMap — Détection de nids-de-poule avec YOLOv8n

Projet de détection automatique de nids-de-poule (`pothole`) et de réparations de chaussée (`pothole_repair`) basé sur **YOLOv8n** et le jeu de données **RDD2022** (sous-ensembles **Czech** et **Japan**).

## Préparation des données et reproductibilité
- **Script de conversion et découpage** : `src/convert_and_split.py` (conversion PASCAL VOC XML → YOLO et répartition stratifiée `train` / `val` / `test` avec `random_state=42`).
- **Documentation détaillée du dataset** : voir [`dataset.md`](dataset.md) (`results/verification_boites.png` pour la vérification visuelle des boîtes).
- **Configuration et dépendances** : `data.yaml` et `requirements.txt`.

## Résultats d'évaluation

| Classe | P | R (1) | R (2) | mAP50 | mAP50-95 |
|---|---|---|---|---|---|
| `pothole` | 0,651 | 0,487 | — | 0,556 | 0,256 |
| `pothole_repair` | 0,650 | 0,754 | — | 0,742 | 0,459 |
| `all` | 0,650 | 0,621 | 0,649 | 0,358 | — |

## Analyse des échecs
- **Détections manquées et fausses alarmes** : 94 images avec nid-de-poule raté sur 310 (≈ 30 %), et 44 fausses alarmes sur 1 748 images propres (≈ 2,5 %).
- **Rappel selon la taille des objets** : petits `0,50`, moyens `0,57`, grands `0,55` — la taille des boîtes n'est donc pas le facteur principal d'erreur.
- **Confusion inter-classes** : aucune confusion entre `pothole` et `pothole_repair` dans la matrice de confusion.

## Utilisation / Suivi
- Modèle : `best.pt` (**YOLOv8n**, 2 classes : `pothole` et `pothole_repair`, ≈ 2,5 ms par image).
- Seuil conseillé pour le suivi (`model.track()`) : `0,25` (à confirmer après test).