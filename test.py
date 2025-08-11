import os
import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team.team import Team
from agno.models.mistral import MistralChat
import re
import requests

# Charger variables d'environnement
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
whatsapp_token = os.getenv("WHATSAPP_ACCESS_TOKEN")

if not api_key:
    st.error("⚠️ La variable d'environnement MISTRAL_API_KEY n'est pas définie.")
    st.stop()

if not whatsapp_token:
    st.error("⚠️ La variable d'environnement WHATSAPP_ACCESS_TOKEN n'est pas définie.")
    st.stop()

def extract_pdf_text(file) -> str:
    pdf = PdfReader(file)
    text = ""
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def send_whatsapp_template_message(token, phone_number_id, recipient_number, template_name="hello_world", language_code="en_US"):
    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": recipient_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code}
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return True
    else:
        st.error(f"Erreur WhatsApp API: {response.status_code} - {response.text}")
        return False

def main():
    st.title("AI Contract Reviewer")

    st.markdown("This tool uses AI to review contracts and provide structured feedback, legal analysis, and negotiation recommendations.")

    uploaded_file = st.file_uploader("Chargez votre contrat PDF ici", type=["pdf"])

    if st.button("Review Contract"):
        if uploaded_file is None:
            st.error("Please upload a contract first.")
            return
        
        with st.spinner("Extraction du texte du contrat..."):
            contract_text = extract_pdf_text(uploaded_file)

        # Création des agents
        structure_agent = Agent(
            name="Contract Structuring Expert",
            role=(
                "You are a Contract Structuring Expert. Your role is to evaluate the structure "
                "of the following contract and suggest improvements. Here is the full contract text:\n\n"
                f"{contract_text}\n\n"
                "Analyze if the contract is structured clearly and logically. Identify missing or unclear sections. "
                "If missing structure, suggest a full structure with standard section headers "
                "(Definitions, Terms, Obligations, Termination, etc.). Avoid legal interpretation; focus on organization and clarity."
            ),
            model=MistralChat(id="mistral-medium", api_key=api_key),
        )

        legal_agent = Agent(
            name="Legal Framework Analyst",
            role=(
                "You are a Legal Framework Analyst tasked with identifying legal issues, risks, and key principles "
                "in the following contract. Contract text:\n\n"
                f"{contract_text}\n\n"
                "For each legal issue or observation, quote exactly the clause or sentence, "
                "then explain the concern briefly. Identify legal domain and likely jurisdiction."
            ),
            model=MistralChat(id="mistral-medium", api_key=api_key),
        )

        negotiation_agent = Agent(
            name="Contract Negotiation Strategist",
            role=(
                "You are a Contract Negotiation Strategist. Your job is to identify potentially negotiable or unbalanced parts "
                "in the following contract. Contract text:\n\n"
                f"{contract_text}\n\n"
                "For each point, quote the exact clause, explain why it may be negotiable or problematic, and suggest alternatives."
            ),
            model=MistralChat(id="mistral-medium", api_key=api_key),
        )

        manager_instructions = """
You are the Contract Manager Team. Your task is to coordinate the work of three specialized agents who analyzed the contract text below.

Produce a consolidated markdown report with these exact sections and format:

# Executive Summary

# Legal Context
clause: [quote the clause]
issue: [describe the legal issue]

# Contract Structure Feedback

# Negotiation Recommendations
clause: [quote the clause]
suggestion: [propose negotiation alternatives]

Make sure the report is clear, well-structured, and easy to read.
Include all details clearly so that the user can display this markdown report directly without further processing.
"""

        contract_team = Team(
            name="Contract Manager Team",
            members=[structure_agent, legal_agent, negotiation_agent],
            mode="coordinate",
            model=MistralChat(id="mistral-medium", api_key=api_key),
            instructions=manager_instructions,
            add_datetime_to_instructions=True,
            show_members_responses=False,
            markdown=True,
        )

        with st.spinner("Analyse en cours... cela peut prendre quelques instants"):
            try:
                response = contract_team.run(contract_text)
                content = response.content
                
                # Affichage dans Streamlit
                sections = content.split('\n# ')  
                
                for i, section in enumerate(sections):
                    if i == 0 and not section.startswith('Executive Summary'):
                        st.markdown(section)
                        continue
                    
                    if i != 0:
                        section = '# ' + section
                    
                    lines = section.split('\n')
                    title_line = lines[0].strip()
                    body = '\n'.join(lines[1:]).strip()
                    
                    st.header(title_line.replace('#', '').strip())
                    if body:
                        body = re.sub(r'clause:\s*\[(.*?)\]', r'*Clause:*  \n> \1', body, flags=re.DOTALL|re.IGNORECASE)
                        body = re.sub(r'suggestion:\s*\[(.*?)\]', r'*Suggestion:*  \n> \1', body, flags=re.DOTALL|re.IGNORECASE)
                        body = re.sub(r'issue:\s*\[(.*?)\]', r'*Issue:*  \n> \1', body, flags=re.DOTALL|re.IGNORECASE)
                        st.markdown(body)
                    
                    st.markdown("---")

                # Envoi WhatsApp - numéro test (sans +, format international)
                WHATSAPP_PHONE_NUMBER_ID = "780135948506513"
                recipient_number = "212654242803"  # ton numéro sans le "+"

                # Envoi message template hello_world (confirm)
                if send_whatsapp_template_message(whatsapp_token, WHATSAPP_PHONE_NUMBER_ID, recipient_number):
                    st.success("Message template WhatsApp envoyé avec succès !")
                else:
                    st.error("Erreur lors de l’envoi du message WhatsApp.")
            
            except Exception as e:
                st.error(f"Erreur lors de l'analyse : {e}")

if __name__ == "__main__":
    main()
