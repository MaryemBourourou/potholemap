# Difficultés rencontrées et solutions adoptées — PotholeMap

## 1. Quota GPU Colab épuisé lors de l'entraînement prolongé
* **Problème :** L'épuisement du quota GPU gratuit sur Google Colab a bloqué la poursuite des entraînements et évaluations intensives sur place.
* **Capture ou log :** Message d'impossibilité de connexion au backend GPU sur Colab ; logs d'exécution sur Kaggle (`Tesla T4`, `14912 MiB`, `Ultralytics 8.4.218`) sur les `2 667` images de validation (`mAP50` global = `0,648`, `mAP50` `pothole` = `0,555`).
* **Causes :** Consommation du quota GPU gratuit par l'entraînement précédent (environ `2 h 21`) et limites de session sur Colab.
* **Solutions envisagées :** Attendre la réinitialisation du quota Colab, utiliser un autre compte ou une offre payante, entraîner sur CPU (écarté : plus d'une heure par époque), ou migrer sur Kaggle avec GPU.
* **Solution retenue :** Migration de l'entraînement et de l'évaluation vers **Kaggle** avec accélérateur **GPU Tesla T4**, tout en conservant Colab/CPU pour les tâches légères.
* **Preuve de résolution :** Capture du message Colab et sortie d'exécution sur Kaggle (`Tesla T4`) produisant des métriques cohérentes (`mAP50` global `0,648` et `mAP50` `pothole` `0,555` pour la baseline).

## 2. Espace disque insuffisant sur le PC pour télécharger le dataset
* **Problème :** Le téléchargement local de l'archive complète (`potholemap_yolo`, environ `2,12 Go`) sur le poste de travail n'était pas adapté en raison de l'espace disque disponible.
* **Capture ou log :** Contrainte d'espace disque local et logs de chargement du dataset dans `/kaggle/working/potholemap_yolo` (`9 334` images d'entraînement, `2 667` images de validation).
* **Causes :** Taille volumineuse du dataset complet face à l'espace libre sur la machine locale.
* **Solutions envisagées :** Télécharger puis transférer manuellement depuis le PC, libérer de l'espace disque local, ou rapatrier l'archive directement dans l'environnement distant.
* **Solution retenue :** Téléchargement direct depuis Google Drive vers `/kaggle/working/` via `gdown`, sans transit par le disque du PC.
* **Preuve de résolution :** Chargement réussi des dossiers `train` et `val` dans `/kaggle/working/potholemap_yolo` et exécution normale de l'entraînement et de l'évaluation.

## 3. Bouton Download inactif et erreur `404` sur `FileLink` dans Kaggle
* **Problème :** Le clic sur **Download** pour récupérer `essai_plus_longtemps.zip` (`20 Mo`) dans `/kaggle/working` ne déclenchait pas le téléchargement, et un lien `FileLink` renvoyait une erreur `404`.
* **Capture ou log :** Capture de l'éditeur Kaggle affichant `essai_plus_longtemps.zip` (`20M`) dans `/kaggle/working` avec le menu **Download** ouvert, erreur `404` avec `FileLink`, puis `git status` / `git ls-files` montrant `weights/best_v2.pt` et `results/essai_plus_longtemps/` poussés sur `origin/main`.
* **Causes :** Comportement ou blocage côté interface/navigateur lors du téléchargement direct depuis l'éditeur interactif Kaggle.
* **Solutions envisagées :** Vérifier le navigateur/bloqueur, tester `FileLink`, créer une version Kaggle (`Save Version`), ou pousser directement vers GitHub depuis le notebook.
* **Solution retenue :** Envoi direct vers le dépôt GitHub `MaryemBourourou/potholemap` depuis Kaggle via un *Fine-grained personal access token* (`Contents: Read and write`) stocké dans **Kaggle Secrets** (`UserSecretsClient`), suivi de la révocation du jeton.
* **Preuve de résolution :** Présence effective de `weights/best_v2.pt` et des fichiers de `results/essai_plus_longtemps/` sur la branche `main` de GitHub.

