---
title: Startup Compliance Agent
emoji: ⚡   
colorFrom: pink
colorTo: yellow
sdk: gradio
sdk_version: 5.23.1
app_file: app.py
pinned: false
tags:
- smolagents
- agent
- smolagent
- tool
- agent-course
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

This repo follows https://huggingface.co/learn/agents-course/en/unit1/tutorial


## Setup

Follow these steps to set up the environment:

1. **Create a virtual environment**:
    ```bash
    python -m venv .venv
    ```

2. **Activate the virtual environment**:
    - On Windows:
      ```bash
      .venv\Scripts\Activate
      ```
    - On macOS/Linux:
      ```bash
      source .venv/bin/activate
      ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt    
    ```

4. **Set up environment variables**:
    - Create a `.env` file in the project root directory
    - Add your API keys to the `.env` file:
    ```bash
    HF_API_KEY="your_huggingface_api_key_here"
    ```
    
    **To get a HuggingFace API key:**
    1. Go to [HuggingFace](https://huggingface.co/)
    2. Create an account or sign in
    3. Go to your profile settings
    4. Navigate to "Access Tokens"
    5. Create a new token with "read" permissions
    6. Copy the token and paste it in your `.env` file

    **To get an Anthropic API key:**
    1. Go to [Anthropic](https://console.anthropic.com/)    
    2. Create an account or sign in
    3. Go to your profile settings
    4. Navigate to "API Keys"
    5. Create a new key
    6. Copy the key and paste it in your `.env` file
    
    **Note**: Never commit your `.env` file to version control. It's already included in `.gitignore`.

5. Run app

```bash
python app.py --eval
```

6. Update the following files when iterating on the agent:

- `agent.json` - agent configuration file with models details and list of tools
- `prompts.yaml` - prompt templates file
- `tools/` - agent tools

## License

This project is for educational purposes only.
