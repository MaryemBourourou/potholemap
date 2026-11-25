# Comparaison baseline et entraînement prolongé

Environnement : Kaggle, Tesla T4, Ultralytics 8.4.218. Même validation (2 667 images).
mAP calculé à conf=0.001 ; précision et rappel lus à conf=0.25.

| Essai | mAP50 global | mAP50 pothole | P pothole | R pothole | Durée |
|---|---|---|---|---|---|
| Baseline YOLOv8n, 50 ép. | 0,648 | 0,555 | 0,566 | 0,553 | 2 h 21 |
| + 30 ép. (80 au total) | 0,656 | 0,578 | 0,561 | 0,573 | (ton temps réel) |

mAP50-95 global : 0,359 pour les deux. pothole_repair : 0,742 puis 0,734.

## Échecs à conf=0.25

| Modèle | Ratés (sur 310) | Fausses alarmes (sur 1 748) |
|---|---|---|
| Baseline | 94 | 44 |
| + 30 ép. | 94 | 56 |

## Conclusion

Léger gain sur pothole (+0,023 de mAP50, +0,020 de rappel), précision stable,
pothole_repair en légère baisse. Un seul entraînement par modèle, pas de jeu de test
séparé : le gain est une tendance, pas une amélioration prouvée.
Modèle conservé : best_v2.pt (best.pt reste la référence).
