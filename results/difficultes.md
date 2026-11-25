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
---

## Difficulté C : Téléchargement du dataset sans passer par le PC local
- **Problème :** Impossible ou inadapté de télécharger l'archive complète du dataset (`potholemap_yolo`, environ `2,12 Go`) sur le poste local avant de l'envoyer sur l'environnement d'entraînement.
- **Capture ou log :** Espace disque insuffisant sur le PC local et logs de téléchargement/extraction vers `/kaggle/working/potholemap_yolo` (`2 667` images de validation).
- **Causes :** Taille importante du dataset par rapport à l'espace disponible en local et coût inutile d'un aller-retour via le PC.
- **Solutions envisagées :** Télécharger l'archive sur le PC puis la transférer manuellement, libérer de l'espace disque local, ou rapatrier le dataset directement depuis Google Drive vers l'espace de travail Kaggle.
- **Solution retenue :** Téléchargement direct depuis Google Drive vers `/kaggle/working/` via `gdown`, sans passer par le PC.
- **Preuve de résolution / vérification :** Dataset présent et lisible dans `/kaggle/working/potholemap_yolo`, avec exécution complète de l'entraînement et de la validation sans erreur d'accès aux images ou labels.

---

## Difficulté D : Bouton Download inactif et erreur `404` sur `FileLink` dans Kaggle
- **Problème :** Cliquer sur le bouton **Download** pour récupérer `essai_plus_longtemps.zip` (`20 Mo`) dans `/kaggle/working` n'a rien déclenché, et un lien `FileLink` direct a renvoyé une erreur `404`.
- **Capture ou log :** Capture d'écran de l'éditeur Kaggle montrant `essai_plus_longtemps.zip` (`20M`) dans `/kaggle/working` avec le menu **Download** ouvert, retour `404` via `FileLink`, puis sorties `git status` / `git ls-files` montrant `weights/best_v2.pt` et `results/essai_plus_longtemps/` poussés sur `origin/main`.
- **Causes :** Comportement de l'interface ou du proxy de téléchargement de l'éditeur interactif Kaggle (ou blocage côté navigateur/extension).
- **Solutions envisagées :** Tester un autre navigateur ou désactiver les bloqueurs, télécharger les fichiers séparément, utiliser `FileLink`, créer une version Kaggle (`Save Version`), ou pousser directement vers GitHub depuis le notebook.
- **Solution retenue :** Envoi direct vers le dépôt GitHub `MaryemBourourou/potholemap` depuis Kaggle via `git` authentifié avec un *Fine-grained personal access token* (`Contents: Read and write`) stocké dans **Kaggle Secrets**.
- **Preuve de résolution / vérification :** `weights/best_v2.pt` et les fichiers de `results/essai_plus_longtemps/` sont bien présents sur la branche `main` de GitHub (commit `24954eb`), et le jeton temporaire a été révoqué après l'opération.
