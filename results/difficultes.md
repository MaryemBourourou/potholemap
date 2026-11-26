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

# Difficultés techniques rencontrées — `potholemap`

## Difficulté A : Quota GPU Colab épuisé
- **Problème :** Impossible d'obtenir un GPU sur Google Colab pour poursuivre les tâches lourdes.
- **Capture ou log :** Message / capture *« Impossible de se connecter au backend de GPU »* lors de la demande d'allocation GPU.
- **Causes :** Consommation du quota gratuit GPU par l'entraînement précédent d'environ `2 h 21`.
- **Solutions envisagées :** Attendre la réinitialisation du quota, utiliser un autre compte, passer sur une offre Colab payante, entraîner sur CPU (écarté : plus d'une heure par époque, soit des dizaines d'heures au total), ou basculer sur Kaggle.
- **Solution retenue :** Migration vers **Kaggle** pour la suite (prévue au Jour 5), tout en réalisant les tâches légères d'analyse et d'inférence vidéo sur CPU Colab.
- **Preuve de résolution / vérification :** En cours — à compléter au Jour 5 avec la vérification `GPU : True` sur Kaggle.

---

## Difficulté B : Balayage de seuil trompeur lors de l'évaluation
- **Problème :** Trois seuils de confiance différents affichaient exactement les mêmes métriques (`P = 0,651`, `R = 0,489`).
- **Capture ou log :** Première sortie du script de balayage de seuils montrant des valeurs identiques quel que soit le seuil testé.
- **Cause :** Les attributs `m.box.p` et `m.box.r` retournent les valeurs mesurées au point de F1 maximal, et non celles correspondant au seuil demandé.
- **Solutions envisagées :** Relancer une évaluation complète à chaque seuil ou extraire les valeurs directement depuis les courbes de précision/rappel à partir d'une évaluation unique à bas seuil.
- **Solution retenue :** Effectuer **une seule évaluation à `conf=0.001`**, puis lire les valeurs de précision et de rappel au seuil souhaité.
- **Preuve de résolution / vérification :** Seconde sortie du script où les métriques varient bien selon le seuil (précision évoluant de `0,348` jusqu'à `0,825`).

---

## Cas bonus : `ModuleNotFoundError: No module named 'ultralytics'` après réinitialisation Colab
- **Problème :** Erreur `ModuleNotFoundError: No module named 'ultralytics'` lors de l'importation après ouverture d'une nouvelle session ou réinitialisation de l'environnement.
- **Capture ou log :** `ModuleNotFoundError: No module named 'ultralytics'`.
- **Cause :** L'environnement d'exécution Colab est éphémère et réinitialisé à chaque nouvelle session / déconnexion, effaçant les paquets installés localement.
- **Solutions envisagées :** Réinstaller manuellement `ultralytics` à chaque fois ou structurer une cellule de démarrage/restauration.
- **Solution retenue :** Utiliser systématiquement la **cellule de restauration** (montage Google Drive, définition de `BASE`, `!pip install -q ultralytics` et chargement de `best.pt`).
- **Preuve de résolution / vérification :** Restauration réussie de la session et exécution de `best.predict(...)` sans erreur d'import.

# Difficultés rencontrées et solutions adoptées — Jour 5

## 1. Quota GPU Colab épuisé lors de l'entraînement prolongé

- **Problème :** L'épuisement du quota GPU sur Google Colab a bloqué la poursuite des entraînements et évaluations sur place.
- **Preuve / Log / Capture :** Sortie d'exécution Kaggle sur `Tesla T4` (`14912 MiB`, `Ultralytics 8.4.218`) et résultats de validation sur les `2 667` images (`mAP50` global = `0,648`, `mAP50` `pothole` = `0,555`).
- **Causes :** Limite de temps GPU / session atteinte sur l'environnement Colab.
- **Solutions envisagées :** Attendre la réinitialisation du quota Colab, réduire la taille de batch/résolution, ou migrer vers un autre environnement GPU disposant d'un quota disponible.
- **Solution retenue :** Migration de l'entraînement et de l'évaluation vers **Kaggle** avec GPU **Tesla T4**.
- **Vérification :** Les scores de validation obtenus sur Kaggle (`mAP50` global `0,648` et `mAP50` `pothole` `0,555` pour la baseline) correspondent aux références attendues, confirmant une migration sans perte de performance.

---

## 2. Espace disque insuffisant sur le PC pour télécharger le dataset

- **Problème :** Le téléchargement local du dataset complet (`potholemap_yolo`, environ `2,12 Go`) sur le PC n'était pas adapté en raison de l'espace disque limité.
- **Preuve / Log / Capture :** Contrainte d'espace local et logs de chargement du dataset directement dans `/kaggle/working/potholemap_yolo` (`9 334` images d'entraînement, `2 667` images de validation).
- **Causes :** Taille importante du dataset face à l'espace disponible sur le poste local.
- **Solutions envisagées :** Télécharger l'archive sur le PC puis l'envoyer manuellement, nettoyer le disque local, ou rapatrier directement le dataset dans l'espace de travail Kaggle.
- **Solution retenue :** Téléchargement direct depuis Google Drive vers `/kaggle/working/` via `gdown`, sans passer par le disque du PC.
- **Vérification :** Les dossiers `train` et `val` se sont chargés sans erreur dans `/kaggle/working/potholemap_yolo` et l'entraînement / validation s'est déroulé normalement.

