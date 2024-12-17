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
    "Given only this information and without using your general knowledge, "
    "please answer the question in the style of an aggressive detective and always answer in English. "
    "Guide the player through the story. Maximum 5 sentences answers: {query_str}\n"
)
qa_template = PromptTemplate(template)
query_engine = index.as_query_engine(streaming=True, text_qa_template=qa_template)


chat_engine = index.as_chat_engine(
    chat_mode=ChatMode.CONDENSE_PLUS_CONTEXT,
    system_prompt=template,
    streaming=True,
)

def visible():
    text_area = gr.TextArea(value="TEXTAREA", visible=True)
    return text_area


def response(history):
    chat_history = []
    for i, msg in enumerate(history):
        if i % 2 == 0:
            history_message = ChatMessage(role=MessageRole.ASSISTANT, content=msg["content"])
        else:
            history_message = ChatMessage(role=MessageRole.USER, content=msg["content"])
        chat_history.append(history_message)
    
    # Streaming der Antwort mit der Chat-Engine
    message = history[-1]["content"]
    streaming_response = chat_engine.stream_chat(message, chat_history=chat_history)
    history.append({"role": "assistant", "content": ""})
    for text in streaming_response.response_gen:
    #    # Verzögerung von 50 ms pro Antwortteil, um das Streaming zu simulieren
        time.sleep(0.05)
        history[-1]["content"] += text
        yield history  # Gibt die Antwort in Teilen zurück

def user(message, history):
    return "", history + [{"role": "user", "content": message}]


def main():
    with open("./avatar_images/background_intergorationroom.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()


    theme = CustomTheme()

    # Dynamic CSS for background
    custom_css = f"""
    .gradio-container {{
        background: url("data:image/png;base64,{encoded_string}") !important;
        background-size: cover !important;
        background-position: center !important;
    }}
    """

    # Layout
    with gr.Blocks(css=custom_css, css_paths="./style.css", theme=theme, fill_height=True) as chatinterface:
        with gr.Row(equal_height=True):  # No equal_width argument
            with gr.Column(): # First column for hints
                text_area = gr.TextArea(value="TEXTAREA", visible=False)  # First empty column

            with gr.Column():  # Second column for picture of detectiv, timer and scale
                timer = gr.Textbox(
                    lines=1, 
                    value=" messages left",
                    show_label=False,
                    container=False
                    )
                scale = gr.Textbox(lines=1, value="scale", show_label=False, container=False)
                picture_of_detectiv = gr.Image(
                    value="avatar_images/detective.jpeg", 
                    show_label=False, 
                    show_download_button=False, 
                    show_fullscreen_button=False,
                    height="38vw",
                    container=False
                    )
                

            with gr.Column():  # Third column for chatbot and input box
                chatbot = gr.Chatbot(
                    value=[{"role": "assistant", "content": "Well, well... look who decided to wake up."}],
                    type="messages",
                    show_label=False,
                    elem_id="CHATBOT",
                    height="42vw"
                )
                input_box = gr.Textbox(
                    show_label= False,
                    elem_id="USER_INPUT",
                    placeholder="Type your message here...",
                    interactive=True,
                    submit_btn=True
                )
                input_box.submit(user, inputs=[input_box, chatbot], outputs=[input_box,chatbot]).then(response, inputs=[chatbot], outputs=[chatbot])
    chatinterface.launch(inbrowser=True,show_api=False)

if __name__ == "__main__":
    main()

