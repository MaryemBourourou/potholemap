# Difficultés rencontrées

## Problème 1 : Effacement de `/content` / déconnexion Colab ou chemins locaux après extraction
- **Le problème** : Lors de l'exécution sur Google Colab, l'environnement temporaire `/content` peut être réinitialisé ou décompressé dans une arborescence inattendue, rendant les chemins vers les images, labels ou poids temporairement introuvables.
- **Message d'erreur ou comportement observé** : `FileNotFoundError` ou dossiers manquants/vides dans `/content/potholemap_yolo` lorsqu'on relance une cellule après interruption ou changement d'exécution.
- **Causes possibles** :
  - Expiration du délai d'inactivité ou changement de type d'exécution sur Colab (qui vide `/content`).
  - Archive `.zip` extraite avec un sous-dossier supplémentaire ou chemin différent de celui attendu par le script.
  - Dossier Google Drive non monté (`drive.mount`) avant d'accéder aux fichiers persistants.
- **Solution retenue** :
  - Monter Google Drive au début du notebook (`/content/drive`) et centraliser les fichiers persistants (`potholemap_yolo_dataset.zip`, `best.pt`, `results/`) dans Drive.
  - Vérifier l'existence des chemins avec `os.path.exists(...)` et décompresser automatiquement l'archive dans `/content` si nécessaire avant de lancer les traitements.
- **Preuve que c'est réglé** : Les comptages sur `train` (9 334 images), `val` (2 667 images) et `test` (1 334 images) s'exécutent sans erreur et `results/verification_boites.png` a bien été généré et sauvegardé dans `results/`.

## Problème 2 : Rappel plus faible sur `pothole` (`0,487`) que sur `pothole_repair` (`0,754`)
- **Le problème** : Le modèle YOLOv8n détecte nettement mieux les réparations de chaussée (`pothole_repair`, rappel `0,754`, `mAP50` `0,742`) que les nids-de-poule (`pothole`, rappel `0,487`, `mAP50` `0,556`), avec 94 images présentant un nid-de-poule raté sur 310 (≈ 30 %).
- **Message d'erreur ou comportement observé** : En évaluation (`val`), le rappel de `pothole` reste autour de `0,487` et des nids-de-poule sont absents des détections dans le dossier `results/failures/`, sans confusion directe avec `pothole_repair` dans la matrice de confusion.
- **Causes possibles** :
  - Déséquilibre de volume d'instances entre classes (davantage d'instances `pothole_repair` que `pothole` dans les splits).
  - Forte variabilité visuelle des nids-de-poule selon l'éclairage, l'ombre, l'humidité ou la texture de l'asphalte.
  - Seuil de confiance/NMS ou capacité du modèle léger `YOLOv8n` sur des défauts peu contrastés.
- **Solution retenue** :
  - Conserver la distinction explicite des deux classes (`0: pothole`, `1: pothole_repair`) pour éviter de mélanger nids-de-poule et zones réparées.
  - Documenter l'analyse d'erreurs (rappel par taille : petits `0,50`, moyens `0,57`, grands `0,55` ; 44 fausses alarmes sur 1 748 images propres) et retenir un seuil de suivi recommandé de `0,25` (`model.track()`) à valider sur séquence.
- **Preuve que c'est réglé** : L'évaluation complète est tracée dans `results/` (courbes, matrice de confusion, courbe PR, `failures/`), les métriques sont consignées dans `README.md`, et l'analyse des échecs est documentée.
