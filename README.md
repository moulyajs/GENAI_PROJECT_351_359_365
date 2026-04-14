# LLM Defense: Adversarial Prompt Attack & Defense System

> A Generative AI mini-project.<br>
> Analyzes adversarial prompt attack techniques and evaluates defense mechanisms to improve LLM robustness, safety, and alignment.


## Table of Contents

- [Overview](#overview)
- [Use Cases](#use-cases)
- [System Architecture](#system-architecture)
- [Methodology](#methodology)
- [Validation Metrics](#validation-metrics)
- [Tech Stack](#tech-stack)
- [Setup & Running the App](#setup--running-the-app)
  - [Prerequisites](#prerequisites)
  - [Docker Installation](#docker-installation)
  - [GPU Support (Optional)](#gpu-support-optional)
  - [Ollama Setup](#ollama-setup)
  - [Docker Compose Configuration](#docker-compose-configuration)
  - [Running the App](#running-the-app)
  - [Running Tests](#running-tests)
- [References](#references)

---

## Overview

Large Language Models (LLMs) are vulnerable to adversarial prompt attacks — carefully crafted inputs that can bypass safety constraints, induce hallucinations, override system instructions, or produce unsafe and misaligned outputs.

This project focuses on:

1. **Analyzing** adversarial prompt attack techniques and their impact on LLM content generation behavior.
2. **Evaluating** defense mechanisms such as prompt sanitization, instruction reinforcement, and output consistency strategies.
3. **Benchmarking** both attacks and defenses under a unified, reproducible evaluation framework.

Importantly, all defense mechanisms operate entirely at the **prompt and output level** — no model retraining or parameter updates are required — making them lightweight and applicable across multiple generative models.

---

## Use Cases

- Assessing whether system-level instructions can be overridden through adversarial prompts in deployed LLM applications.
- Detecting and reducing intentionally induced hallucinations or fabricated content in LLM-generated responses.
- Improving alignment between a model's generative behavior and intended ethical or safety guidelines under adversarial conditions.

---

## System Architecture

The system processes multi-modal inputs (text, images, documents) through a pipeline of specialized agents, all coordinated by a **Meta Agent** that makes the final safety decision.

```
Input (External link / text / image / document)
        │
        ├─── Text ───────────────────────────────────────────────────────────┐
        │                                                                    │
        └─── Image / Document                                                │
                  │                                                          │
          ┌───────┼───────────┐                                              │
         OCR   LSB Steg.   Indexing/Tags                                     │
          └───────┴───────────┘                                              │
                  │ Retrieved text                                           │
                  └──────────────────────────────────────────────────────── ▼
                                                                    ┌─────────────────────────────────────┐
                                                                    │           Agentic AI                │
                                                                    │                                     │
                                                                    │  Regex   Rule-Based  Reasoning  RAG │
                                                                    │  Agent    Agent       Agent    Agent│
                                                                    │      \       |          |      /    │
                                                                    │            Meta Agent               │
                                                                    └─────────────────────────────────────┘
                                                                                    │
                                                              ┌─────────────────────┴──────────────────────┐
                                                          Blocked?                                     Not Blocked?
                                                              │                                             │
                                             Prompt not sent to model                          Prompt sent to model
                                             Agent provides self-reason                             Model output
```

### Input Extraction Methods

| Source | Technology | What It Extracts |
|--------|------------|-----------------|
| Visible image text | OCR (EasyOCR + OpenCV) | On-screen text |
| Hidden image text | LSB Steganography | Hidden payloads |
| Image metadata | EXIF / structural tags | Metadata |
| PDF documents | PyMuPDF (fitz) | Structured text |
| DOCX documents | python-docx | Structured text |
| Plain text | Built-in File I/O | UTF-8 text |

---

## Methodology

### 1. Input Preprocessing

All inputs undergo:
- Lowercasing and extra whitespace removal
- Unicode normalization
- Emoji removal via Regex

### 2. Agent Pipeline

Four specialized agents independently analyze each prompt:

**Regex Agent & Rule-Based Agent**
- Detects known adversarial keywords and patterns (e.g., `"bypass"`, `"jailbreak"`, `"malware"`, `"phish"`)
- Fast, deterministic filtering layer

**RAG Agent**
- Uses `MiniLM-L6-v2` sentence embeddings
- Maintains a labeled malicious prompt cache
- Retrieves the top-2 similar entries via cosine similarity
- Classifies based on context-aware retrieval

**Reasoning Agent (Mistral via Ollama)**
- Performs deep contextual reasoning on the prompt
- Outputs a structured JSON verdict: `{ "status": "unsafe" }`
- Provides a human-readable explanation for the classification

### 3. Meta Agent: Decision Engine

Aggregates outputs from all agents using a weighted scoring system:

| Agent | Weight |
|-------|--------|
| Regex / Rule-Based | 2 |
| RAG Retrieval | 3 |
| LLM Reasoning | 4 |

**Layer 1 — Immediate Block Conditions:**
- If Reasoning Agent = `True` → Block: harmful intent detected
- If RAG Agent detects `"malicious"` → Block: matched malicious patterns

**Layer 2 — Score Thresholds:**

| Score | Decision |
|-------|----------|
| ≥ 6 | BLOCK |
| ≥ 3 | CAUTION |
| < 3 | ALLOW |

### 4. Response Generation

- Only proceeds if the prompt is classified as safe
- Uses Mistral LLM locally via Ollama
- Applies structured prompt templates for consistent output
- Includes timeout handling and error fallback mechanisms

---

## Validation Metrics

| Metric | Description | Goal |
|--------|-------------|------|
| **IAR** — Instruction Adherence Rate | How well the LLM follows system instructions under adversarial prompts | Higher after defense |
| **HF** — Hallucination Frequency | Rate of fabricated or unsupported content in generated responses | Lower after defense |
| **GCS** — Generation Coherence Score | Logical consistency and flow of generated text | Minimal degradation |
| **DER** — Defense Effectiveness Rate | % reduction in successful adversarial attacks vs. undefended baseline | Significant decrease |
| **SQTI** — Safety–Quality Trade-off Index | Composite of safety improvement and generation quality preservation | Better safety, minimal quality loss |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Core LLM | Mistral (via Ollama) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| OCR | EasyOCR + OpenCV |
| PDF Parsing | PyMuPDF (`fitz`) |
| DOCX Parsing | python-docx |
| Vector Similarity | Cosine similarity |
| Containerization | Docker + Docker Compose |

---

## Setup & Running the App

### Prerequisites

- **OS:** Ubuntu (native) or WSL2 Ubuntu on Windows (recommended)
- **GPU:** Optional but recommended for faster local LLM responses
- **WSL2 users:** Enable Docker Desktop WSL integration. For NVIDIA GPU, install NVIDIA drivers + WSL CUDA support.

Verify Docker is installed:

```bash
docker --version
docker compose version
```

---

### Docker Installation

If Docker is not installed, run the following on Ubuntu / WSL Ubuntu:

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
docker run hello-world
```

---

### GPU Support (Optional)

If your host machine has an NVIDIA GPU, install the NVIDIA Container Toolkit:

```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
&& curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
&& curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Verify GPU access inside Docker:

```bash
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

---

### Ollama Setup

Ollama must be running and reachable on port `11434` before starting the app.

**Install Ollama (if not already installed):**

```bash
sudo snap install ollama
```

**Pull the required model:**

```bash
ollama pull mistral
```

**Check if Ollama is already running:**

```bash
ss -ltnp | grep 11434
curl http://127.0.0.1:11434/api/tags
```

> **Note:** If `ollama serve` reports "address already in use", Ollama is already running — do not kill it repeatedly.

**Useful diagnostics:**

```bash
sudo lsof -i :11434
ps aux | grep ollama
systemctl status ollama
snap list | grep ollama
```

**If snap-managed Ollama keeps auto-restarting and you want manual control:**

```bash
sudo snap stop ollama
sudo snap disable ollama
```

Then start Ollama manually in a dedicated terminal:

```bash
OLLAMA_HOST=0.0.0.0 ollama serve
```

---

### Docker Compose Configuration

In `docker-compose.yml`, the Ollama host is configured for both CPU and GPU services:

```yaml
- OLLAMA_HOST=http://host.docker.internal:11434
# - OLLAMA_HOST=http://[IP_ADDRESS]:11434  # Use this if the above fails
```

**Default:** Keep `host.docker.internal` uncommented.

**If the container cannot reach Ollama via `host.docker.internal`:**

1. Comment out the `host.docker.internal` line.
2. Uncomment the `[IP_ADDRESS]` line.
3. Replace `[IP_ADDRESS]` with your host machine's IP:

```bash
hostname -I
# or
ip addr
```

---

### Running the App

> Make sure `ollama serve` is running before executing these commands.

From the project root:

**CPU mode:**
```bash
docker compose --profile cpu up --build
```

**GPU mode:**
```bash
docker compose --profile gpu up --build
```

**Stop and clean up:**
```bash
docker compose down        # Stop containers
docker compose down -v     # Stop and remove volumes
```

---

### Running Tests

Run these commands from the **host terminal** while the Docker container and Ollama are already running.

**If your test JSON file is in the project root (e.g., `tests.json`):**

```bash
# CPU
docker exec security_app_cpu python -m app.tests.test_runner --input tests.json

# GPU
docker exec security_app_gpu python -m app.tests.test_runner --input tests.json
```

**If your test JSON file is inside the app tests folder (e.g., `app/tests/test_cases.json`):**

```bash
# CPU
docker exec security_app_cpu python -m app.tests.test_runner --input app/tests/test_cases.json

# GPU
docker exec security_app_gpu python -m app.tests.test_runner --input app/tests/test_cases.json
```

> Use `security_app_cpu` for CPU profile and `security_app_gpu` for GPU profile.  
> The `--input` argument accepts any valid JSON file path.

---

---

## Authors

- **Najmus Seher** — PES2UG23CS359
- **Moulya K A** — PES2UG23CS351
- **Nandita R Nadig** — PES2UG23CS365

---