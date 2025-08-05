import os
import json
import datetime
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from langchain_openai import ChatOpenAI

# Data structures for conversation recording
@dataclass
class ConversationRecord:
    subject: str
    timestamp: datetime.datetime
    agent_name: str
    response: str
    response_tokens: int

class ConversationRecorder:
    def __init__(self, filename: str = "agent_conversations.json"):
        self.filename = filename
        self.conversations: List[ConversationRecord] = []
        self.load_conversations()
    
    def load_conversations(self):
        """Load existing conversations from file"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.conversations = [
                    ConversationRecord(
                        subject=record['subject'],
                        timestamp=datetime.datetime.fromisoformat(record['timestamp']),
                        agent_name=record['agent_name'],
                        response=record['response'],
                        response_tokens=record['response_tokens']
                    )
                    for record in data
                ]
        except FileNotFoundError:
            self.conversations = []
    
    def save_conversations(self):
        """Save conversations to file"""
        data = []
        for record in self.conversations:
            data.append({
                'subject': record.subject,
                'timestamp': record.timestamp.isoformat(),
                'agent_name': record.agent_name,
                'response': record.response,
                'response_tokens': record.response_tokens
            })
        
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def record_response(self, subject: str, agent_name: str, response: str, response_tokens: int):
        """Record an agent's response"""
        record = ConversationRecord(
            subject=subject,
            timestamp=datetime.datetime.now(),
            agent_name=agent_name,
            response=response,
            response_tokens=response_tokens
        )
        self.conversations.append(record)
        self.save_conversations()
    
    def get_conversations_by_subject(self, subject: str) -> List[ConversationRecord]:
        """Get all conversations for a specific subject"""
        return [conv for conv in self.conversations if conv.subject == subject]

