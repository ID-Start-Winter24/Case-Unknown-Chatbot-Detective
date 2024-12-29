import os
import time
import gradio as gr
import base64
import random
from openai import OpenAI
from theme import CustomTheme
import Blackwell

client = OpenAI()

message_counter = 2
persuasion_level = 5  # Start persuasion scale in the middle (0 to 10)
path_modulhandbuch = "./dokumente"
path_persist = os.path.join(path_modulhandbuch, "persist")

template = (
    "We have provided context information below. \n"
    "---------------------\n"
    "{context_str}"
    "\n---------------------\n"
    "Given only this information and without using your general knowledge, "
    "please answer the question in the style of an aggressive detective and always answer in English. "
    "Guide the player through the story. Maximum 5 sentences answers: {query_str}\n"
)

qa_template = {"template": template}



def update_persuasion(is_believed):
    global persuasion_level
    if is_believed:
        persuasion_level = min(10, persuasion_level + 1)
    else:
        persuasion_level = max(0, persuasion_level - 1)
    return persuasion_level

def evaluate_response(user_response):
    prompt = f"""
    You are a detective evaluating the suspect's response. Rate how convincing this statement is on a scale of 1 to 10:
    "{user_response}"
    Only respond with the number.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=1,
        temperature=0
    )
    score = int(response['choices'][0]['text'].strip())
    if score >= 7:
        return update_persuasion(is_believed=True)
    elif score <= 4:
        return update_persuasion(is_believed=False)
    return persuasion_level  # No change for neutral responses


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
        game_over_overlay = gr.HTML("""
        <div id='game_over_overlay'>
            <div id='game_over_message'>Game Over</div>
        </div>
        """, visible=True)
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

def show_ending():
    pass

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
        #game_over_overlay = gr.HTML("""
        #<div id='game_over_overlay'>
        #    <div id='game_over_message'>Game Over</div>
        #</div>
        #""", visible=False)  # Set visible=True for testing
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

                persuasion_display = gr.Markdown(value=f"Persuasion Level: {persuasion_level} / 10", show_label=False, container=True, elem_classes="persuasion_display")
                timer = gr.Markdown(
                    f"<p class='timer'>You have {message_counter} messages left</p>",
                    elem_classes="timer",
                    container=False
                    )                
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