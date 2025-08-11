# 📜 AI Contract Reviewer  

![Aperçu de l'application](image1.PNG)

## 📌 Description  
**AI Contract Reviewer** est une application **Streamlit** qui analyse des contrats PDF grâce à des agents IA spécialisés, puis génère un rapport structuré comprenant :  
- **Résumé exécutif**  
- **Contexte légal**  
- **Analyse de la structure du contrat**  
- **Recommandations de négociation**  

Une fois l’analyse terminée, l’application envoie également un **message de confirmation via WhatsApp** en utilisant l’API officielle de Meta.  

---

## 🚀 Fonctionnalités  
- 📂 **Upload d’un contrat PDF**  
- 🤖 **Analyse multi-agents IA** avec **Mistral** :  
  - *Contract Structuring Expert* : Vérifie la clarté et la logique de la structure  
  - *Legal Framework Analyst* : Identifie les problèmes juridiques et les risques  
  - *Contract Negotiation Strategist* : Suggère des points de négociation  
- 📑 **Rapport Markdown** prêt à l’emploi  
- 📲 **Envoi d’un message WhatsApp** automatique pour confirmation  

---

## 🛠️ Technologies utilisées  
- [Python 3.10+](https://www.python.org/)  
- [Streamlit](https://streamlit.io/)  
- [PyPDF2](https://pypi.org/project/PyPDF2/) – Extraction de texte depuis PDF  
- [python-dotenv](https://pypi.org/project/python-dotenv/) – Gestion des variables d’environnement  
- [agno](https://pypi.org/project/agno/) – Framework d’agents IA  
- [Mistral AI](https://mistral.ai/) – Modèles d’analyse  
- [Requests](https://docs.python-requests.org/) – API WhatsApp  

---

