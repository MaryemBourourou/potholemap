# Commentaires des 10 exemples d'échecs — YOLOv8n (`potholemap`)

## Résumé des mesures
- **Erreurs sur la validation :** 94 images avec nid-de-poule raté sur 310 (environ 30 %), et 44 fausses alarmes sur 1 748 images propres (environ 2,5 %).
- **Rappel par taille :** petits `0,50`, moyens `0,57`, grands `0,55` — la taille n'est donc pas le facteur principal.
- **Matrice de confusion :** aucune confusion entre `pothole` et `pothole_repair`.

## 5 exemples ratés (`rates/`)
- Czech_Czech_000296.jpg (raté) : objet lointain ou petit sur la chaussée, peu visible à distance.
- Czech_Czech_000083.jpg (raté) : contraste faible entre le défaut et le revêtement de la route.
- val_batch0_labels.jpg — défaut non prédit (raté) : ombre ou tache sombre rendant les contours peu nets.
- val_batch1_labels.jpg — défaut non prédit (raté) : réparation ou rustine d'asphalte proche de l'apparence du défaut.
- val_batch2_labels.jpg — défaut non prédit (raté) : annotation douteuse ou manquante / défaut de faible contraste.

## 5 exemples de fausses alarmes (`fausses_alarmes/`)
- val_batch0_pred.jpg (fausse alarme probable (pas d'annotation), conf. 0,30) : plaque d'égout ou grille, forme et contraste proches d'un trou.
- val_batch0_pred.jpg (fausse alarme probable (pas d'annotation), conf. 0,28) : ombre ou tache sombre sur la chaussée.
- val_batch1_pred.jpg (fausse alarme probable (pas d'annotation), conf. 0,27) : réparation ou rustine d'asphalte.
- val_batch1_pred.jpg (fausse alarme probable (pas d'annotation), conf. 0,26) : contraste faible (tache ou irrégularité de la même couleur que la route).
- val_batch2_pred.jpg (fausse alarme probable (pas d'annotation), conf. 0,25) : annotation douteuse ou manquante sur une zone ambiguë.