---

## 3. Bouton Download inactif et erreur `404` sur `FileLink` dans Kaggle

- **Problème :** Cliquer sur **Download** pour récupérer `essai_plus_longtemps.zip` (`20 Mo`) dans `/kaggle/working` n'a rien déclenché, et un lien `FileLink` direct a renvoyé une erreur `404`.
- **Preuve / Log / Capture :** Capture d'écran de l'éditeur Kaggle montrant `essai_plus_longtemps.zip` (`20M`) dans `/kaggle/working` avec le menu **Download** ouvert[cite: 1], retour `404` via `FileLink`, puis `git status` / `git ls-files` montrant `weights/best_v2.pt` et `results/essai_plus_longtemps/` poussés sur `origin/main`.
- **Causes :** Blocage ou comportement de l'interface/proxy de téléchargement dans l'éditeur interactif Kaggle (ou restriction de téléchargement/fenêtre côté navigateur)[cite: 1].
- **Solutions envisagées :** Vérifier les paramètres du navigateur/bloqueur, tester `FileLink`, créer une version Kaggle (`Save Version`) pour télécharger depuis l'onglet *Output*, ou pousser directement vers GitHub depuis le notebook.
- **Solution retenue :** Envoi direct vers le dépôt GitHub `MaryemBourourou/potholemap` depuis Kaggle à l'aide d'un *Fine-grained personal access token* (`Contents: Read and write`) stocké dans **Kaggle Secrets** (`UserSecretsClient`).
- **Vérification :** `weights/best_v2.pt` et les fichiers de `results/essai_plus_longtemps/` sont bien présents sur la branche `main` de GitHub, et le jeton d'accès a été révoqué après usage.

---

# Difficultés rencontrées et solutions adoptées — Jour 6

## 1. Dépendances non installées sur le Space à cause du fichier `requirements (1).txt`

- **Problème :** Lors du premier déploiement sur Hugging Face Spaces, le fichier de dépendances téléversé portait le nom `requirements (1).txt` au lieu de `requirements.txt`, empêchant l'installation automatique des bibliothèques requises.
- **Preuve / Log / Capture :** Erreur au démarrage du Space (`Runtime error`) et logs de build montrant l'absence d'installation de `ultralytics`, `lapx`, `folium`, `gpxpy` et `opencv-python-headless`.
- **Causes :** Fichier renommé automatiquement avec un suffixe `(1)` lors du téléchargement/téléversement sur le poste local avant l'ajout dans le dépôt du Space.
- **Solutions envisagées :** Modifier la configuration du Space ou supprimer le fichier mal nommé et téléverser un fichier nommé exactement `requirements.txt`.
- **Solution retenue :** Suppression de `requirements (1).txt` dans l'onglet *Files* du Space et ajout de `requirements.txt` à la racine avec l'ensemble des dépendances du projet.
- **Vérification :** Le log de build suivant confirme l'installation complète des paquets (`ultralytics`, `lapx`, `folium`, `gpxpy`, `pandas`, `opencv-python-headless`, `gradio`) sans erreur.

---

## 2. Erreur ZeroGPU au démarrage (`No @spaces.GPU function detected during startup`)

- **Problème :** Même après l'installation réussie de toutes les dépendances, le Space affichait `Runtime error` au démarrage bien que le serveur Gradio se lance sur `http://0.0.0.0:7860`.
- **Preuve / Log / Capture :** Message affiché sous l'onglet *App* : `Runtime error — No @spaces.GPU function detected during startup`[cite: 2].
- **Causes :** Le Space est configuré sur le matériel **ZeroGPU** de Hugging Face, qui exige la présence d'au moins une fonction décorée avec `@spaces.GPU` au démarrage de l'application[cite: 2].
- **Solutions envisagées :** Basculer le Space sur un matériel CPU classique (plus lent pour l'inférence vidéo) ou adapter `app.py` pour déclarer `@spaces.GPU` sur la fonction d'analyse.
- **Solution retenue :** Ajout de `import spaces` en tête de `app.py` et décoration de la fonction `traiter(...)` avec `@spaces.GPU`.
- **Vérification :** Le Space `Maryembrr/potholemap` démarre correctement et l'analyse complète d'une séquence vidéo de `57,4 s` produit la vidéo annotée, le résumé (`13` détections sans suivi, `8` défauts uniques gardés sur `14` pistes brutes), le tableau, la carte interactive et le fichier CSV[cite: 3].