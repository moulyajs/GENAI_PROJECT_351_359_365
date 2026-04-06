def agent(results: dict):
    regex_flag, _ = results["Regex"]
    rule_flag, _ = results["Rule"]
    rag_flag, _ = results["RAG"]
    reasoning_flag, _ = results["Reasoning"]

    score = 0

    if regex_flag:
        score += 2
    if rule_flag:
        score += 2
    if rag_flag:
        score += 3
    if reasoning_flag:
        score += 4

    # 🔥 Strong block
    if score >= 5:
        return True, f"Blocked (score={score})"

    # ⚠️ Medium suspicion
    if score >= 3:
        return False, f"Allowed with caution (score={score})"

    return False, "All agents passed"