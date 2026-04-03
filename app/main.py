from input.input_handler import handle_input
from input.preprocessing import clean_text
from agents.regex_agent import agent as regex_agent
from agents.rule_agent import agent as rule_agent


def run_pipeline(user_prompt):
    # Step 1: Input
    data = handle_input(user_prompt)

    # Step 2: Preprocessing
    clean_prompt = clean_text(data["prompt"])

    # Step 3: Agents
    regex_result = regex_agent(clean_prompt)
    rule_result = rule_agent(clean_prompt)

    return {
        "Regex": regex_result,
        "Rule": rule_result,
        "clean_prompt": clean_prompt
    }


if __name__ == "__main__":
    prompt = input("Enter prompt: ")
    result = run_pipeline(prompt)
    print(result)