## 4. Balayage de seuil trompeur lors de l'évaluation
* **Problème :** Plusieurs seuils de confiance différents affichaient exactement les mêmes métriques (`P = 0,651`, `R = 0,489`).
* **Capture ou log :** Première sortie du script de balayage de seuils montrant des lignes identiques quel que soit le seuil testé, suivie de la seconde sortie après correction.
* **Causes :** Lecture directe des attributs `m.box.p` et `m.box.r` qui correspondent au point de F1 maximal plutôt qu'aux valeurs associées à chaque seuil évalué.
* **Solutions envisagées :** Relancer une évaluation complète pour chaque seuil ou extraire les métriques par seuil à partir d'une évaluation à bas seuil (`conf=0.001`).
* **Solution retenue :** Effectuer une évaluation unique à `conf=0.001` puis lire les valeurs de précision et de rappel correspondant à chaque seuil.
* **Preuve de résolution :** Nouvelle sortie du script affichant des métriques distinctes selon le seuil (précision variant de `0,348` jusqu'à `0,825`).

## 5. Rappel plus faible sur `pothole` (`0,487`) que sur `pothole_repair` (`0,754`) et écart de domaine
* **Problème :** Le modèle détecte mieux les réparations de chaussée (`pothole_repair`, rappel `0,754`, `mAP50` `0,742`) que les nids-de-poule (`pothole`, rappel `0,487`, `mAP50` `0,556`, avec `94` images sur `310` ayant au moins un nid-de-poule manqué), et l'application à des séquences réelles reste sensible à l'écart de domaine et au filtrage.
* **Capture ou log :** Métriques de validation (`val`), exemples dans `results/failures/` (rappel par taille : petits `0,50`, moyens `0,57`, grands `0,55` ; `44` fausses alarmes sur `1 748` images propres) et sorties de suivi/filtrage sur vidéo.
* **Causes :** Déséquilibre entre classes, forte variabilité visuelle des nids-de-poule (éclairage, ombres, humidité, revêtement), capacité du modèle léger `YOLOv8n` et filtrage des pistes peu persistantes ou sous le seuil.
* **Solutions envisagées :** Fusionner les deux classes, baisser les seuils sans contrôle, entraîner plus longtemps (`best_v2.pt`), ou conserver la séparation des classes en documentant les limites et le seuil de suivi retenu.
* **Solution retenue :** Conserver les deux classes distinctes (`0: pothole`, `1: pothole_repair`), documenter les limites (`results/resultats.md`) et retenir un seuil de suivi recommandé (`0,25` en validation / suivi) avec affichage transparent des comptages et de l'origine GPS.
* **Preuve de résolution :** Courbes, matrice de confusion, courbe PR et `results/failures/` enregistrés dans `results/`, complétés par les analyses dans `README.md` et `results/resultats.md`.

## 6. Réinitialisation d'environnement et chemins locaux (`ModuleNotFoundError` / `/content`)
* **Problème :** La réinitialisation de session ou la décompression d'archives dans un répertoire inattendu provoquait `ModuleNotFoundError: No module named 'ultralytics'` ou des chemins introuvables (`FileNotFoundError`).
* **Capture ou log :** Erreur `ModuleNotFoundError: No module named 'ultralytics'` après redémarrage de session et `FileNotFoundError` / dossiers manquants lors d'une extraction inattendue.
* **Causes :** Caractère éphémère de l'environnement d'exécution (réinitialisation des paquets/fichiers temporaires) et variations d'arborescence après extraction d'archive.
* **Solutions envisagées :** Réinstaller manuellement les dépendances à chaque fois ou structurer une initialisation/vérification systématique des chemins et des fichiers persistants.
* **Solution retenue :** Utiliser un bloc d'initialisation vérifiant l'existence des chemins (`os.path.exists`), installant les dépendances nécessaires et chargeant les poids/archives depuis l'emplacement persistant.
* **Preuve de résolution :** Exécution sans erreur des vérifications de splits (`train` : `9 334`, `val` : `2 667`, `test` : `1 334`), génération de `results/verification_boites.png` et exécution réussie de l'inférence après restauration.

## 7. Dépendances non installées sur le Space (`requirements (1).txt`)
* **Problème :** Lors du premier déploiement sur Hugging Face Spaces, le fichier de dépendances avait été ajouté sous le nom `requirements (1).txt`, empêchant l'installation automatique des paquets.
* **Capture ou log :** `Runtime error` au démarrage et logs de build indiquant l'absence des bibliothèques (`ultralytics`, `lapx`, `folium`, `gpxpy`, `opencv-python-headless`).
* **Causes :** Renommage automatique du fichier en `requirements (1).txt` lors du téléchargement/téléversement en local avant l'ajout sur le Space.
* **Solutions envisagées :** Supprimer `requirements (1).txt` et téléverser un fichier nommé `requirements.txt`, ou modifier la configuration du Space.
* **Solution retenue :** Suppression de `requirements (1).txt` dans l'onglet *Files* du Space et ajout de `requirements.txt` à la racine avec toutes les dépendances requises.
* **Preuve de résolution :** Log de build confirmant l'installation complète de `ultralytics`, `lapx`, `folium`, `gpxpy`, `pandas`, `opencv-python-headless` et `gradio` sans erreur.

## 8. Erreur ZeroGPU au démarrage (`No @spaces.GPU function detected during startup`)
* **Problème :** Après installation des dépendances, le Space affichait `Runtime error` au démarrage malgré le lancement du serveur Gradio sur `http://0.0.0.0:7860`.
* **Capture ou log :** Message affiché sous l'onglet *App* : `Runtime error — No @spaces.GPU function detected during startup`.
* **Causes :** Exécution sur matériel **ZeroGPU** Hugging Face nécessitant qu'au moins une fonction soit décorée avec `@spaces.GPU` au démarrage.
* **Solutions envisagées :** Changer le type de matériel du Space (CPU) ou ajouter `@spaces.GPU` sur la fonction principale d'inférence dans `app.py`.
* **Solution retenue :** Import de `spaces` dans `app.py` et décoration de la fonction de traitement (`traiter(...)`) avec `@spaces.GPU`.
* **Preuve de résolution :** Démarrage fonctionnel du Space `Maryembrr/potholemap` et traitement complet d'une vidéo de `57,4 s` générant vidéo annotée, résumé (`13` détections sans suivi, `8` défauts uniques gardés sur `14` pistes brutes), tableau, carte interactive et CSV.