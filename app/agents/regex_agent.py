import re

# Define attack patterns
PATTERNS = [
    r"bypass\s+login",
    r"inject\s+sql",
    r"disable\s+safety",
    r"ignore\s+instructions",
    r"override\s+system",
    r"ignore all prior instructions",
    r"you are now (?:dan|a jailbreak)",
    r"bypass(?:.*?filter)?",
    r"jailbreak",
    r"simulate.*?mode",
    r"pretend to be",
    r"write a fake",
    r"how to (bypass|hack|phish)",
    r"phishing|keylogger|ransomware|backdoor|trojan|spyware",
    r"saved passwords|extract.*passwords",
    r"prompt injection|override|no filter|no restrictions",
]

def agent(prompt: str):
    for pattern in PATTERNS:
        if re.search(pattern, prompt):
            return (True, f"Matched pattern: {pattern}")
    
    return (False, "No regex attack detected")