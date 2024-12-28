import os
import time
import gradio as gr
import base64
import random
#from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, PromptTemplate
#from llama_index.llms.openai import OpenAI
#from llama_index.core import Settings
#from llama_index.core.llms import ChatMessage, MessageRole
#from llama_index.core.chat_engine.types import ChatMode
from openai import OpenAI
from theme import CustomTheme
import Blackwell
#from openai import OpenAI
client = OpenAI()


message_counter = 15
path_modulhandbuch = "./dokumente"
path_persist = os.path.join(path_modulhandbuch, "persist")
"""
Settings.llm = OpenAI(temperature=0.1, model="gpt-4o-mini")

    if not os.path.exists(path_persist):
    documents = SimpleDirectoryReader(path_modulhandbuch).load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=path_persist)
else:
    storage_context = StorageContext.from_defaults(persist_dir=path_persist)
    index = load_index_from_storage(storage_context)
"""

template = (
    "We have provided context information below. \n"
    "---------------------\n"
    "{context_str}"
    "\n---------------------\n"
    "Given only this information and without using your general knowledge, "
    "please answer the question in the style of an aggressive detective and always answer in English. "
    "Guide the player through the story. Maximum 5 sentences answers: {query_str}\n"
)
"""""
qa_template = PromptTemplate(template)
query_engine = index.as_query_engine(streaming=True, text_qa_template=qa_template)


chat_engine = index.as_chat_engine(
    chat_mode=ChatMode.CONDENSE_PLUS_CONTEXT,
    system_prompt=template,
    streaming=True,
)
"""
qa_template = {"template": template}




def visible():
    text_area = gr.TextArea(value="TEXTAREA", visible=True)
    return text_area

def response(history):
    chat_history = []
    for i, msg in enumerate(history):
        if i % 2 == 0:
            history_message = {"role": "assistant", "content": msg["content"]}
        else:
            history_message = {"role": "user", "content": msg["content"]}
        chat_history.append(history_message)
        
    # Streaming der Antwort mit der Chat-Engine
    message = history[-1]["content"]
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        stream=True,
        messages=[
        
            {   "role": "system", 
                "content": Blackwell.SystemPrompt},
            {   "role": "user",
                "content": message}
        ]
   
        )
    #streaming_response = chat_engine.stream_chat(message, chat_history=chat_history)
    history.append({"role": "assistant", "content": ""})
    for chunk in completion:
        text = ""
        if chunk.choices and chunk.choices[0].delta.content:
            text = chunk.choices[0].delta.content
#    # Verzögerung von 50 ms pro Antwortteil, um das Streaming zu simulieren
        time.sleep(0.05)
        history[-1]["content"] += text
        yield history  # Gibt die Antwort in Teilen zurück

def user(message, history):
    global message_counter
    if message_counter > 0:
        message_counter -= 1
        return "", history + [{"role": "user", "content": message}], f"{message_counter} messages left"
    else:
        return "", history + [{"role": "user", "content": message}], f"game over"

        
is_visible_up = None
is_visible_mid = None
is_visible_down = None
def show_hint(history):
    global is_visible_up
    global is_visible_mid
    global is_visible_down
    if len(history) == 3:
        hint_index = random.randint(1, 4)
        is_visible_up = f"./hint_pics/hint_{hint_index}.jpg"
    elif len(history) == 5:
        hint_index = random.randint(4, 7)
        is_visible_mid = f"./hint_pics/hint_{hint_index}.jpg"    
    elif len(history) == 7:
        hint_index = random.randint(7, 10)
        is_visible_down = f"./hint_pics/hint_{hint_index}.jpg"
    
    up_image = gr.Image(value=is_visible_up, elem_classes="fixed-image-up", show_label= False, show_download_button= False, visible=False if not is_visible_up else True)
    mid_image = gr.Image(value=is_visible_mid, elem_classes="fixed-image-mid", show_label= False, show_download_button= False, visible=False if not is_visible_mid else True)
    down_image = gr.Image(value=is_visible_down, elem_classes="fixed-image-down", show_label= False, show_download_button= False, visible=False if not is_visible_down else True)
    
    return up_image, mid_image, down_image

def change_detective_picture(history):
    if len(history) % 2 != 0:
        detective_image = "avatar_images/Detective_still.png"
    else: 
        detective_image = "avatar_images/Detective_animated.gif"
    return detective_image

    

def main():
    with open("./avatar_images/background_b2_wide.jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    with open("./startpage/mouse_o.png", "rb") as image_file:
        encoded_mouse_o = base64.b64encode(image_file.read()).decode()


    theme = CustomTheme()

    # Dynamic CSS for background
    custom_css = f"""
    .gradio-container {{
        background: url("data:image/png;base64,{encoded_string}") !important;
        background-size: cover !important;
        background-position: center !important;
    }}
    body, img {{
    cursor: url('data:image/png;base64,{encoded_mouse_o}') 32 52, auto !important;
    }}
    """


    with gr.Blocks(css=custom_css, css_paths="./style.css", theme=theme, fill_height=True) as chatinterface:
        with gr.Row(equal_height=True):  # Equal_width argument
            with gr.Column(scale=2): # First column for hints
                with gr.Row(elem_classes="logo-box", visible=True, max_height="6.5vw"):
                    logo = gr.Image(value="./avatar_images/logo.png", elem_classes="logo", show_label= False, show_download_button= False, container=False, show_fullscreen_button=False)
                with gr.Row(elem_classes="white-box", visible=True, min_height="34vw" ):
                    gr.Markdown("## Here are your tips:", elem_classes="heading"),
                    up_image = gr.Image(value="./hint_pics/hint_3.jpg", elem_classes="fixed-image-up", show_label= False, show_download_button= False, visible=False)
                    mid_image = gr.Image(value="./hint_pics/hint_6.jpg", elem_classes="fixed-image-mid", show_label= False, show_download_button= False, visible=False)
                    down_image = gr.Image(value="./hint_pics/hint_7.jpg", elem_classes="fixed-image-down", show_label= False, show_download_button= False, visible=False)
                   
            with gr.Column(scale=3):  # Second column for picture of detectiv, timer and scale
                timer = gr.Textbox(

                    lines=1, 
                    value=f"{message_counter} messages left",
                    show_label=False,
                    container=False,
                    elem_classes="timer"
                    )
                scale = gr.Textbox(value="scale", show_label=False, container=False, elem_classes="scale")
                picture_of_detectiv = gr.Image(
                    value="avatar_images/Detective_still.png", 
                    show_label=False, 
                    show_download_button=False, 
                    show_fullscreen_button=False,
                    height="38vw",
                    container=False,
                    )

            with gr.Column(scale=2):  # Third column for chatbot and input box
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

                input_box.submit(user, inputs=[input_box, chatbot], outputs=[input_box,chatbot, timer]).then(change_detective_picture, chatbot, picture_of_detectiv).then(response, inputs=[chatbot], outputs=[chatbot]).then(change_detective_picture, chatbot, picture_of_detectiv).then(show_hint, chatbot, [up_image, mid_image, down_image])
    chatinterface.launch(inbrowser=True,show_api=False)


if __name__ == "__main__":
    main()