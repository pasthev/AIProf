# AIProf

AIProf est une application Streamlit qui assiste les enseignants dans la préparation de supports pédagogiques variés. Elle utilise l'API Gemini de Google pour générer des contenus adaptés à l'âge et au nombre d'élèves.

[AIProf en ligne](https://aiprof-pasthev.streamlit.app/)

## Capture d'écran

![AIProf Screenshot](aiprof.jpg)

## Fonctionnalités

- **Génération de contenus pédagogiques** : cours, mémos, exercices, ateliers, plans de révision, devoirs et quizz.
- **Personnalisation : choix du sujet**, du niveau scolaire (6-18 ans) et du nombre d'élèves.
- **Historique interactif** : navigation entre les générations passées et conservation des résultats.
- **Reprise automatique** : les exercices et évaluations font référence au dernier cours créé sur le même sujet.
- **Interface intuitive** : affichage clair, boutons avec bulles d'aide, et choix aléatoire de sujets.

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/pasthev/AIProf.git
cd AIProf
```
2. installez les dépendances nécessaires :
```bash
pip install -r requirements.txt
```
3. Assurez-vous d'avoir une clé API valide pour utiliser le modèle Gemini. Vous devez la renseigner dans `secrets.toml` sous la forme :
```bash
API_KEY = "votre_cle_api"
```
4. Lancez l'application :
```bash
streamlit run AIProf.py
```
## Utilisation

1. Sélectionnez l'âge des élèves et le nombre d'élèves.
2. Choisissez un mode : **Sujets** (précis) ou **Matières** (libre).
3. Entrez un sujet manuellement ou utilisez le bouton aléatoire 🎲.
4. Ajoutez une consigne spéciale si besoin.
5. Cliquez sur un bouton de contenu pour générer une ressource pédagogique.
6. Consultez et naviguez dans l'historique des générations.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus d'informations.
