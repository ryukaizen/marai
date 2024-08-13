# MarAI: Conversational AI for Marathi

<div align="center">
  <img src="https://i.imgur.com/Xb37sNN.jpeg" alt="MarAI"/>

  ![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-red.svg)
  [![Rasa](https://img.shields.io/badge/Rasa-3.x-purple)](https://rasa.com/)
  [![React](https://img.shields.io/badge/React-17.x-cyan)](https://reactjs.org/)
  ![Python](https://img.shields.io/badge/python-3.10-green)
  ![scikit-learn](https://img.shields.io/badge/scikit--learn-v1.3.0-orange)
  ![Transformers](https://img.shields.io/badge/transformers-v4.33.2-blueviolet)
  ![inltk](https://img.shields.io/badge/inltk-v0.9.0-brightgreen)
  ![GitHub repo size](https://img.shields.io/github/repo-size/ryukaizen/marai)
  
</div>

## 📖 Overview

MarAI is an conversational AI designed specifically for the Marathi language. It combines the power of [Rasa](https://rasa.com/docs/rasa/) for intent recognition and dialogue management with fallback mechanisms including [TF-IDF](https://en.wikipedia.org/wiki/Tf-idf) based retrieval and Google Search integration.

### 🌟 Features

- **Rasa-powered Conversations**: Primary dialogue management using Rasa.
- **TF-IDF Fallback**: Corpus-based retrieval for handling out-of-scope queries.
- **googlesearch-python Integration**: Content retrieval focused on Marathi Wikipedia.
- **Response Paraphrasing**: Natural-sounding responses using multilingual paraphrase generation.
- **React-based Frontend**: A sweet user interface. 

**Important Note**: MarAI is not a transformer-based large language model (LLM). Instead, it uses a combination of rule-based systems, machine learning techniques, and retrieval-based methods to provide responses. While it can engage in Marathi conversations and provide information, its capabilities are different from and more limited than those of large language models like GPT-3 or BERT. Hence, it is not always accurate or contextually appropriate.

> **Future Plans**:
We initially considered implementing a quantized text generation model, specifically fine-tuned on a Marathi corpus. However, due to hardware limitations, time constraints, and resource considerations, we opted for our current approach. In the future, we plan to enhance MarAI by replacing the current fallback mechanism with a LLM for Marathi, such as [Misal](https://smallstep.ai/misal). This upgrade would significantly improve the system's response generation capabilities and contextual understanding.

## 💡 How It Works

1. User input is first processed by the Marathi Rasa model, specifically trained for handling basic, day-to-day conversations in Marathi.
2. If Rasa fails to handle the query, the TF-IDF based retriever searches the local corpus.
3. If relevant content is found in the local corpus, it'll be sent to the user.
4. If no suitable content is found, a Google search is performed, filtering for Marathi Wikipedia articles.
5. The retrieved content is saved to the corpus for future use.
6. Responses from Marathi Rasa model are paraphrased using AI4Bharat's MultiIndicParaphraseGeneration for natural language output.

> Note: Currently we are NOT rephrasing any response from TF-IDF fallback mechanism, you can modify the ```actions.py``` file if you want to rephrase the content fetched from Wikipedia or the local corpus.

## 🚀 Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/ryukaizen/marai.git
   cd marai
   ```

2. **Set up the environment**

   ```bash
   docker-compose up --build
   ```

3. **Access the application**

   Open your browser and navigate to `http://localhost:3000`

## 🏗️ Project Structure

```
marai
├── marai/               # Rasa project files
│   ├── actions/         # Custom actions including TF-IDF retrieval
│   ├── data/            # Training data (NLU, stories, rules)
│   └── models/          # Trained Rasa models
├── public/              # Static assets for the React app
├── src/                 # React application source code
└── docker-compose.yml   # Docker composition file
```

## 🚂 Training and Running Rasa

To train and run the Rasa model:

1. **Train the model**:
   ```bash
   rasa train
   ```

2. **Test the model in shell mode**:
   ```bash
   rasa shell
   ```

3. **Run Rasa as an API (for frontend interaction)**:
   ```bash
   rasa run --enable-api --cors "*"
   ```

## 📚 Customizing the Corpus

You can add your own data to the corpus by adding `.txt` files to the `marai/actions/corpora` directory. The retriever will automatically include these files in its knowledge base.

## 🔧 Tuning the Retrieval Mechanism

The retrieval mechanism can be fine-tuned by adjusting the conditions in the `is_result_relevant` function in `retriever.py`. Key parameters to consider:

- `relevance_score`: Cosine similarity threshold (currently 0.2)
- `term_match_percentage`: Percentage of query terms that should match the result (currently 0.3)
- `name_similarity`: Fuzzy matching threshold for document names (currently 0.8)

## 🧪 Testing the Paraphraser Model

To experiment with AI4Bharat's paraphraser model, refer to the `inference_test.py` file. This script allows you to test and evaluate the performance of the paraphrasing functionality.

## 🔄 Paraphraser Function

The `rephrase` function in `actions.py` uses [AI4Bharat](https://github.com/AI4Bharat)'s model for paraphrasing:

```python
def rephrase(self, message):
    inp = self.tokenizer(message + " </s> " + self.lang_id, add_special_tokens=False, return_tensors="pt", padding=True).input_ids
    model_output = self.model.generate(
        inp,
        use_cache=True,                  # Enables caching of key/value pairs for faster decoding
        no_repeat_ngram_size=2,          # Prevents repetition of 2-gram phrases in the output
        encoder_no_repeat_ngram_size=2,  # Prevents repetition of 2-gram phrases in the encoder
        num_beams=2,                     # Number of beams for beam search. Higher values = more diverse outputs but slower
        max_length=30,                   # Maximum length of the generated sequence
        min_length=10,                   # Minimum length of the generated sequence
        early_stopping=True,             # Whether to stop the beam search when at least num_beams sentences are finished per batch
        pad_token_id=self.pad_id,        # Token ID for padding
        bos_token_id=self.bos_id,        # Token ID for beginning of sentence
        eos_token_id=self.eos_id,        # Token ID for end of sentence
        decoder_start_token_id=self.tokenizer._convert_token_to_id_with_added_voc(self.lang_id)  # Start token ID for the decoder
    )
    return self.tokenizer.decode(model_output[0], skip_special_tokens=True, clean_up_tokenization_spaces=False)
```

Adjust these parameters to fine-tune the paraphrasing output.

## 📁 Rasa-related Files

Rasa uses several configuration files to define the behavior of the chatbot:

1. **data/nlu.yml**: Contains training data for the natural language understanding (NLU) model. This includes example user utterances and their corresponding intents and entities.

2. **data/stories.yml**: Defines conversation flows, showing how the bot should respond to different sequences of user intents.

3. **data/rules.yml**: Contains rules for specific conversation patterns that should always be followed, regardless of the conversation history.

4. **domain.yml**: Defines the universe of the chatbot, including intents, entities, slots, actions, and responses.

5. **config.yml**: Configures the NLU pipeline and policy ensemble for the Rasa model.

6. **endpoints.yml**: Specifies the URLs for the different endpoints the bot can use.

7. **credentials.yml**: Contains credentials for external services the bot might use.

To customize the bot's behavior, you'll primarily work with `nlu.yml`, `stories.yml`, `rules.yml`, and `domain.yml`.

## 👥 Contributing

Whether big or small, contributions are always warmly welcomed!

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

We gratefully acknowledge the use of [AI4Bharat](https://github.com/AI4Bharat)'s technologies in this project:

1. The MultiIndicParaphraseGeneration model for natural language generation. Please cite the following paper when using or referencing this work:

```bibtex
@inproceedings{Kumar2022IndicNLGSM,
  title={IndicNLG Suite: Multilingual Datasets for Diverse NLG Tasks in Indic Languages},
  author={Aman Kumar and Himani Shrotriya and Prachi Sahu and Raj Dabre and Ratish Puduppully and Anoop Kunchukuttan and Amogh Mishra and Mitesh M. Khapra and Pratyush Kumar},
  year={2022},
  url = "https://arxiv.org/abs/2203.05437"
}
```

2. The "[@ai4bharat/indic-transliterate](https://github.com/AI4Bharat/indic-transliterate-js)" React library, which is used for real-time quick transliteration from English to Marathi on the text input. This feature greatly enhances the user experience for those more comfortable typing in English.

We would also like to thank the [smallstep.ai](https://smallstep.ai) team for giving valuable insights on how to proceed with this project.

---
<div align="center">
  <p style="font-size: 1.2em;">
    <i>लाभले आम्हास भाग्य बोलतो <b>मराठी</b></i><br>
    <i>जाहलो खरेच धन्य ऐकतो <b>मराठी</b></i><br>
    <i>धर्म , पंथ , जात एक जाणतो <b>मराठी</b></i><br>
    <i>एवढ्या जगात माय मानतो <b>मराठी</i></b>
  </p>
</div>

<div align="center">
  Made with ❤️ for the Marathi-speaking community
</div>