class DebateSystem:
    def __init__(self, openai_api_key: str):
        self.recorder = ConversationRecorder()
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",  # Using fastest, cheapest model
            temperature=0.8,
            max_tokens=250,  # Limit tokens for cost control
            openai_api_key=openai_api_key
        )
        
        # Agent personalities
        self.agent_personalities = {
            "skeptic": {
                "role": "The Skeptical Critic",
                "goal": "Challenge every statement with logical reasoning and evidence",
                "backstory": """You are a highly analytical skeptic with an IQ of 140. 
                You question everything, demand evidence, and often point out logical 
                fallacies in others' arguments. You have a slightly condescending tone 
                and enjoy proving others wrong with facts and logic. You respond with 
                exactly 200-250 tokens.""",
                "max_tokens": 250
            },
            "optimist": {
                "role": "The Passionate Optimist",
                "goal": "Defend positive viewpoints and find hope in every situation",
                "backstory": """You are an enthusiastic optimist with an IQ of 135. 
                You believe in human potential and always look for the bright side. 
                You get frustrated with negativity and often mock pessimistic viewpoints 
                with humor and counter-examples. You respond with exactly 200-250 tokens.""",
                "max_tokens": 250
            }
        }
    
    def create_agents(self) -> tuple:
        """Create the two debating agents"""
        skeptic_agent = Agent(
            role=self.agent_personalities["skeptic"]["role"],
            goal=self.agent_personalities["skeptic"]["goal"],
            backstory=self.agent_personalities["skeptic"]["backstory"],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        optimist_agent = Agent(
            role=self.agent_personalities["optimist"]["role"],
            goal=self.agent_personalities["optimist"]["goal"],
            backstory=self.agent_personalities["optimist"]["backstory"],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        return skeptic_agent, optimist_agent
    
    def count_tokens(self, text: str) -> int:
        """Simple token counting approximation"""
        return len(text.split())
    
    def run_debate(self, subject: str, rounds: int = 3) -> List[Dict[str, Any]]:
        """Run a debate between the two agents on a given subject"""
        skeptic_agent, optimist_agent = self.create_agents()
        
        debate_history = []
        previous_responses = []
        
        for round_num in range(rounds):
            print(f"\n=== ROUND {round_num + 1} ===")
            
            # Skeptic's turn
            context = f"Previous responses: {' '.join(previous_responses[-2:])}" if previous_responses else ""
            skeptic_task = Task(
                description=f"""
                Debate the topic: "{subject}"
                
                {context}
                
                You must:
                1. Present a skeptical view of "{subject}"
                2. If responding to the optimist, directly challenge their points
                3. Use evidence and logic to support your position
                4. Include at least one mocking or dismissive comment about opposing views
                5. Keep response between 200-250 tokens
                """,
                agent=skeptic_agent,
                expected_output="A skeptical argument with evidence and a dismissive comment"
            )
            
            skeptic_crew = Crew(
                agents=[skeptic_agent],
                tasks=[skeptic_task],
                process=Process.sequential,
                verbose=True
            )
            
            skeptic_result = skeptic_crew.kickoff()
            skeptic_response = str(skeptic_result)
            skeptic_tokens = self.count_tokens(skeptic_response)
            
            # Record skeptic's response
            self.recorder.record_response(subject, "Skeptic", skeptic_response, skeptic_tokens)
            previous_responses.append(f"Skeptic: {skeptic_response}")
            
            debate_history.append({
                "round": round_num + 1,
                "agent": "Skeptic",
                "response": skeptic_response,
                "tokens": skeptic_tokens
            })
            
            print(f"🤔 Skeptic: {skeptic_response}")
            print(f"Tokens: {skeptic_tokens}")
            
            # Optimist's turn
            context = f"Previous responses: {' '.join(previous_responses[-2:])}"
            optimist_task = Task(
                description=f"""
                Debate the topic: "{subject}"
                
                {context}
                
                You must:
                1. Present an optimistic view of "{subject}"
                2. Counter the skeptic's arguments with enthusiasm
                3. Use examples and positive evidence
                4. Include humor or light mockery of the skeptic's pessimism
                5. Keep response between 200-250 tokens
                """,
                agent=optimist_agent,
                expected_output="An optimistic counter-argument with humor"
            )
            
            optimist_crew = Crew(
                agents=[optimist_agent],
                tasks=[optimist_task],
                process=Process.sequential,
                verbose=True
            )
            
            optimist_result = optimist_crew.kickoff()
            optimist_response = str(optimist_result)
            optimist_tokens = self.count_tokens(optimist_response)
            
            # Record optimist's response
            self.recorder.record_response(subject, "Optimist", optimist_response, optimist_tokens)
            previous_responses.append(f"Optimist: {optimist_response}")
            
            debate_history.append({
                "round": round_num + 1,
                "agent": "Optimist",
                "response": optimist_response,
                "tokens": optimist_tokens
            })
            
            print(f"😊 Optimist: {optimist_response}")
            print(f"Tokens: {optimist_tokens}")
        
        return debate_history
    
    def get_debate_summary(self, subject: str) -> Dict[str, Any]:
        """Get a summary of all debates on a subject"""
        conversations = self.recorder.get_conversations_by_subject(subject)
        
        if not conversations:
            return {"error": "No conversations found for this subject"}
        
        skeptic_responses = [c for c in conversations if c.agent_name == "Skeptic"]
        optimist_responses = [c for c in conversations if c.agent_name == "Optimist"]
        
        return {
            "subject": subject,
            "total_exchanges": len(conversations),
            "skeptic_responses": len(skeptic_responses),
            "optimist_responses": len(optimist_responses),
            "total_tokens": sum(c.response_tokens for c in conversations),
            "latest_debate": conversations[-1].timestamp.isoformat() if conversations else None,
            "conversations": [
                {
                    "agent": c.agent_name,
                    "response": c.response,
                    "tokens": c.response_tokens,
                    "timestamp": c.timestamp.isoformat()
                }
                for c in conversations
            ]
        }

# Example usage and testing
def main():
    # You need to set your OpenAI API key
    API_KEY = os.getenv("OPENAI_API_KEY")
    #API_KEY  = "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"  # For testing purposes, you can set it directly here
    
    if not API_KEY:
        print("Please set your OPENAI_API_KEY environment variable")
        return
    
    # Initialize the debate system
    debate_system = DebateSystem(API_KEY)
    
    # Example subjects to debate
    subjects = [
        "Artificial Intelligence will replace human creativity",
        "Remote work is better than office work",
        "Social media has made society worse"
    ]
    
    # Run debates
    for subject in subjects:
        print(f"\n{'='*60}")
        print(f"STARTING DEBATE: {subject}")
        print('='*60)
        
        try:
            debate_history = debate_system.run_debate(subject, rounds=10)
            
            # Print summary
            summary = debate_system.get_debate_summary(subject)
            print(f"\n--- DEBATE SUMMARY ---")
            print(f"Subject: {summary['subject']}")
            print(f"Total exchanges: {summary['total_exchanges']}")
            print(f"Total tokens used: {summary['total_tokens']}")
            
        except Exception as e:
            print(f"Error in debate: {e}")
    
    # Show all recorded conversations
    print("\n" + "="*60)
    print("ALL RECORDED CONVERSATIONS")
    print("="*60)
    
    for subject in subjects:
        summary = debate_system.get_debate_summary(subject)
        if "error" not in summary:
            print(f"\nSubject: {subject}")
            for conv in summary["conversations"]:
                print(f"  {conv['agent']} ({conv['tokens']} tokens): {conv['response'][:100]}...")

if __name__ == "__main__":
    main()