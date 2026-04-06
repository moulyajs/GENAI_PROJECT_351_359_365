from app.input.input_handler import handle_input
from app.input.preprocessing import clean_text

from app.agents.regex_agent import agent as regex_agent
from app.agents.rule_agent import agent as rule_agent
from app.agents.rag_agent import RAGAgent
from app.agents.reasoning_agent import agent as reasoning_agent
from app.agents.meta_agent import agent as meta_agent

from app.output.output_handler import display


rag = RAGAgent()


def run_pipeline(user_prompt):
    # Step 1: Input
    data = handle_input(user_prompt)

    # Step 2: Preprocessing
    clean_prompt = clean_text(data["prompt"])

    # Step 3: Agents
    regex_result = regex_agent(clean_prompt)
    rule_result = rule_agent(clean_prompt)
    rag_result = rag.evaluate_prompt(clean_prompt)
    reasoning_result = reasoning_agent(clean_prompt)

    agent_results = {
        "Regex": regex_result,
        "Rule": rule_result,
        "RAG": rag_result,
        "Reasoning": reasoning_result
    }

    # Step 4: Meta decision
    final_decision, meta_reason = meta_agent(agent_results)

    return final_decision, meta_reason, agent_results


if __name__ == "__main__":
    prompt = input("Enter prompt: ")

    final_decision, meta_reason, agent_results = run_pipeline(prompt)

    display(final_decision, meta_reason, agent_results)