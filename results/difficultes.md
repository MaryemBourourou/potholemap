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
