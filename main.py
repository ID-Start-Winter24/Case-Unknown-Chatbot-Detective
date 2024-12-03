import os
import time
import gradio as gr
import base64
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, PromptTemplate
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.chat_engine.types import ChatMode

from theme import CustomTheme


path_modulhandbuch = "./dokumente"
path_persist = os.path.join(path_modulhandbuch, "persist")

Settings.llm = OpenAI(temperature=0.1, model="gpt-4o-mini")

if not os.path.exists(path_persist):
    documents = SimpleDirectoryReader(path_modulhandbuch).load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=path_persist)
else:
    storage_context = StorageContext.from_defaults(persist_dir=path_persist)
    index = load_index_from_storage(storage_context)


template = (
    "We have provided context information below. \n"
    "---------------------\n"
    "{context_str}"
    "\n---------------------\n"
    "Given only this information and without using ur general knowledge, please answer the question in the style of an aggressive detective and always answer in english. Guide the player through the story. Maximum 5 sentences answers. : {query_str}\n"
)
qa_template = PromptTemplate(template)
query_engine = index.as_query_engine(streaming=True, text_qa_template=qa_template)


chat_engine = index.as_chat_engine(
 chat_mode=ChatMode.CONDENSE_PLUS_CONTEXT,
 system_prompt=template,
 streaming=True,
)

def response(message, history):
    chat_history = []
    for i, msg in enumerate(history):
        if i % 2 == 0:
            history_message = ChatMessage(role=MessageRole.ASSISTANT, content=msg["content"])
        else:
            history_message = ChatMessage(role=MessageRole.USER, content=msg["content"])
        chat_history.append(history_message)
    streaming_response = chat_engine.stream_chat(message, chat_history=chat_history)

    answer = ""
    for text in streaming_response.response_gen:
        time.sleep(0.05)
        answer += text
        yield answer


theme = CustomTheme()

def main():
    with open("./avatar_images/background_intergorationroom.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    # Create dynamic CSS for the background
    custom_css = f"""
    .gradio-container {{
        background: url("data:image/png;base64,{encoded_string}") !important;
        background-size: cover !important;
        background-position: center !important;
        max-width: 100% !important;
        height: auto !important;
    }}
    """
    chatbot = gr.Chatbot(
        value=[{"role": "assistant", "content": "Well, well... look who decided to wake up."}],
        type="messages",
        show_label=False,
        elem_id="CHATBOT"

    )
    input_box = gr.Textbox(
        label="Type a message...",
        elem_id="USER_INPUT"  # Связь с CSS-идентификатором
    )

    
    chatinterface = gr.ChatInterface(
    fn=response,
    chatbot=chatbot,
    type="messages",
    theme=theme,
    css=custom_css,
    css_paths="./style.css"  # Path to your custom CSS
    )
    
    custom_css = f"""
        .gradio-container {{
            background: url("data:image/png;base64,{encoded_string}") !important;
            background-size: cover !important;
            background-position: center !important;
            max-width: 30% !important;
            height: auto !important;
        }}
        #CHATBOT {{
            width: 30%;
            margin-left: 70%;
            margin-top: 10%;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
            border-radius: 8px;
        }}
        #component-4 {{
            background: #ecebeb !important;
            width: 30% !important;
            margin-left: 70% !important;
            margin-top: 10% !important;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2) !important;
            border-radius: 8px !important;
        }}
    """


    chatinterface.launch(
        inbrowser=True

)





if __name__ == "__main__":
    main()
