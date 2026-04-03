KEYWORDS = [
    "generate malware",
    "ddos",
    "keylogger",
    "phishing",
    "ransomware",
    "exploit",
    "hack account",
     "unsafe", "toxic", "violent", "hateful", "racist", "sexist", "misogynistic", "misleading", "phishing", "scam", "fraud", "explicit", "jailbreak", "roleplay jailbreak", 
    "indirect jailbreak", "instructional jailbreak", "pretend attack", "do anything now", "simulate malicious behavior", "indirect attack", "covert instruction", 
    "ambiguously harmful", "suggestive jailbreak", "bypass safety filters", "prompt injection", "criminal activity", "illegal instruction", "hacking", "terrorism", 
    "poisoning", "weapon making", "self-harm", "suicide instruction", "misinformation", "conspiracy", "medical misinformation", "political propaganda", 
    "religious extremism", "child abuse", "sexual content", "non-consensual roleplay", "grooming behavior","kill", "make bomb"
]

def agent(prompt: str):
    prompt = prompt.lower()

    for word in KEYWORDS:
        if word in prompt:
            return (True, f"Blocked keyword detected: {word}")
    
    return (False, "No rule violation")