import sys
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# created this just to test and experiment with parameters, not a part of prod

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
            use_cache=True,  # enables caching of key/value pairs for faster decoding
            no_repeat_ngram_size=2,  # prevents repetition of 2-gram phrases in the output
            encoder_no_repeat_ngram_size=2,  # prevents repetition of 2-gram phrases in the encoder
            num_beams=2,  # number of beams for beam search. Higher values = more diverse outputs but slower
            max_length=30,  # maximum length of the generated sequence
            min_length=10,  # minimum length of the generated sequence
            early_stopping=True,  # stops generation when all beam hypotheses reach the EOS token
            pad_token_id=self.pad_id,  # ID of the padding token
            bos_token_id=self.bos_id,  # ID of the beginning-of-sequence token
            eos_token_id=self.eos_id,  # ID of the end-of-sequence token
        )
        return self.tokenizer.decode(model_output[0], skip_special_tokens=True, clean_up_tokenization_spaces=False)

def main():
    paraphraser = MBartParaphraser()

    print("Welcome to the Marathi Paraphraser!")
    print("Enter Marathi text to paraphrase. Type 'exit' to quit.")

    while True:
        user_input = input("\nEnter Marathi text: ")
        
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        try:
            paraphrased_text = paraphraser.rephrase(user_input)
            print(f"\nOriginal text: {user_input}")
            print(f"Paraphrased text: {paraphrased_text}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
    

#  **** On current parameters **** 
# Welcome to the Marathi Paraphraser!
# Enter Marathi text to paraphrase. Type 'exit' to quit.

# Enter Marathi text: माफ करा मी समजू शकलो नाही

# Original text: माफ करा मी समजू शकलो नाही
# Paraphrased text: मला समजत नाही मला माफ कर..

# Enter Marathi text: 