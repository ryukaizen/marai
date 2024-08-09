import React, { useEffect, useRef, useState } from "react";
import { IndicTransliterate, Language } from "@ai4bharat/indic-transliterate";
import './App.css';

interface Message {
    name: string;
    img: string;
    side: string;
    text: string;
    timestamp: string;
  }

  const App: React.FC = () => {

  const toggleTransliteration = () => {
    setTransliterationEnabled(!transliterationEnabled);
  };
  
  const translations = {
    'marathi': {
      'headline': 'मराठी भाषेकरिता संभाषणात्मक बुद्धिमत्ता',
      'chatbot_name': 'मराठी ए.आय.',
      'welcome_message': 'नमस्कार, आपले स्वागत आहे! कृपया मला आपला संदेश पाठवा. 😄',
      'transliteration': 'लिप्यंतरण (इंग्रजी-मराठी)',
      'inputbox': 'आपला संदेश द्या...'
    },
    
    'english': {
      'headline': 'Conversational AI for the Marathi Language',
      'chatbot_name': 'MarAI',
      'welcome_message': 'Hi, welcome! Go ahead and send me a message. 😄',
      'transliteration': 'Transliteration (en-mr)',
      'inputbox': 'Ask anything...'
    }
  };

  let currentLanguage = 'marathi'; 
  
  const toggleLanguage = () => {
    currentLanguage = currentLanguage === 'english' ? 'marathi' : 'english';
    updateUI();
  }
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  const updateUI = () => {    
    const langContent = translations[currentLanguage as keyof typeof translations];
    const msgerHeaderTitle = document.querySelector('.msger-header-title');
    const msgText = document.querySelector('.msg-text');
    const msgInfoChatbotName = document.querySelector('.msg-info-chatbot-name');
    const msgerHeaderToggleLabel = document.querySelector('.msger-header-toggle label');
    const msgerInput = document.querySelector('.msger-inputarea .msger-input');
    
    if (msgerHeaderTitle) {
        msgerHeaderTitle.innerHTML = langContent['headline'];
    }

    if (msgText) {
        msgText.textContent = langContent['welcome_message'];
    }

    if (msgInfoChatbotName) {
        msgInfoChatbotName.textContent = langContent['chatbot_name'];
    }

    if (msgerHeaderToggleLabel) {
        msgerHeaderToggleLabel.textContent = langContent['transliteration'];
    }

    if (msgerInput) {
        msgerInput.setAttribute('placeholder', langContent['inputbox']);

    }
  }

  updateUI(); 

  const [text, setText] = useState("");
  const [lang] = useState<Language>("mr");
  const [transliterationEnabled, setTransliterationEnabled] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const msgerChatRef = useRef<HTMLDivElement>(null);

  const BOT_IMG = "../public/assets/images/MarathiWoman.svg";
  // const PERSON_IMG = "User.svg";
  const BOT_NAME = "मराठी ए.आय.";

  const appendMessage = (name: string, img: string, side: string, text: string) => {
    const options: Intl.DateTimeFormatOptions = { hour: 'numeric', minute: 'numeric', hour12: true };
    const newMessage: Message = {
      name,
      img,
      side,
      text,
      timestamp: new Date().toLocaleTimeString('en-US', options),
    };
    setMessages(prevMessages => [...prevMessages, newMessage]);
  };

  // const [setIsTyping] = useState(false);


  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (text.trim() !== "") {
      appendMessage("", "", "right", text);
      setText("");
  
      try {
        const response = await fetch('http://0.0.0.0:5005/webhooks/rest/webhook', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: text }), 
        });
  
        if (!response.ok) {
          throw new Error('Failed to fetch response'); 
        }
  
        const data = await response.json();
        console.log(data)
        const rasaResponseText = data[0]?.text; 
        appendMessage(BOT_NAME, BOT_IMG, "left", rasaResponseText);
      } catch (error) {
        console.error('Error in handleSubmit:', error);
      } 
    }
  };

  useEffect(() => {
    updateUI();
  }, [currentLanguage, updateUI]);

  useEffect(() => {
    if (msgerChatRef.current) {
      msgerChatRef.current.scrollTop = msgerChatRef.current.scrollHeight;
    }

  }, [messages]);
  
  
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSubmit(e as unknown as React.FormEvent<HTMLFormElement>);
      }
    };
  
    const textareaElement = textareaRef.current;
    if (textareaElement) {
      textareaElement.addEventListener("keydown", handleKeyDown);
    }
  
    return () => {
      if (textareaElement) {
        textareaElement.removeEventListener("keydown", handleKeyDown);
      }
    };
  }, [handleSubmit]);

  return (
          <div className="overall">
              <section className="msger">
                <header className="msger-header">

                  <img src="assets/images/MarAI-transparent.png" alt="Marathi AI" width="348" height="77"/>

                  <div className="msger-header-title">
                    Conversational AI for Marathi Language
                  </div>

                  {/* <div className="msger-header-dropdown">
                    <select id="modelSelect" onChange={selectModel}>
                      <option value="model1">Rasa Local</option>
                      <option value="model2">External</option>
                    </select>
                  </div> */}


                  <div className="msger-header-buttons">
                    <button onClick={toggleLanguage} title="Toggle UI Language">
                      <img src="assets/images/language-button.svg" alt="Language" width="50" height="50" draggable="false"/>
                    </button>
                  </div>

                </header>

                <main className="msger-chat" ref={msgerChatRef}>
                <div className="msg left-msg">
                  {/*<div className="msg-img-chatbot"></div>*/}
                  <div className="msg-bubble">
                    <div className="msg-info">
                      <div className="msg-info-chatbot-name">मराठी ए.आय.</div>
                      <div className="msg-info-time"></div>
                    </div>
                    
                    <div className="msg-text">
                    Hi, welcome! Go ahead and send me a message. 😄
                    </div>
                   </div>
                </div>
                  {messages.map((message, index) => (
                    <div key={index} className={`msg ${message.side}-msg`}>
                      
                      <div className="msg-bubble">
                        <div className="msg-info">

                          <div className="msg-info-chatbot-name">
                            {message.name}
                          </div>
                    
                        </div>

                        <div className="msg-text">
                          {message.text}
                          </div>

                          <div className="msg-info-time">
                            {message.timestamp}
                          </div>

                      </div>

                    </div>
              
                  ))} 
            
                </main>
            
                <form className="msger-inputarea" id="inputContainer" onSubmit={handleSubmit}>
              
                <div className="msger-header-toggle">
                  
                  <label htmlFor="transliterationToggle">Transliteration (en-mr):</label>            
                  
                  <input type="checkbox" id="transliterationToggle" checked={transliterationEnabled}  onChange={toggleTransliteration}/>

                  <IndicTransliterate renderComponent={(props) => {
                      return <input {...props} className="msger-input" id="textInput" placeholder="Start typing..." wrap="hard" rows="5"></input> 
                      }
                    }
                    value={text}

                    onChangeText={(text) => {
                        setText(text);
                      }
                    }

                    lang={lang}

                    enabled={transliterationEnabled}
                  
                  />

                  </div>
              
                  <button type="submit" className="msger-send-btn" title="Send">
                
                    <img src="assets/images/send-button.png" alt="Send" draggable="false"/>
              
                  </button>
        
                </form>

              </section>

          </div>
  );
};

export default App;