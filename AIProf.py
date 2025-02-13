# 
# A.I. Prof
# https://aiprof-pasthev.streamlit.app/ / https://github.com/pasthev/AIProf
#
# 
# Exécuter l'application avec : streamlit run AIProf.py ou python -m streamlit run AIProf.py
#
import streamlit as st
import google.generativeai as genaipro
from google import genai
from google.genai import types
import random
import json
import os
import glob
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Load subjects and disciplines from JSON files with error handling
# ------------------------------------------------------------------------------------------------------------------------------------------------
def load_json(filename):
    filepath = os.path.join(JSON_PATH, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(j_err["filenotfound"].format(f=filename))
        return None
    except json.JSONDecodeError:
        st.error(j_err["jsondecoderr"].format(f=filename))
        return None
    except Exception as e:
        st.error(j_err["jsonexcption"].format(f=filename, e=e))
        return None
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Add pictures folder pathname to filename
# ------------------------------------------------------------------------------------------------------------------------------------------------
def pic_path(filename):
    fullpath = os.path.join(PICTURES_PATH, filename)
    return fullpath
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Detect available languages by checking the presence of the three required JSON files.
# ------------------------------------------------------------------------------------------------------------------------------------------------
def detect_available_languages():
    available_languages = []
    try:
        json_files = glob.glob(os.path.join(JSON_PATH, "*.json"))		# json_files = list all JSON files in the current directory
    except Exception as e:
        st.error(j_err["jsonnotfound"].format(e=e))                     # Error if glob fails (unlikely but good to catch)
        return available_languages 										# Returns empty list, so the app can still (partially) function

    language_codes = set(f.split("_")[-1].split(".")[0]                 # language_codes = ["fr-fr", "fr-ca", "en-us"...] name candidates
                     for f in json_files if "_" in f and "-" in f)      # only parses filenames containing _ and -
    for lang in language_codes:
        required_files = {                                              # Builds a list of all required files for each name candidate
                          f"interface_{lang}.json",
                          f"topics_{lang}.json",
                          f"disciplines_{lang}.json"
                         }
        if required_files.issubset({os.path.basename(f) for f in json_files}):  # checks if all files listed in required_files are available
            available_languages.append(lang)                                    # (os.path.basename(f) extracts names alone from full path)

    if not available_languages:                                                 # Check if any language was detected
        st.warning("No valid JSON language file in json folder")                #
        st.stop()                                                               # Critical error

    return available_languages
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Conditional logging
# ------------------------------------------------------------------------------------------------------------------------------------------------
def warning(message):
	if log:
		st.warning(message)
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Add an entry to the history.
# ------------------------------------------------------------------------------------------------------------------------------------------------
def add_to_history(prompt, subject, title, age, headcount, text):
    st.session_state.history.append((prompt, subject, title, age, headcount, text))
    st.session_state.history_index = len(st.session_state.history) - 1
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Browse history backwards to find a related 'Course' entry with the same subject, age, and number of students.
# ------------------------------------------------------------------------------------------------------------------------------------------------
def find_related_course(subject, age, headcount):
    for prompt, s, t, a, n, history_content in reversed(st.session_state.history):
        if t == "course" and s == subject and a == age and n == headcount:
            return history_content  												# Returns the corresponding course text
    return ""  																		#  or an empty string if no match is found
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Initialize all session variables.
# ------------------------------------------------------------------------------------------------------------------------------------------------
def initialize_session_state():

    if "lang" not in st.session_state:  			# App language
        st.session_state.lang = DEFAULT_LANG		#   defaults to French
    if "subject_index" not in st.session_state:		# subject field index
        st.session_state.subject_index = 0
    if "random_subject" not in st.session_state:	# subject field value
        st.session_state.random_subject = ""
    if "mode_selection" not in st.session_state:	# Topics or Disciplines mode
        st.session_state.mode_selection = "Sujets"  #   Default mode: topics
    if "expander_open" not in st.session_state:		# History expanded or not
        st.session_state.expander_open = False		#   False = collapsed, True = expanded
    if "history" not in st.session_state:			# response history
        st.session_state.history = []
    if "history_index" not in st.session_state:		# response history index
        st.session_state.history_index = -1			#   -1 means no response has been recorded yet
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Configure Gemini Pro (old) API and return the GenerativeModel, and handles potential errors
# Raises GeminiAPIError if there is an error calling the Gemini API.
# ------------------------------------------------------------------------------------------------------------------------------------------------
def configure_geminipro_api():
    try:
        api_key = st.secrets["API_KEY"]
        genaipro.configure(api_key=api_key)
        model = genaipro.GenerativeModel("gemini-pro")
        return model                                    # Return the configured model if successful
    except KeyError:                                    # Error if API_KEY is not found in secrets
        st.error(j_err["geminiapikey"])
        return None
    except Exception as e:                              # Catch any other configuration errors
        st.error(j_err["geminiexcptn"].format(e=e))
        return None
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Gemini API call and handle potential errors
# ------------------------------------------------------------------------------------------------------------------------------------------------
#
def call_gemini_api(full_prompt):
    if current_llm == GEMINI_PRO:
        try:
            response = model.generate_content(full_prompt)      # API call
            return response.text                                # Return the generated text if successful
        except Exception as e:                                  # Catch API call errors
            error_message = f"Gemini API error: {e}"            # Message for log
            st.error(j_err["geminicllerr"].format(e=e))         # Message for user
        raise GeminiAPIError(error_message) from e              # Raise custom exception, and encapsulates
        
    elif current_llm == GEMINI_FLS:
        client = genai.Client(api_key=st.secrets["API_KEY"], 
                        http_options={'api_version':'v1alpha'})
        try:
            response = client.models.generate_content(model='gemini-2.0-flash-thinking-exp', contents=full_prompt)        # API call
            return response.text                                # Return the generated text if successful
        except Exception as e:                                  # Catch API call errors
            error_message = f"Gemini API error: {e}"            # Message for log
            st.error(j_err["geminicllerr"].format(e=e))         # Message for user
        raise GeminiAPIError(error_message) from e              # Raise custom exception, and encapsulates
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Generate content based on the clicked button with a specific prompt.
# ------------------------------------------------------------------------------------------------------------------------------------------------
def generate_content(button_name):
    data = j_buttons[button_name]														    # Retrieves button data
    if st.button(data["label"], help=data["help"], use_container_width=True):  				# Display each button in its column
        if i_subject:																		# If subject input is not empty
            subject_override = c_subject  													# Default value
            if button_name in {"exercises", "workshops", "revision", "homework", "quiz"}: 	# In history for the concerned types,
                if course := find_related_course(i_subject, i_age, i_headcount):			# Does a course exists with input vals (Walrus operator)
                    subject_override = j_prompt["override"].format(course=course) 			# " following the previous course"
            # Generation and saving
            full_prompt = data["prompt"].format(
                                                l_subject=subject_override, 
                                                l_public=c_public, 
                                                l_headcount=c_headcount, 
                                                l_special=c_special, 
                                                l_answers=answers,
                                                l_remed=remediation
                                               )
#
            with st.spinner(j_texts["lbl_spn"]):	            # 🧠⏳ from json with spinner
                try:
                    content = call_gemini_api(full_prompt)      # Call the dedicated API function
                except GeminiAPIError:                          # Catches exception from GeminiAPIError
                    content = j_err["geminicller2"]             # Message utilisateur par défaut (à localiser)
#
                add_to_history(full_prompt,                     # Add to history in both cases of success or failure 
                               i_subject, 
                               button_name, 
                               i_age, 
                               i_headcount, 
                               content
                              )
        else:
            st.warning(j_prompt["empty_subject"])
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# ************ Code start *************
# ------------------------------------------------------------------------------------------------------------------------------------------------
#
LOG = False                             # If LOG = True, full prompt will be displayed before each answer
JSON_PATH = "json"  					# JSON folder location
PICTURES_PATH = "pics"					# Pictures folder location
DEFAULT_LANG = "fr-fr"
GEMINI_PRO = "Gemini Pro"
GEMINI_FLS = "Gemini 2.0 Flash Thinking Exp." 
current_llm = GEMINI_PRO
class GeminiAPIError(Exception):        # Defines an exception to raise in case of error on Gemini API call
    pass                                # NOP
#
initialize_session_state()								# Initialize all session variables
lang = st.session_state.lang  							# Reads current language key
topics = load_json(f"topics_{lang}.json")				# "topics" designates the pre-registered list of random matters here
disciplines = load_json(f"disciplines_{lang}.json")		# "disciplines" designates the list of school disciplines here
interface = load_json(f"interface_{lang}.json")         # "interface" contains all the application texts
#
										# Application texts from json:
j_texts = interface["texts"]			# Header, warnings...
j_help = interface["help"]				# Help popup texts
j_buttons = interface["buttons"]		# Buttons data
j_prompt = interface["prompts"]			# Prompt for API
j_err = interface["errors"]		    	# Error messages
j_grades = interface["grades"]		    # School grade names
#
j_stud = j_prompt["students"]			# Single variable to simplify code (j_stud = " students" or " élèves")
j_old = j_prompt["old"]					# Single variable to simplify code (j_old = " years old." or " ans.")
#
model = configure_geminipro_api()          # Configure API and get the model
if model is None:                       # If configuration failed, stop the app or handle it appropriately
    st.stop()                           # Stop the app if API config fails
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------------------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ " + j_texts["app_title"])      # Sidebar Title
    st.markdown(j_texts["app_shelp"])           # Short help message

    # st.markdown("---")                          # Generates hline

    st.subheader(j_texts["app_lnhlp"])          # Title for LLM choice
    available_languages = detect_available_languages()
    selected_language = st.selectbox("🌍 ...",												# Requires hardcoding: can't use j_texts["lbl_lng"]
                                     available_languages,
                                    index=available_languages.index(st.session_state.lang)
                                    if st.session_state.lang in available_languages else 0, # Defaults to first language if current not found
                                     key="language_selectbox",
                                     label_visibility="collapsed"
                                    )
    if selected_language != st.session_state.get("lang", DEFAULT_LANG):                     # Set a default for first app run
        st.session_state.subject_index = 0                                                  # Easier to prevent index errors with list lengths
        st.session_state.lang = selected_language
        st.rerun()                                                                          # Reloads page to refresh language

    st.subheader(j_texts["app_plhlp"])          # Title for LLM choice
    current_llm_selection = st.radio(           # Label for radio buttons
        j_texts["app_lthlp"],
        [GEMINI_PRO, GEMINI_FLS],               # Options : preset models choice
        index=[GEMINI_PRO, GEMINI_FLS].index(current_llm) if current_llm in [GEMINI_PRO, GEMINI_FLS] else 0 # Current model or first from list
    )

    if current_llm_selection != current_llm:    # If a new model is selected
        current_llm = current_llm_selection     # Select new current_llm
        # st.session_state.model_changed = True   # Optional : store info about model change
        # st.rerun()                              # Reload to apply new model

    st.markdown("---")                          # Generates hline
    st.markdown(j_texts["app_gthub"])           # GitHub link
    st.markdown(j_texts["app_crdts"])           # Credits info
    st.image(pic_path("aiprof02.png"))

#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Streamlit Interface : Header
# ------------------------------------------------------------------------------------------------------------------------------------------------
#
col_header, col_pic = st.columns([2, 1])													# Page header with picture ***************************
with col_header:
    st.title(j_texts["app_title"])				# Page title 📖 
    st.markdown(j_texts["app_sbtle"])			# Page subtitle
    st.markdown(j_texts["app_stext"])			# Page intro subtext
with col_pic:
        st.image(pic_path("aiprof01.png"))
#
# -------------------------------------------------------------------------------------------
# Streamlit Interface : Age, Headcount, Mode row
# -------------------------------------------------------------------------------------------
col_age, col_headcount, col_mode = st.columns([2, 4, 2], border=True)		# Menu and slider for age, number, and mode **********
with col_age:
    i_age = st.selectbox(j_texts["lbl_age"], options=list(range(6, 18)), index=1, 
                       help=j_help["age"]
                      )
    if str(i_age) in j_grades:                                                              # Age to string, then make sure age is 
        st.write(j_grades[str(i_age)])                                                      #   valid in j_grades
with col_headcount:																			# Number of students: headcount input
    i_headcount = st.slider(j_texts["lbl_nbr"], 1, 34, 23,
                           help=j_help["nbr"]
                           )
with col_mode:																				# Toggle between "Topics" and "Disciplines"
    mode_selection = st.radio(j_texts["lbl_mde"], [
                              j_texts["lbl_smt"], 
                              j_texts["lbl_ssj"],
                              j_texts["lbl_slb"]],
                              index=0, horizontal=True, help=j_help["mod"]
                             )
    if mode_selection != st.session_state.mode_selection:                                   # If mode changed
        st.session_state.subject_index = 0                                                  # Reset subject index (list lengths vary)
        st.session_state.mode_selection = mode_selection                                    # Update session mode
        st.rerun()                                                                          # Reloads immediately
#
# -------------------------------------------------------------------------------------------
# Streamlit Interface : Learning subject & Special instructions
# -------------------------------------------------------------------------------------------
#                                                                                           # Subject field and dice button **********************
col_topic_area = st.empty()                                                                 # Dynamic zone for col_topic (selectbox ou input)
col_random_area = st.empty()                                                                # Dynamic zone for col_random (dice button)

if mode_selection != j_texts["lbl_slb"]:                                                    # If mode is NOT "Free"
    with col_topic_area.container():
        col_topic, col_random = st.columns([6,1], vertical_alignment="bottom")
        current_list = topics if mode_selection == j_texts["lbl_ssj"] else disciplines      # Select list based on chosen mode
        with col_topic:
            i_subject = st.selectbox(j_texts["lbl_sbj"],
                                    [""] + current_list[str(i_age)],
                                    index=st.session_state.subject_index,				    # Use the stored index
                                    help=j_help["sbj"]
                                    )
        with col_random:		                                                            # Button with a dice emoji 🎲 *************************
            if st.button(j_texts["lbl_rnd"], use_container_width=True, help=j_help["rnd"]):
                st.session_state.subject_index = random.randint(
                                    1, len(current_list[str(i_age)])) 	                    # Avoid index 0 ("")
                st.rerun()                                                                  # Reloads page to update the subject field
#
    with col_random_area.container():
        pass                                                    # col_random is already managed in col_topic_area and should not disappear here
    i_free_subject = None                                       # To ensure that there is no confusion with the free mode
else:                                                           # If mode_selection == j_texts["lbl_slb"]: if mode is set to "Free"
    with col_topic_area.container():                            # Replace selectbox with input text
        i_free_subject = st.text_input(j_texts["lbl_sbj"],      # Free topic field
                                       "", help=j_help["hsl"])
    with col_random_area.container():                           # Hide the "Random" button
        pass                                                    # Display nothing in the random button column
    i_subject = i_free_subject                                  # In free mode, i_subject takes the value of the free text field

# -------------------------------------------------------------------------------------------
if mode_selection == j_texts["lbl_smt"]:                                                    # "Specific" field ***********************************
    s_prompt = j_texts["lbl_inm"]                               # Different "special" prompt if school subjects is selected
    s_help = j_help["spm"]                                      # Also a custom Help
else:
    s_prompt = j_texts["lbl_ins"]
    s_help = j_help["spc"]
    
i_special = st.text_input(s_prompt, "", help=s_help) 			# User instruction field
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Prompt construction
# ------------------------------------------------------------------------------------------------------------------------------------------------
#
if mode_selection == j_texts["lbl_ssj"]:							# If checked mode is "Topics" 
    c_subject = j_prompt["topic"].format(t_topic=i_subject)
elif mode_selection == j_texts["lbl_smt"]:							# If checked mode is "Disciplines"
    c_subject = j_prompt["subject"].format(t_subject=i_subject)
elif mode_selection == j_texts["lbl_slb"]:                          # If checked mode is "Free"
    c_subject = j_prompt["subject"].format(t_subject=i_subject)

c_public = j_prompt["public"].format(t_age=i_age)
if i_age < 12:														# If low age input, check if appropriate
    c_public += j_prompt["appropriate"]
answers = j_prompt["solution"]										# If work types requires answers for teacher
c_headcount = j_prompt["number"].format(t_headcount=i_headcount)
remediation = j_prompt["remediation"]										# Feeds Remediation, if later needed
c_special = ""
if i_special:														# If any specific instruction
    c_special = j_prompt["special"].format(t_special=i_special)
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Create button columns entirely based on JSON
# ------------------------------------------------------------------------------------------------------------------------------------------------
#
col_buttons = st.columns(len(j_buttons))
for i, (button_name, data) in enumerate(j_buttons.items()):
    with col_buttons[i]:
        generate_content(button_name)
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Display the current response
# ------------------------------------------------------------------------------------------------------------------------------------------------
#
if st.session_state.history:
    st.image(pic_path("seprtr01.png"))
    prompt, subject, type, age, headcount, content = st.session_state.history[-1]  	# Last generated response
    st.subheader(subject)                    										# Displays the subject (e.g., "📝 " + "Water")
    label = j_buttons[type]["label"]												# Text name from activity var e.g. memo -> "Mémo"
    st.markdown(f":blue[*{label} - {headcount}{j_stud}, {age}{j_old}*]")       		# Displays the type (e.g., "📜 " + "Course Proposal")
    if LOG: st.markdown(f"**Prompt :** :red[*{prompt}*]")							# If Debug mode, shows the full generated prompt
    st.write(content)                              									# Displays the generated text in full width
    st.markdown(j_texts["app_warng"])												# Hallucination warning reminder
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Display history navigation controls
# ------------------------------------------------------------------------------------------------------------------------------------------------
#
if len(st.session_state.history) > 1:											    # Only display history if there are multiple responses
    st.image(pic_path("seprtr02.png"))
    col_prev, col_index, col_next, col_expand = st.columns([2, 2, 2, 1], vertical_alignment="top")
#
# <- Navigate history
    if col_prev.button(j_texts["lbl_prv"], use_container_width=True) and st.session_state.history_index > 0:
        st.session_state.history_index -= 1
#
# -> Navigate history
    if col_next.button(j_texts["lbl_nxt"], use_container_width=True) and st.session_state.history_index < len(st.session_state.history) - 1:
        st.session_state.history_index += 1
#
# Indicates the displayed history index number and the number of entries (code *must* be after the two if <- ->)
    with col_index:
        hist=j_texts["lbl_hst"]
        st.markdown(
            f"<div style='text-align: center; font-weight: bold;'>{hist}{st.session_state.history_index + 1} / {len(st.session_state.history)}</div>",
            unsafe_allow_html=True
        )
# Lock history expander
    if col_expand.button(j_texts["lbl_lck"], type="tertiary", use_container_width=True,
                        help=j_help["lck"]
                        ):
        st.session_state.expander_open = not st.session_state.expander_open
        st.rerun()  															    # Reloads the page to apply the change
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Display Title and details of the currently displayed history with framed style and gray background
# ------------------------------------------------------------------------------------------------------------------------------------------------
#
    prompth, subjecth, typeh, ageh, headcounth, contenth = st.session_state.history[st.session_state.history_index]
    icon = j_buttons[typeh]["icon"] 											# Retrieves the icon from JSON
    with st.expander(f"{icon} {subjecth} ({j_buttons[typeh]['label']} - {headcounth}{j_stud}, {ageh}{j_old})",
                     expanded=st.session_state.expander_open
                    ):
        if LOG: st.markdown(f"**Prompt :** :red[*{prompth}*]")
        st.markdown(															# Displays the content of this history entry
            f"""
            <div style="padding: 10px; border-radius: 10px; background-color: #f0f0f0;">
                {contenth}
            </div>
            """,
            unsafe_allow_html=True
         )
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Clear history button
# ------------------------------------------------------------------------------------------------------------------------------------------------
    if st.button(j_texts["lbl_del"], use_container_width=True):
        st.session_state.history = []
        st.session_state.history_index = -1
        st.rerun()
#
# ------------------------------------------------------------------------------------------------------------------------------------------------
# Footer image
# ------------------------------------------------------------------------------------------------------------------------------------------------
#
st.image(pic_path("aiprof03.png"), caption=j_texts["app_crdts"])
#
