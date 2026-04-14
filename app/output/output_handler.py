def display(final_decision, meta_reason, agent_results):
    
    print("\n==============================")
    print("FINAL DECISION:", "BLOCK" if final_decision else "ALLOW")
    print("Reason:", meta_reason)

    print("\n--- Agent Breakdown ---")
    for agent, (flag, reason) in agent_results.items():
        print(f"{agent}: {'BLOCK' if flag else 'ALLOW'} | {reason}")