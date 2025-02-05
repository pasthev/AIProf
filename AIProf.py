# A.I. Prof
# https://aiprof-pasthev.streamlit.app/ / https://github.com/pasthev/AIProf
#
# 
# Exécuter l'application avec : streamlit run AIProf.py ou python -m streamlit run AIProf.py
#

import streamlit as st
import google.generativeai as genai
import random
import json

# ------------------------------------------------------------------------------------------------------------------------------------------------
# Charger les sujets depuis le fichier JSON
# ------------------------------------------------------------------------------------------------------------------------------------------------
def load_sujets():
    with open("sujets.json", "r", encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------------------------------------------------------------------------------------
# Log conditionnel
# ------------------------------------------------------------------------------------------------------------------------------------------------
def warning(message):
	if log:
		st.warning(message)

# ------------------------------------------------------------------------------------------------------------------------------------------------
# Génère du contenu en fonction du bouton cliqué avec un prompt spécifique.
# ------------------------------------------------------------------------------------------------------------------------------------------------
def generate_content(button_label, prompt, title):
    if st.button(button_label, use_container_width=True):  # Le bouton reste dans sa colonne
        if sujet:
            warning(prompt)
            response = model.generate_content(prompt)
            
            # Stocker la réponse dans l'historique
            st.session_state.history.append((sujet, title, age, nbre_eleves, response.text))
            st.session_state.history_index = len(st.session_state.history) - 1
        else:
            st.warning(emptytext)
# ------------------------------------------------------------------------------------------------------------------------------------------------


log = False

sujets_par_age = load_sujets()

# Initialiser la valeur du champ sujet dans la session
if "random_subject" not in st.session_state:
    st.session_state.random_subject = ""


# Initialisation de l'historique des réponses (-1 signifie qu'aucune réponse n'a encore été enregistrée)
if "history" not in st.session_state:
    st.session_state.history = []
if "history_index" not in st.session_state:
    st.session_state.history_index = -1
	
# Configuration de l'API Gemini # https://docs.streamlit.io/develop/concepts/connections/secrets-management 
API_KEY = st.secrets["API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-pro")

# ------------------------------------------------------------------------------------------------------------------------------------------------
# Interface Streamlit
# ------------------------------------------------------------------------------------------------------------------------------------------------
#
col_titre, col_pic = st.columns([2, 1])
with col_titre:
    st.title("A.I. Prof")	# 📖 
    st.markdown(":blue[**Assistance à la préparation d'apprentissages \navec un vrai prof vraiment humain pour de vrai.**]")
    st.markdown(":blue[*Et aussi Google Gemini, un peu.*]")
    # st.write("**Assistance à la préparation d'apprentissages \navec un vrai prof vraiment humain pour de vrai.**")
    # st.write("*Et aussi Google Gemini, un peu.*")
with col_pic:
        st.image("AIProf00.jpg")





# Menu et curseur pour l'âge et le nombre d'élèves
col_age, col_nbre_eleves = st.columns([1, 2], border=True)
with col_age:
    age = st.selectbox("Âge des élèves", options=list(range(6, 18)), index=1)
with col_nbre_eleves:
    nbre_eleves = st.slider("Nombre d'élèves", 1, 34, 23)
	
# Champs de texte utilisateur
# Disposition en colonnes pour le champ texte et le bouton dé
col_text, col_button = st.columns([5,1], vertical_alignment="bottom")

# Champ de texte utilisateur
with col_text:
    sujet = st.text_input("Sur quoi doit porter l'apprentissage (exemple : Les fleuves de France) :", st.session_state.random_subject)

# Bouton avec un emoji de dé 🎲
with col_button:
    if st.button("🎲", help="Choix aléatoire dans la tranche d'âge sélectionnée", use_container_width=True):
        st.session_state.random_subject = random.choice(sujets_par_age[str(age)])
        st.rerun()  # Recharge la page pour mettre à jour le champ sujet


special = st.text_input("Indiquez s'il y a des consignes particulières à respecter (exemple : Insister sur ce qui définit un fleuve):", "")

# Variables texte pour la création du prompt
emptytext = "Veuillez entrer un sujet d'apprentissage."
subject = f" sur le sujet suivant : {sujet}."
public = f" Adapte le niveau pour des élèves âgés de {age} ans. Commence ta réponse par un petit paragraphe intitulé 'Pertinence du sujet' dans lequel tu indiques si tu estimes ce sujet approprié ou trop avancé pour commencer à l'enseigner à des élèves de cet âge, suivi d'une hline."
answers = " À la fin de ta réponse, insère une hline puis un titre gras 'Réponses pour l'enseignant', et indique la liste des réponses correctes."
consigne = ""
nombre = f" La classe compte {nbre_eleves} élèves."
remed = "Termine par un paragraphe décrivant des méthodes de remédiation destinée à des élèves qui ne comprendraient pas certaines parties de ce cours."
if special:
	consigne = f" Consigne particulière à respecter : {special}."

# Création des colonnes de boutons
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    generate_content("Cours",
		                 "Propose-moi un modèle pédagogique de cours" + subject + public + nombre + consigne, 
                         "Proposition de cours")

with col2:
    generate_content("Mémo",
                     "Propose-moi un mémo structuré, destiné à l'enseignant, listant les connaissances principales" + subject + public + consigne, 
                     "Mémo pour l'enseignant")

with col3:
    generate_content("Exercices",
                     "Propose-moi des exercices pratiques" + subject + public + consigne + answers, 
                     "Exercices pratiques")

with col4:
    generate_content("Ateliers",
                     "Propose-moi un modèle d'atelier pédagogique en sous-groupes" + subject + public + nombre + consigne, 
                     "Proposition d'atelier")

with col5:
    generate_content("Révision",
                     "Propose-moi un plan de révision" + subject + public + consigne, 
                     "Plan de révision")

with col6:
    generate_content("Devoirs",
                     "Rédige des devoirs à la maison sous forme de 3 à 5 exercices prêts à présenter" + subject + public + consigne + answers, 
                     "Devoirs à la maison")

with col7:
    generate_content("Quizz",
                     "Rédige un quizz prêt à présenter" + subject + public + consigne + answers, 
                     "Quizz / QCM")

# ------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage de la réponse actuelle
# ------------------------------------------------------------------------------------------------------------------------------------------------
#
if st.session_state.history:
    st.image("separator-c.jpg")
    sujet, type, age, nombre, contenu = st.session_state.history[-1]  	# Dernière réponse générée
    st.subheader(sujet)                    								# Affiche le sujet (ex: "📝 " + "L'eau")
    st.markdown(f":blue[*{type} - {nombre} élèves, {age} ans.*]")       # Affiche le type  (ex: "📜 " + "Proposition de cours")
    st.write(contenu)                              						# Affiche le texte généré sur toute la largeur
    st.write("*Rappel : Gemini peut parfois halluciner et fournir des réponses inexactes.*")

# ------------------------------------------------------------------------------------------------------------------------------------------------
# Affichage de l'historique avec style encadré et fond gris
# ------------------------------------------------------------------------------------------------------------------------------------------------
#
if len(st.session_state.history) > 1:  # Afficher l'historique uniquement s'il y a plusieurs réponses
    st.image("separator-b.png")
    # st.text("*Historique des réponses*") #  
    col_prev, col_index, col_next = st.columns([1, 1, 1], vertical_alignment="top")
    
    if col_prev.button("⬅ Précédent", use_container_width=True) and st.session_state.history_index > 0:
        st.session_state.history_index -= 1
    
    with col_index:
        st.markdown(
            f"<div style='text-align: center; font-weight: bold;'>Historique {st.session_state.history_index + 1} / {len(st.session_state.history)}</div>",
            unsafe_allow_html=True
        )

    
    if col_next.button("Suivant ➡", use_container_width=True) and st.session_state.history_index < len(st.session_state.history) - 1:
        st.session_state.history_index += 1

    sujeth, typeh, ageh, nombreh, contenth = st.session_state.history[st.session_state.history_index]
    st.subheader(sujeth)  # Affiche le titre (ex: "Proposition de cours :")
    st.markdown(f":blue[*{typeh} - {nombreh} élèves, {ageh} ans.*]")                         # Affiche le type (ex: "📝 " + "Proposition de cours")
    st.markdown(
        f"""
        <div style="padding: 10px; border-radius: 10px; background-color: #f0f0f0;">
            {contenth}
        </div>
        """,
        unsafe_allow_html=True
    )
# ------------------------------------------------------------------------------------------------------------------------------------------------
	
st.image("AIProf01.jpg", caption="pasthev 2025")
