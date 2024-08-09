from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from .tfidf.retriever import get_response
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class MBartParaphraser:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("ai4bharat/MultiIndicParaphraseGeneration", do_lower_case=False, use_fast=False, keep_accents=True)
        self.model = AutoModelForSeq2SeqLM.from_pretrained("ai4bharat/MultiIndicParaphraseGeneration")
        self.bos_id = self.tokenizer._convert_token_to_id_with_added_voc("<s>")
        self.eos_id = self.tokenizer._convert_token_to_id_with_added_voc("</s>")
        self.pad_id = self.tokenizer._convert_token_to_id_with_added_voc("<pad>")
        self.lang_id = "<2mr>"

    def rephrase(self, message):
        inp = self.tokenizer(message + " </s> " + self.lang_id, add_special_tokens=False, return_tensors="pt", padding=True).input_ids
        model_output = self.model.generate(
            inp,
            use_cache=True,
            no_repeat_ngram_size=2,
            encoder_no_repeat_ngram_size=2,
            num_beams=2,
            max_length=30,
            min_length=10,
            early_stopping=True,
            pad_token_id=self.pad_id,
            bos_token_id=self.bos_id,
            eos_token_id=self.eos_id,
            decoder_start_token_id=self.tokenizer._convert_token_to_id_with_added_voc(self.lang_id)
        )
        return self.tokenizer.decode(model_output[0], skip_special_tokens=True, clean_up_tokenization_spaces=False)

paraphraser = MBartParaphraser()

class ActionRephraseResponse(Action):
    def name(self) -> Text:
        return "action_rephrase_response"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        latest_intent = tracker.latest_message['intent'].get('name')
        utterance_name = f"utter_{latest_intent}"
        utterance = domain['responses'].get(utterance_name)

        if utterance:
            original_text = utterance[0]['text']
            
            rephrased_text = paraphraser.rephrase(original_text)
            
            dispatcher.utter_message(text=rephrased_text)
        else:
            dispatcher.utter_message(text="माफ करा, मी समजू शकलो नाही.")

        return []

class ActionDefaultFallback(Action):
    def name(self) -> str:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        latest_message = tracker.latest_message
        intent = latest_message['intent']['name']
        confidence = latest_message['intent']['confidence']
        print(f"\n\nIntent: {intent}, Confidence: {confidence}\n\n")
        user_message = tracker.latest_message.get('text', '')
        response = get_response(user_message)
        dispatcher.utter_message(text=response)
        return []