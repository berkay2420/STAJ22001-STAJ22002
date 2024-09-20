from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from pymongo import MongoClient
from rasa_sdk.events import Restarted, SlotSet
from rasa_sdk.types import DomainDict
import re
from LLM_integration.responseGenerator import generate_Out_Of_Scope_Response, generate_suggestion_response


ATTEMPT_LIMIT=3


class ActionRestart(Action):
    def name(self) -> Text:
        return "action_restart"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
    
        return [Restarted()]
    


class ValidateSubmitUserMessageForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_submit_user_message_form"
    
    def is_valid_email(self, email: str) -> bool:
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(regex, email) is not None

    def validate_email(
            self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate user email address"""

        email = slot_value  
        print(f"Extracted email: {email}")
        
        return {"email": email}
    
    def validate_email_confirmation(
            self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Ask user for email confirmation"""

        email_confirmation = slot_value  
        print(f"Users anser to email confirmation: {email_confirmation}")

        email = tracker.get_slot('email')
        num_user_attempts = tracker.get_slot('num_user_attempts') or 0
        print(f"User Attempts So far:{num_user_attempts}") 
        
        if email_confirmation=="Yes":
            if self.is_valid_email(email):
                return {"email_confirmation": email_confirmation}
            else:
                dispatcher.utter_message(text="Geçersiz bir adres girdiniz lütfen tekrar deneyiniz")
                num_user_attempts += 1
                print(f"User Attempts So far:{num_user_attempts}") 
                if num_user_attempts >= ATTEMPT_LIMIT:
                        dispatcher.utter_message(text="Çok fazla yanlış adres girdiniz konuşma yeniden başlatılıyor. Lütfen daha sonra yeniden deneyiniz")
                        return { "requested_slot": None}
                
                return {"email_confirmation": None,"email": None,"num_user_attempts":num_user_attempts}
        else:
            dispatcher.utter_message(text="LÜtfen eposta adresinizi yeniden giriniz")
            return {"email_confirmation": None,"email": None}
            
    
    def validate_user_message(
            self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate users message """

        user_message=slot_value
        print(f"users message: {user_message}")
        
        return {"user_message": user_message}
    
    


class ActionGenerateOutOfScopeResponse(Action):
    def name(self) -> Text:
        return "action_generate_out_of_scope_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        latest_message = tracker.latest_message['text']
        
        response = generate_Out_Of_Scope_Response(latest_message)

        dispatcher.utter_message(text=response)

        return []

class ActionGeneratSuggestionResponse(Action):
    def name(self) -> Text:
        return "action_generate_suggestion_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        latest_message = tracker.latest_message['text']
        
        response = generate_suggestion_response(latest_message)

        dispatcher.utter_message(text=response)

        return []
