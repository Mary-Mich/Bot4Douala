# This files contains your custom actions which can be used to run
# custom Python code.
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging
from database.database import UniversityDatabase

logger = logging.getLogger(__name__)

# Initialiser la base de données
db = UniversityDatabase()

class ActionGuideOrientation(Action):
    def name(self) -> Text:
        return "action_guide_orientation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Récupérer le domaine d'intérêt de l'utilisateur
        domaine_interest = next(tracker.get_latest_entity_values("domaine"), None)
        
        if not domaine_interest:
            dispatcher.utter_message(text="Pour mieux vous orienter, pourriez-vous me préciser votre domaine d'intérêt ? (sciences, santé, droit, technologie, commerce, etc.)")
            return []
        
        # Rechercher les filières correspondantes
        filieres = db.get_filieres_by_domaine(domaine_interest)
        
        if not filieres:
            dispatcher.utter_message(text=f"Je n'ai pas trouvé de filières spécifiques pour le domaine '{domaine_interest}'. Voici plutôt toutes nos formations disponibles :")
            etablissements = db.get_etablissements()
            response = "Établissements disponibles :\n"
            for etab in etablissements:
                response += f"• {etab['nom']} - {etab['description']}\n"
            dispatcher.utter_message(text=response)
            return []
        
        # Préparer la réponse
        response = f"Voici les filières correspondant à vos intérêts en '{domaine_interest}':\n\n"
        
        for filiere in filieres[:5]:  # Limiter à 5 résultats
            type_icon = "🎯" if filiere['type'] == 'professionnelle' else "📚"
            response += f"{type_icon} **{filiere['nom']}** ({filiere['type']})\n"
            response += f"   📍 {filiere['etablissement_nom']}\n"
            response += f"   ⏱️ {filiere['duree']}\n"
            response += f"   💰 {filiere['frais_inscription']}\n\n"
        
        if len(filieres) > 5:
            response += f"Et {len(filieres) - 5} autres formations...\n"
        
        response += "Pour plus de détails sur une filière spécifique, dites-moi son nom !"
        
        dispatcher.utter_message(text=response)
        return [SlotSet("domaine_interet", domaine_interest)]

class ActionDetailFiliere(Action):
    def name(self) -> Text:
        return "action_detail_filiere"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        filiere_nom = next(tracker.get_latest_entity_values("filiere"), None)
        
        if not filiere_nom:
            dispatcher.utter_message(text="De quelle filière souhaitez-vous connaître les détails ?")
            return []
        
        details = db.get_filiere_details(filiere_nom)
        
        if not details:
            # Essayer une recherche approximative
            similar_filieres = db.search_filieres(filiere_nom)
            if similar_filieres:
                response = f"Je n'ai pas trouvé '{filiere_nom}' exactement. Peut-être cherchez-vous :\n"
                for filiere in similar_filieres[:3]:
                    response += f"• {filiere['nom']}\n"
                dispatcher.utter_message(text=response)
            else:
                dispatcher.utter_message(text=f"Je n'ai pas trouvé la filière '{filiere_nom}'. Vérifiez l'orthographe ou consultez la liste complète des filières.")
            return []
        
        # Construire une réponse détaillée
        response = f"🎓 **{details['nom']}**\n\n"
        response += f"**Type :** {details['type'].capitalize()}\n"
        response += f"**Durée :** {details['duree']}\n"
        response += f"**Établissement :** {details['etablissement_nom']}\n"
        response += f"**Frais d'inscription :** {details['frais_inscription']}\n\n"
        
        response += f"**Description :**\n{details['description']}\n\n"
        
        if details['debouches']:
            response += f"**Débouchés :**\n{details['debouches']}\n\n"
        
        if details['conditions_admission']:
            response += f"**Conditions d'admission :**\n{details['conditions_admission']}\n\n"
        
        if details['contact_etablissement']:
            response += f"**Contact :** {details['contact_etablissement']}\n"
        
        if details['site_web_etablissement']:
            response += f"**Site web :** {details['site_web_etablissement']}"
        
        dispatcher.utter_message(text=response)
        return [SlotSet("filiere_choisie", details['nom'])]

