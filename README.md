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

## Choix du seuil

| Seuil de confiance | Précision | Rappel | F1-score | Remarque |
|---:|---:|---:|---:|---|
| 0,15 | — | — | — | Utilisé en entrée du suivi ByteTrack |
| **0,25** | — | **0,553** | **Meilleur F1** | **Seuil retenu pour la détection** |
| F1 max | — | 0,487 | F1 maximal | Rappel plus faible qu'au seuil 0,25 |

- **Meilleur compromis à 0,25 :** le meilleur score F1 est obtenu autour de `0,25`, choisi comme seuil principal de détection.
- **Nuance importante sur le rappel :** le rappel vaut `0,487` au point de F1 maximal, alors qu'il atteint `0,553` à `0,25` (permettant de récupérer davantage de défauts réels avant filtrage temporel).

## Analyse des échecs

- **Taux d'erreurs sur la validation :** `94` images avec nid-de-poule raté sur `310` (environ `30 %`), et `44` fausses alarmes sur `1 748` images propres (environ `2,5 %`).
- **Rappel par taille :** petits `0,50`, moyens `0,57`, grands `0,55` — la taille seule n'est donc pas le facteur principal des ratés.
- **Séparation des classes :** aucune confusion entre `pothole` et `pothole_repair` dans la matrice de confusion.
- **Causes principales observées :** contraste faible avec l'asphalte, objets éloignés ou peu marqués, ombres/taches sombres, plaques d'égout ou grilles, rustines/réparations et annotations douteuses ou manquantes (détails dans `results/failures/commentaires.md`).
  ## Environnements

- **Google Colab :** Ultralytics `8.4.216`, `torch 2.14.1`, Python `3.13.16`, GPU `Tesla T4`
- **Kaggle :** Ultralytics `8.4.218`, `torch 2.11.0+cu130`, Python `3.13.16`, GPU `Tesla T4` (`14912 MiB`)

## Modèles

- **`weights/best.pt`** : modèle baseline YOLOv8n (`50` époques, référence initiale).
- **`weights/best_v2.pt`** : modèle issu de l'entraînement prolongé de `+30` époques (`80` époques au total).

## Seuils

- **Détection simple :** seuil de confiance à **`conf = 0.25`**.

## Améliorations (50 vs 80 époques)

Évaluation sur le même jeu de validation (`2 667` images, dont `1 748` images sans annotation et `1 240` instances). Les métriques `mAP` sont calculées à `conf = 0.001` ; précision (`P`) et rappel (`R`) par classe sont lus à `conf = 0.25`.

| Essai | mAP50 global | mAP50 `pothole` | P `pothole` | R `pothole` | Durée |
|---|---|---|---|---|---|
| Baseline YOLOv8n (`50` ép.) | `0,648` | `0,555` | `0,566` | `0,553` | `2 h 21` |
| Essai prolongé (`+30` ép., `80` au total) | `0,656` | `0,578` | `0,561` | `0,573` | `(durée +30 ép.)` |

- **Métriques complémentaires :** `mAP50-95` global à `0,359` pour les deux modèles ; `mAP50` de `pothole_repair` à `0,742` (`50` ép.) puis `0,734` (`80` ép.).
- **Échecs à `conf = 0.25` :** `94` ratés (sur `310`) pour les deux modèles ; fausses alarmes (sur `1 748`) passant de `44` (`baseline`) à `56` (`+30` ép.) *(ratés communs : `(X)` / `94` ; fausses alarmes communes : `(Y)` — optionnel si non calculé)*.
- **Décision :** **`weights/best_v2.pt` est conservé** (`weights/best.pt` reste la référence). Le gain observé sur `pothole` (`+0,023` de `mAP50`, `+0,020` de rappel à `conf = 0.25`) reste une **tendance** (un seul entraînement par modèle, pas de jeu de test séparé, et hausse des fausses alarmes sur images propres).
- Rapports détaillés : [`results/comparaison_essais.md`](results/comparaison_essais.md) et [`results/difficultes.md`](results/difficultes.md).

## Test sur vidéo réelle

- **Source testée :** extrait vidéo de route montagneuse aux Philippines (`clip1.avi` / `results_video/`), évalué sur CPU avec le modèle YOLOv8n (`nc=2`).
- **Comportement observé :** détection des défauts image par image suivie d'un filtrage/suivi temporel (voir `results/test_video.md` pour le détail des détections et observations).

## Démo en ligne (Hugging Face Space)

L'application **PotholeMap** est déployée sur Hugging Face Spaces (ZeroGPU) :
👉 **[https://huggingface.co/spaces/Maryembrr/potholemap](https://huggingface.co/spaces/Maryembrr/potholemap)**

### Sorties générées
Après l'analyse d'une vidéo de route (avec trace `.gpx` ou trajet simulé), l'interface fournit :
1. **Vidéo annotée** : boîtes de détection (`pothole` / `pothole_repair`) et identifiants de suivi.
2. **Résumé** : durée analysée, détections brutes, défauts uniques filtrés et rappel sur la gravité relative.
3. **Tableau des défauts uniques** : identifiant, classe, gravité, score, confiance max, aire relative, nombre d'images, horodatage (`temps_s`) et coordonnées (`lat`, `lon`).
4. **Carte interactive** : tracé du trajet et localisation des défauts détectés.
5. **Export CSV** : téléchargement des défauts uniques pour exploitation externe.

> **Conseil d'utilisation (ZeroGPU) :** privilégiez un **clip vidéo court (15 à 20 secondes)** lors des tests ou démonstrations afin d'obtenir un traitement rapide et d'économiser le quota GPU.
