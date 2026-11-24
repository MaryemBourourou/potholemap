# Balayage du seuil de confiance — classe `pothole`

| Seuil | Précision pothole | Rappel pothole | F1 |
| :---: | :---: | :---: | :---: |
| 0.10 | 0.651 | 0.489 | 0.558 |
| 0.15 | 0.651 | 0.489 | 0.558 |
| 0.20 | 0.651 | 0.489 | 0.558 |
| 0.25 | 0.651 | 0.489 | 0.558 |
| 0.35 | 0.702 | 0.460 | 0.556 |
| 0.50 | 0.826 | 0.338 | 0.479 |

## Interprétation et recommandation pour le suivi
- **Meilleur compromis F1** : `conf = 0.10` (Précision = `0.651`, Rappel = `0.489`, F1 = `0.558`).
- **Recommandation suivi vidéo** : utiliser un seuil de détection plus bas (ex. `0.20`) pour conserver un rappel suffisant sur les nids-de-poule, combiné à un filtrage de piste plus strict (durée minimale de piste et confiance maximale atteinte sur la piste) pour filtrer les fausses détections isolées.
