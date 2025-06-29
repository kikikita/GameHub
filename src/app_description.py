import gradio as gr

def app_description():
    with gr.Column():
        gr.Markdown("""
            # 🎮 LLMGameHub - Your Personal Visual Novel
            
            **Craft your own adventures with an AI-powered game master!**
            
            🎥 [Video Demo](https://youtu.be/pQfP9lA1QUM)
        """)
        gr.HTML("""<iframe width="560" height="315" src="https://www.youtube.com/embed/pQfP9lA1QUM" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen=""></iframe>""")
        gr.Markdown("""
            This application is an interactive storytelling experience where you are the author. Create a unique world, design your character, and let our AI agent weave a narrative tailored to your choices. It's a blend of a game constructor and a visual novel, powered by generative AI.
            
            ## 🎯 Key Features
            - **🤖 AI Game Master**: An intelligent agent that generates a dynamic story with branching narratives based on your inputs.
            - **🎨 World Building**: Define your own game setting, from fantasy realms to sci-fi dystopias.
            - **👤 Character Creation**: Customize your protagonist's name, age, background, and personality.
            - **🎭 Genre Selection**: Choose from a variety of genres to set the tone of your story (e.g., Fantasy, Sci-Fi, Mystery).
            - **🖼️ Visual & Audio Experience**: The AI generates images and background music to accompany the scenes, immersing you in the story.
            - **✍️ Interactive Choices**: Guide the narrative by selecting from AI-generated options or writing your own custom actions.
            
            ## 🛠️ How It Works
            
            1.  **Construct Your World**: Use the forms to describe the setting and your character.
            2.  **Choose a Genre**: Select the style of your adventure.
            3.  **Start the Game**: The AI will generate the opening scene based on your setup.
            4.  **Make Your Choices**: Interact with the story by choosing from a list of actions or writing your own.
            5.  **Experience Your Story**: Watch as the AI dynamically creates a unique story with text and images just for you.
            
            ## 📊 Agent Demo
            This Space showcases **intelligent agent capabilities for creative writing**:
            - Dynamic story and scene generation.
            - Contextual understanding of player choices.
            - AI-powered generation of text, images, and music.
            
            ---
    
            ## 🤖 Powered by the **Gradio Agents & MCP Hackathon 2025**
            Created as an entry for the official [Gradio Agents & MCP Hackathon](https://huggingface.co/Agents-MCP-Hackathon) – June 2-10 2025.
            """)