class ActionListeEtablissements(Action):
    def name(self) -> Text:
        return "action_liste_etablissements"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        etablissements = db.get_etablissements()
        
        response = "🏛️ **Établissements de l'Université de Douala**\n\n"
        
        for etab in etablissements:
            response += f"**• {etab['nom']}** ({etab['type']})\n"
            response += f"  {etab['description']}\n"
            if etab['contact']:
                response += f"  📞 {etab['contact']}\n"
            if etab['site_web']:
                response += f"  🌐 {etab['site_web']}\n"
            response += "\n"
        
        dispatcher.utter_message(text=response)
        return []

class ActionGuidePreinscription(Action):
    def name(self) -> Text:
        return "action_guide_preinscription"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        processus = db.get_processus_preinscription()
        documents = db.get_documents_requis()
        dates = db.get_dates_importantes()
        
        response = "📝 **Guide de Préinscription - Université de Douala**\n\n"
        
        response += "**📋 Étapes du processus :**\n"
        for etape in processus:
            response += f"{etape['etape']}. {etape['description']}\n"
            if etape['details']:
                response += f"   → {etape['details']}\n"
        
        response += "\n**📄 Documents requis :**\n"
        for doc in documents:
            obligatoire = "🔴" if doc['obligatoire'] else "🟡"
            response += f"{obligatoire} {doc['type_document']}\n"
        
        response += "\n**📅 Dates importantes :**\n"
        for date in dates:
            response += f"• {date['evenement']} : {date['date_debut']}"
            if date['date_fin'] and date['date_fin'] != date['date_debut']:
                response += f" au {date['date_fin']}"
            response += f" ({date['annee_academique']})\n"
        
        response += "\n**💡 Important :** Consultez régulièrement le site officiel pour les mises à jour."
        
        dispatcher.utter_message(text=response)
        return []

class ActionFiliereProfessionnelleScience(Action):
    def name(self) -> Text:
        return "action_filieres_professionnelles_science"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        filieres = db.get_filieres_by_type("professionnelle", "Faculté des Sciences")
        
        response = "🎯 **Filières Professionnelles - Faculté des Sciences**\n\n"
        response += "Ces formations pratiques préparent directement à l'insertion professionnelle :\n\n"
        
        for filiere in filieres:
            response += f"**• {filiere['nom']}**\n"
            response += f"  Durée : {filiere['duree']}\n"
            response += f"  Frais : {filiere['frais_inscription']}\n"
            response += f"  {filiere['description']}\n"
            response += f"  Débouchés : {filiere['debouches']}\n\n"
        
        response += "💼 **Avantages des filières professionnelles :**\n"
        response += "• Formation pratique et concrète\n• Stages en entreprise\n• Insertion professionnelle rapide\n• Compétences directement opérationnelles"
        
        dispatcher.utter_message(text=response)
        return []

class ActionFiliereClassiqueScience(Action):
    def name(self) -> Text:
        return "action_filieres_classiques_science"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        filieres = db.get_filieres_by_type("classique", "Faculté des Sciences")
        
        response = "📚 **Filières Classiques - Faculté des Sciences**\n\n"
        response += "Formations fondamentales permettant la poursuite d'études ou la recherche :\n\n"
        
        for filiere in filieres:
            response += f"**• {filiere['nom']}**\n"
            response += f"  Durée : {filiere['duree']}\n"
            response += f"  Frais : {filiere['frais_inscription']}\n"
            response += f"  {filiere['description']}\n"
            response += f"  Débouchés : {filiere['debouches']}\n\n"
        
        response += "🎓 **Avantages des filières classiques :**\n"
        response += "• Formation théorique solide\n• Poursuite en master/doctorat\n• Orientation vers la recherche\n• Base large pour diverses spécialisations"
        
        dispatcher.utter_message(text=response)
        return []

