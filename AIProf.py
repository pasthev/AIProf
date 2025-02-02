import streamlit as st
import google.generativeai as genai

def warning(message):
	if log:
		st.warning(message)

# Configuration de l'API Gemini
# https://docs.streamlit.io/develop/concepts/connections/secrets-management 
API_KEY = st.secrets["API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-pro")

log = False
# Interface Streamlit
st.title("📖 AIProf")
st.write("Assistance à la préparation d'apprentissages - niveaux élémentaires")

# Champs de texte utilisateur
texte = st.text_input("Sur quoi doit porter l'apprentissage (exemple : Les fleuves de France) :", "")
special = st.text_input("Indiquez s'il y a des consignes particulières à respecter (exemple : Insister sur ce qui définit un fleuve):", "")


# Curseur pour l'âge des élèves
age = st.slider("Âge des élèves :", 6, 10, 7)
nbre_eleves = st.slider("Nombre d'élèves :", 1, 34, 23)

# Variables textes
emptytext = "Veuillez entrer un sujet d'apprentissage."
subject = f" sur le sujet suivant : {texte}."
# public = f" Adapte le niveau pour des élèves âgés de {age} ans. Si tu estimes ce sujet trop avancé pour commencer à l'enseigner à des élèves de cet âge, indique-le en tête de ta réponse."
public = f" Adapte le niveau pour des élèves âgés de {age} ans. Commence ta réponse par un petit paragraphe intitulé 'Pertinence du sujet' dans lequel tu indiques si tu estimes ce sujet approprié ou trop avancé pour commencer à l'enseigner à des élèves de cet âge, suivi d'une hline."
answers = " À la fin de ta réponse, insère une hline puis un titre gras 'Réponses pour l'enseignant', et indique la liste des réponses correctes."
consigne = ""
nombre = f" La classe compte {nbre_eleves} élèves."
if special:
	consigne = f" Consigne particulière à respecter : {special}."

# Boutons pour générer différents contenus
col1, col2, col3, col4, col5, col6 = st.columns(6)

if col1.button("Cours"):
    if texte:
        prompt = "Propose-moi un modèle pédagogique de cours" + subject + public +  nombre + consigne
        warning(prompt)
        response = model.generate_content(prompt)
        st.subheader("Proposition de cours :")
        st.write(response.text)
    else:
        st.warning(emptytext)

if col2.button("Exercices"):
    if texte:
        prompt = "Propose-moi des exercices pratiques" + subject + public + consigne + answers
        warning(prompt)
        response = model.generate_content(prompt)
        st.subheader("Exercices pratiques :")
        st.write(response.text)
    else:
        st.warning(emptytext)

if col3.button("Ateliers"):
    if texte:
        prompt = "Propose-moi un modèle d'atelier pédagogique en sous-groupes" + subject + public + nombre + consigne
        warning(prompt)
        response = model.generate_content(prompt)
        st.subheader("Proposition de cours :")
        st.write(response.text)
    else:
        st.warning(emptytext)

if col4.button("Révisions"):
    if texte:
        prompt = "Propose-moi un plan de révision" + subject + public + consigne
        warning(prompt)
        response = model.generate_content(prompt)
        st.subheader("Plan de révision :")
        st.write(response.text)
    else:
        st.warning(emptytext)

if col5.button("Devoirs"):
    if texte:
        prompt = "Rédige des devoirs à la maison sous forme de 3 à 5 exercices prêts à présenter" + subject + public + consigne + answers
        warning(prompt)
        response = model.generate_content(prompt)
        st.subheader("Devoirs :")
        st.write(response.text)
    else:
        st.warning(emptytext)
		
if col6.button("Quizz"):
    if texte:
        prompt = "Rédige un quizz prêt à présenter" + subject + public + consigne + answers
        warning(prompt)
        response = model.generate_content(prompt)
        st.subheader("Quizz :")
        st.write(response.text)
    else:
        st.warning(emptytext)

st.image("AIProf01.jpg", caption="pasthev 2025")

# Exécuter l'application avec : streamlit run AIProf.py ou python -m streamlit run AIProf.py