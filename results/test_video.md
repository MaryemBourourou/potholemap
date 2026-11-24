# Test vidéo — YOLOv8n baseline (`clip1.avi`)

## 1. Informations sur le clip
- **Source :** Pexels — `https://www.pexels.com/fr-fr/video/route-panoramique-sur-une-route-de-montagne-aux-philippines-29243823/` (Licence Pexels)
- **Fichier d'entrée / sortie :** `clips/clip1.mp4` (`1280x720`, 60 fps, 1040 frames) → `results_video/baseline_clip1/clip1.avi` (`conf=0.25`, `vid_stride=2`, `device="cpu"`)
- **Durée :** [À compléter : ex. ~17 s / durée affichée du clip]
- **Lumière :** [À compléter : ex. plein jour / soleil / ombres marquées / ciel couvert]
- **Type de route :** Route de montagne (revêtement, dénivelé et environnement extérieur des Philippines)

## 2. Comptage : vrais nids-de-poule vs détections
- **Vrais nids-de-poule observés à l'œil :** [À compléter]
- **Détectés par le modèle (`conf=0.25`) :** [À compléter — ex. détections ponctuelles isolées telles que frames 204–205 et 248, à vérifier sur l'ensemble de la vidéo]

## 3. Fausses alarmes observées
- **Plaques d'égout :** [À compléter : oui/non + passages concernés]
- **Ombres :** [À compléter : oui/non + passages concernés]
- **Réparations / fissures / bords de route :** [À compléter : oui/non + passages concernés]
- **Marquages au sol :** [À compléter : oui/non + passages concernés]

## 4. Différences avec RDD2022
- **Angle de vue :** [À compléter : caméra embarquée / point de vue / cadrage différent des prises de vue RDD2022]
- **Résolution :** Source HD `1280x720` traitée à `384x640` lors de l'inférence (`vid_stride=2`)
- **Luminosité et environnement :** [À compléter : contrastes, ombres d'arbres/montagne, texture d'asphalte différente]

## 5. Conclusion (écart de domaine)
[À compléter franchement : le comportement sur cette vidéo diffère de la validation sur RDD2022 en raison de l'écart de domaine (nouveau contexte géographique/routier, éclairage, cadrage et faible persistance temporelle de certaines détections isolées). Cela confirme l'intérêt de tester le modèle sur des vidéos réelles externes et de combiner détection et suivi temporel.]