class ActionComparerFiliere(Action):
    def name(self) -> Text:
        return "action_comparer_filieres"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        filiere_nom = next(tracker.get_latest_entity_values("filiere"), None)
        
        if not filiere_nom:
            dispatcher.utter_message(text="Quelle filière souhaitez-vous que je compare ?")
            return []
        
        details = db.get_filiere_details(filiere_nom)
        
        if not details:
            dispatcher.utter_message(text=f"Je n'ai pas trouvé la filière '{filiere_nom}'.")
            return []
        
        # Trouver des filières similaires pour comparaison
        similaires = db.search_filieres(details['nom'].split()[-1])  # Recherche par mot-clé
        
        if len(similaires) <= 1:
            dispatcher.utter_message(text=f"Voici les détails de {details['nom']} :\n\n{details['description']}")
            return []
        
        response = f"🔍 **Comparaison de filières similaires**\n\n"
        
        for filiere in similaires[:3]:  # Comparer avec 2 autres maximum
            response += f"**{filiere['nom']}** ({filiere['type']})\n"
            response += f"• Durée : {filiere['duree']}\n"
            response += f"• Frais : {filiere['frais_inscription']}\n"
            response += f"• Établissement : {filiere['etablissement_nom']}\n"
            response += f"• Type : {filiere['type'].capitalize()}\n\n"
        
        response += "💡 **Conseil :** Les filières professionnelles sont plus pratiques, les classiques plus théoriques."
        
        dispatcher.utter_message(text=response)
        return []

class ActionSuggestFiliere(Action):
    def name(self) -> Text:
        return "action_suggest_filieres"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Récupérer les préférences de l'utilisateur
        domaine = tracker.get_slot("domaine_interet")
        type_prefere = tracker.get_slot("type_filiere_prefere")  # professionnelle/classique
        
        if not domaine:
            dispatcher.utter_message(text="Pour vous suggérer des filières, dites-moi ce qui vous intéresse !")
            return []
        
        # Rechercher les filières correspondantes
        if type_prefere:
            filieres = db.get_filieres_by_type(type_prefere)
            # Filtrer par domaine
            filieres = [f for f in filieres if any(domaine.lower() in f['description'].lower() or 
                                                  domaine.lower() in f['nom'].lower() for f in [f])]
        else:
            filieres = db.get_filieres_by_domaine(domaine)
        
        if not filieres:
            dispatcher.utter_message(text=f"Je n'ai pas trouvé de filières correspondant à vos critères. Essayez d'élargir votre recherche.")
            return []
        
        # Trier par popularité ou pertinence (ici simple tri alphabétique)
        filieres = sorted(filieres, key=lambda x: x['nom'])[:3]
        
        response = f"💡 **Suggestions pour vous** (basé sur : {domaine}"
        if type_prefere:
            response += f", {type_prefere}"
        response += ")\n\n"
        
        for i, filiere in enumerate(filieres, 1):
            response += f"{i}. **{filiere['nom']}**\n"
            response += f"   📍 {filiere['etablissement_nom']}\n"
            response += f"   ⏱️ {filiere['duree']} | 💰 {filiere['frais_inscription']}\n"
            response += f"   {filiere['description'][:100]}...\n\n"
        
        response += "Dites-moi laquelle vous intéresse pour plus de détails !"
        
        dispatcher.utter_message(text=response)
        return []

class ActionInformationsPratiques(Action):
    def name(self) -> Text:
        return "action_informations_pratiques"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dates = db.get_dates_importantes()
        documents = [doc for doc in db.get_documents_requis() if doc['obligatoire']]
        
        response = "ℹ️ **Informations Pratiques - Préinscription**\n\n"
        
        response += "**📅 Calendrier académique 2024-2025 :**\n"
        for date in dates:
            response += f"• {date['evenement']} : {date['date_debut']}"
            if date['date_fin'] and date['date_fin'] != date['date_debut']:
                response += f" au {date['date_fin']}"
            response += "\n"
        
        response += "\n**📄 Documents obligatoires :**\n"
        for doc in documents:
            response += f"• {doc['type_document']}\n"
        
        response += "\n**💻 Plateforme :** http://preinscription.univ-douala.cm"
        response += "\n**📞 Support :** +237 233 40 20 00"
        response += "\n**📧 Email :** preinscription@univ-douala.cm"
        
        response += "\n\n**⚠️ Important :** Ces informations peuvent changer, consultez toujours le site officiel."
        
        dispatcher.utter_message(text=response)
        return []

