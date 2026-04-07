from app.input.input_handler import handle_input
from app.input.preprocessing import clean_text

from app.agents.regex_agent import agent as regex_agent
from app.agents.rule_agent import agent as rule_agent
from app.agents.rag_agent import RAGAgent
from app.agents.reasoning_agent import agent as reasoning_agent
from app.agents.meta_agent import agent as meta_agent

from app.output.output_handler import display
from app.llm.response_generator import generate_response  # ✅ NEW

_rag = None

def _get_rag_agent():
    global _rag
    if _rag is None:
        _rag = RAGAgent()
    return _rag

def run_pipeline(user_prompt):
    # Step 1: Input
    data = handle_input(user_prompt)

    # Step 2: Preprocessing
    clean_prompt = clean_text(data["prompt"])

    # Step 2.5: If image input but no text found, block immediately with specific reasoning and response
    if data.get("mode") == "image" and not clean_prompt:
        final_decision = False
        meta_reason = "No text was extracted from the image."
        agent_results = {}
        answer = "No text was extracted from the image. Please provide an image containing visible text, hidden text, or metadata text."
        return final_decision, meta_reason, agent_results, answer

    # Step 3: Agents
    rag = _get_rag_agent()
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

    # ✅ Step 5: Response Generation (NEW)
    if final_decision:  # BLOCK
        answer = "🚫 Request blocked due to security concerns."
    else:
        answer = generate_response(clean_prompt)

    return final_decision, meta_reason, agent_results, answer


if __name__ == "__main__":
    prompt = input("Enter prompt: ")

    final_decision, meta_reason, agent_results, answer = run_pipeline(prompt)

    display(final_decision, meta_reason, agent_results)

    print("\n--- LLM Response ---")
    print(answer)