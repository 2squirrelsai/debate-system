# CrewAI Agent Debate System - Setup Guide

## Requirements

Create a `requirements.txt` file with the following dependencies:

```
crewai==0.22.5
langchain-openai==0.0.5
openai==1.12.0
python-dotenv==1.0.0
```

## Installation Steps

1. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
Create a `.env` file in your project directory:
```
OPENAI_API_KEY=your_openai_api_key_here
```

4. **Run the system:**
```bash
python debate_system.py
```

## Key Features Implemented

### ✅ Agent Personalities
- **Skeptic Agent**: High IQ (140), analytical, condescending, challenges everything
- **Optimist Agent**: High IQ (135), enthusiastic, humorous, finds positive angles

### ✅ Conversation Recording
- Records subject, timestamp, agent name, response, and token count
- Saves to `agent_conversations.json`
- Provides conversation history and summaries

### ✅ Disagreement & Conflict
- Agents are designed to contradict each other
- Include mocking and dismissive comments
- Use evidence and counter-arguments

### ✅ Cost Optimization
- Uses GPT-3.5-turbo (fastest, cheapest model)
- Limited token responses (80-150 tokens per response)
- Efficient conversation recording

## Usage Examples

### Basic Usage
```python
from debate_system import DebateSystem

# Initialize
debate_system = DebateSystem("your-openai-api-key")

# Run a debate
debate_history = debate_system.run_debate("Climate change solutions", rounds=3)

# Get summary
summary = debate_system.get_debate_summary("Climate change solutions")
```

### Custom Subjects
```python
subjects = [
    "Cryptocurrency is the future of money",
    "Video games cause violence",
    "Working from home increases productivity"
]

for subject in subjects:
    debate_system.run_debate(subject, rounds=2)
```

## Customization Options

### Modify Agent Personalities
Edit the `agent_personalities` dictionary in the `DebateSystem` class:

```python
self.agent_personalities = {
    "agent1": {
        "role": "Your custom role",
        "goal": "Your custom goal", 
        "backstory": "Your custom backstory with IQ and response pattern",
        "max_tokens": 100
    }
}
```

### Add More Agents
Extend the system by adding more agents to the personalities dictionary and modifying the `create_agents()` method.

### Change Response Limits
Modify the `max_tokens` parameter in the ChatOpenAI initialization and agent backstories.

## File Structure
```
project/
├── debate_system.py          # Main system code
├── requirements.txt          # Dependencies
├── .env                     # Environment variables
├── agent_conversations.json # Recorded conversations (auto-generated)
└── README.md               # This file
```

## Expected Output Format

The system will output debates like this:

```
=== ROUND 1 ===
🤔 Skeptic: Your argument about AI creativity is fundamentally flawed. True creativity requires consciousness and emotional depth, which AI lacks. These systems merely recombine existing patterns - hardly the revolutionary breakthrough you claim.

😊 Optimist: Oh please! That's like saying cameras can't capture beauty because they're not human eyes. AI is already composing symphonies and creating art that moves people. Your narrow definition of creativity is just gatekeeping!
```

Each response is recorded with:
- Subject matter
- Timestamp
- Agent name
- Full response text
- Token count

## Cost Estimation

Using GPT-3.5-turbo with 150 tokens per response:
- ~$0.0015 per 1000 tokens
- 2 agents × 3 rounds = 6 responses
- 6 × 150 = 900 tokens per debate
- Cost: ~$0.00135 per debate subject

Very affordable for prototyping and testing!# debate-system
