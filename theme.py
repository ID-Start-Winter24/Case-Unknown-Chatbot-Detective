from gradio.themes.base import Base


class CustomTheme(Base):
    def __init__(self):
        super().__init__()

        super().set(
            body_background_fill="#0f0f0f",
            input_background_fill="##fffffc",
        )