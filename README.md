# Google ADK AI Agents

Two AI agents built with Google's Agent Development Kit (ADK) during the "Beyond Chatbots: Building AI Agents with Google ADK" workshop.

## Agents

### 1. Personal Assistant (`personal_assistant/`)
An assistant agent that can use tools to answer questions:
- **Google Search** for up-to-date information
- **Calculator** for arithmetic
- **Text Analyzer** for analyzing text

### 2. SmartStudy (`smartstudy/`)
A multi-agent study planner where several agents work together using **sequential**, **parallel** and **loop** workflows.

## How to Run

1. Clone the repo and go into the folder:
   ```bash
   git clone https://github.com/sunnybbaishnab/google-adk-agents
   cd <repo-name>
   ```

2. Create and activate a virtual environment, then install the dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey). Copy `.env.example` into **each** agent folder as `.env`, then put your key in both:
   ```bash
   cp .env.example personal_assistant/.env
   cp .env.example smartstudy/.env
   ```

4. Run an agent from the project root:
   ```bash
   adk run personal_assistant
   ```
   Or open the browser interface and choose an agent from the dropdown:
   ```bash
   adk web
   ```
