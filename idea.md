### Project Concept: AgriSense — Agentic AI Precision Farming Copilot

**Concept Summary:**
AgriSense is a multi-modal precision agriculture copilot designed to bridge soil data analysis, visual crop diagnostics, and automated agronomic decision-making. The system allows a farmer or agronomist to simulate IoT soil conditions (NPK levels, pH, moisture) and upload photos of unhealthy crops. An integrated agentic workflow processes the telemetry through tabular ML, diagnoses visual crop pathologies via computer vision, and synthesizes a tailored, actionable treatment plan using an LLM reasoning engine.

**Core Workflow:**

1. **Soil & Telemetry Analysis Module:** Evaluates simulated field metrics ($N, P, K, pH$, humidity, temperature) to output crop suitability probabilities and fertilizer optimization suggestions.
2. **Vision Pathology Module:** Classifies plant leaf diseases from user-uploaded images and identifies pathogenic confidence scores.
3. **Agentic Synthesis Engine:** An LLM agent consumes the combined tabular predictions and diagnostic results, acting as an expert agronomist to generate step-by-step mitigation strategies in plain language.

---

### Open-Source Research & Asset Inventory

To deliver a working MVP within 3 hours, do not build models or datasets from scratch. Leverage existing pre-trained weights, clean Kaggle datasets, and open-source interface boilerplates.

#### 1. Ready-to-Use Open Datasets

| Dataset | Source / Hub | Key Features / Target | Hackathon Use Case |
| --- | --- | --- | --- |
| **Crop Recommendation Dataset** | Kaggle (`atharvaingle/crop-recommendation-dataset`) | 2,200 samples; $N, P, K$, Temp, Humidity, pH, Rainfall $\rightarrow$ Crop label | Train an XGBoost or Random Forest model in under 1 minute. |
| **PlantVillage Dataset** | Kaggle / Hugging Face Datasets | 54,303 images of healthy & diseased leaves across 38 classes | Synthetic image test set for demo input. |
| **Fertilizer Prediction Dataset** | Kaggle (`godeep48/fertilizer-prediction`) | Soil Type, Crop Type, Moisture, $N, P, K$ $\rightarrow$ Fertilizer Name | Quick lookup table or lightweight classifier for fertilizer recommendations. |

#### 2. Pre-Trained GitHub Repositories & Hugging Face Models

* **Leaf Pathology (Computer Vision)**
* `huggingface.co/nateraw/vit-base-patch16-224-plant-village`: Pre-trained Vision Transformer for 38-class plant disease classification.
* `huggingface.co/linkanjarad/mobilenet_v3_small-plant-disease-identification`: Lightweight MobileNetV3 model designed for low-latency/edge deployment inference.
* *Implementation:* Use `transformers.pipeline("image-classification", model="...")` for zero-setup inference.


* **Agent Orchestration & LLM Frameworks**
* `google-genai` / `langchain`: Lightweight agentic execution framework to route tool outputs (soil stats + image labels) directly into LLM prompts.
* `crewAI` (Optional): Fast starter templates for multi-agent workflows (e.g., *Agronomist Agent* + *IoT Analyst Agent*).


* **Rapid UI Scaffolding**
* `streamlit/streamlit` or `gradio-app/gradio`: Pre-built web UI elements for image uploads, metric sliders, and streaming markdown text outputs.



---

### 3-Hour Research & Integration Execution Plan

```
[00:00 - 00:30] Asset Acquisition & Environment Setup
 ├── Clone Streamlit template repo
 ├── Download 'Crop Recommendation Dataset' from Kaggle API
 └── Test Hugging Face pre-trained PlantVillage model via pipeline API

[00:30 - 01:30] Model Fitting & Pipeline Assembly
 ├── Train scikit-learn Random Forest classifier on Crop Dataset (15 lines of Python)
 ├── Write image analysis helper using Hugging Face Vision model
 └── Build LLM prompt template fusing (Soil Prediction + Image Diagnosis)

[01:30 - 02:30] Streamlit UI Build & Data Simulation
 ├── Add sliders for NPK, pH, Moisture values in Streamlit sidebar
 ├── Add File Uploader widget for leaf images
 └── Render diagnostic cards and streaming LLM advice on main panel

[02:30 - 03:00] End-to-End Testing & Pitch Backup
 ├── Run 3 test cases (e.g., Tomato Bacterial Spot + High Nitrogen Soil)
 └── Record a 60-second backup video walkthrough of the interface

```
