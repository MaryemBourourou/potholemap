# Résultats et interprétation — PotholeMap

Ce document synthétise les performances du projet selon trois niveaux d'analyse, en lien avec la partie 5 du cahier des charges.

## Synthèse par niveau

| Niveau | Chiffres à citer | Interprétation |
| :--- | :--- | :--- |
| **Modèle (validation)** | `mAP50` global **0,656** ; `pothole` **0,578** ; `pothole_repair` **0,734** ; **aucune confusion** entre les deux classes dans la matrice de confusion | Performance cohérente pour un modèle léger entraîné sur **RDD2022** ; l'entraînement prolongé apporte un gain modeste, à interpréter comme une tendance plutôt que comme une certitude statistique. |
| **Seuil et échecs** | Meilleur compromis F1 autour de **0,25** ; **94 images ratées sur 310** (≈ 30 %) avec nid-de-poule ; **44 fausses alarmes sur 1 748** images propres ; rappel par taille : **0,50** (petits), **0,57** (moyens), **0,55** (grands) | La taille des défauts n'explique pas à elle seule les échecs (rappel homogène autour de 0,50–0,57) ; les ombres, plaques d'égout, marquages ou zones réparées génèrent l'essentiel des fausses alarmes. |
| **Suivi sur vidéo** | Voir le tableau de comptage dans `results/comptage_videos.md` *(ex. Clip 1 : 13 détections brutes -> 0 `pothole` unique et 8 `pothole_repair` uniques avec `min_conf = 0,40`)* | Le suivi temporel et le filtrage (`min_frames`, `min_conf`) éliminent les détections isolées ou instables, mais les résultats restent sensibles à l'écart de domaine entre la vidéo testée et RDD2022. |

---

## Captures de l'application

Les captures d'écran de l'application en fonctionnement sont enregistrées dans `results/demo/` :

* `results/demo/capture_1.png` — *Interface Gradio et résumé de l'analyse (avec indication de l'origine GPS).*
* `results/demo/capture_2.png` — *Vidéo annotée, tableau des défauts uniques et carte géolocalisée.*
* `results/demo/capture_3.png` — *Réglages et export CSV / résultats complémentaires.*

*(Adapte les noms de fichiers exacts selon ceux que tu as déposés dans `results/demo/`.)*

---

## Limites

* **Écart de domaine (*domain shift*) :** les vidéos de test (caméra embarquée, angle de vue, éclairage, revêtement ou qualité d'encodage) peuvent différer des images d'entraînement issues de RDD2022, ce qui dégrade la détection ou le rappel sur certaines séquences.
* **Un seul entraînement par modèle :** chaque configuration n'a été entraînée qu'une seule fois, sans répétition sur plusieurs *seeds* pour mesurer la variance d'entraînement.
* **Absence de jeu de test séparé dédié :** l'évaluation quantitative repose principalement sur la validation plutôt que sur un jeu de test externe totalement indépendant et exhaustivement annoté.
* **GPS simulé :** en l'absence de trace `.gpx` synchronisée, les positions GPS sont interpolées entre deux points (`trajet SIMULÉ (positions fictives)`) et ne reflètent pas un trajet réel mesuré.
* **Gravité relative :** l'indicateur de gravité est une estimation relative (liée par exemple à la taille de la boîte ou à la confiance/surface apparente), et non une mesure physique réelle en centimètres ou en profondeur.
* **Possibles doublons d'identifiants (*ID switches*) :** un même défaut peut recevoir deux identifiants distincts (ou une piste peut être interrompue puis recréée) lors d'une occlusion, d'un changement d'angle ou d'une baisse ponctuelle de confiance.