class ActionFilieresEtablissement(Action):
    def name(self) -> Text:
        return "action_filieres_etablissement"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        etablissement_nom = next(tracker.get_latest_entity_values("etablissement"), None)
        
        if not etablissement_nom:
            dispatcher.utter_message(text="De quel établissement souhaitez-vous connaître les filières ?")
            return []
        
        # Chercher l'établissement
        etablissements = db.get_etablissements()
        etablissement_trouve = None
        
        for etab in etablissements:
            if etablissement_nom.lower() in etab['nom'].lower():
                etablissement_trouve = etab
                break
        
        if not etablissement_trouve:
            dispatcher.utter_message(text=f"Je n'ai pas trouvé l'établissement '{etablissement_nom}'. Voici la liste des établissements disponibles :")
            return [FollowupAction("action_liste_etablissements")]
        
        # Récupérer les filières de cet établissement
        filieres = db.get_filieres_by_etablissement(etablissement_trouve['id'])
        
        if not filieres:
            dispatcher.utter_message(text=f"L'établissement {etablissement_trouve['nom']} ne propose pas encore de filières dans notre base de données.")
            return []
        
        response = f"🎓 **Filières de {etablissement_trouve['nom']}**\n\n"
        
        # Séparer filières professionnelles et classiques
        filieres_pro = [f for f in filieres if f['type'] == 'professionnelle']
        filieres_classiques = [f for f in filieres if f['type'] == 'classique']
        
        if filieres_pro:
            response += "🎯 **Filières Professionnelles**\n"
            for filiere in filieres_pro:
                response += f"• {filiere['nom']} ({filiere['duree']}) - {filiere['frais_inscription']}\n"
            response += "\n"
        
        if filieres_classiques:
            response += "📚 **Filières Classiques**\n"
            for filiere in filieres_classiques:
                response += f"• {filiere['nom']} ({filiere['duree']}) - {filiere['frais_inscription']}\n"
            response += "\n"
        
        response += f"💼 *Total : {len(filieres)} filière(s)*\n"
        response += f"📞 Contact : {etablissement_trouve['contact']}\n"
        response += f"🌐 Site : {etablissement_trouve['site_web']}"
        
        dispatcher.utter_message(text=response)
        return [SlotSet("dernier_etablissement", etablissement_trouve['nom'])]

class ActionListeEtablissements(Action):
    def name(self) -> Text:
        return "action_liste_etablissements"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        etablissements = db.get_etablissements()
        
        if not etablissements:
            dispatcher.utter_message(text="Je n'ai pas pu récupérer la liste des établissements pour le moment.")
            return []
        
        # Construire une réponse structurée
        response = "🏛️ **Établissements de l'Université de Douala**\n\n"
        
        for etab in etablissements:
            response += f"**• {etab['nom']}** ({etab['type']})\n"
            response += f"  _{etab['description']}_\n"
            
            # Ajouter les filières pour cet établissement
            filieres = db.get_filieres_by_etablissement(etab['id'])
            if filieres:
                response += f"  📚 {len(filieres)} filière(s) disponible(s)\n"
            
            if etab['contact']:
                response += f"  📞 {etab['contact']}\n"
            if etab['site_web']:
                response += f"  🌐 {etab['site_web']}\n"
            
            response += "\n"
        
        response += "💡 *Pour voir les filières d'un établissement spécifique, dites-moi son nom !*"
        
        dispatcher.utter_message(text=response)
        return []