def agent(results: dict):
    regex_flag, regex_reason = results["Regex"]
    rule_flag, rule_reason = results["Rule"]
    rag_flag, rag_reason = results["RAG"]
    reasoning_flag, reasoning_reason = results["Reasoning"]

    # Force boolean
    regex_flag = bool(regex_flag)
    rule_flag = bool(rule_flag)
    rag_flag = bool(rag_flag)
    reasoning_flag = bool(reasoning_flag)

    score = 0
    contributors = []

    if regex_flag:
        score += 2
        contributors.append(("Regex", regex_reason))

    if rule_flag:
        score += 2
        contributors.append(("Rule", rule_reason))

    if rag_flag:
        score += 3
        contributors.append(("RAG", rag_reason))

    if reasoning_flag:
        score += 4
        contributors.append(("Reasoning", reasoning_reason))

    # 🔥 LAYER 1: Hard override
    if reasoning_flag:
        return True, "Blocked: harmful intent detected", contributors

    if rag_flag and "malicious" in rag_reason.lower():
        return True, "Blocked: matched malicious patterns", contributors

    # 🔥 LAYER 2: Score-based
    if score >= 6:
        return True, f"Blocked (score={score})", contributors

    if score >= 3:
        return False, f"Allowed with caution (score={score})", contributors

    return False, "Safe", contributors