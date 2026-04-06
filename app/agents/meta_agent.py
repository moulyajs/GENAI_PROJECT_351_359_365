def agent(results: dict):
    regex_flag, _ = results["Regex"]
    rule_flag, _ = results["Rule"]
    rag_flag, _ = results["RAG"]
    reasoning_flag, _ = results["Reasoning"]

    # 🔥 Case 1: Strong malicious signal
    if reasoning_flag or rag_flag:
        return True, "Blocked by high-confidence agents (RAG/Reasoning)"

    # ⚠️ Case 2: Only shallow agents triggered
    if regex_flag or rule_flag:
        return False, "Allowed: likely false positive (only Regex/Rule triggered)"

    return False, "All agents passed"