# UtilityGuard 🌊
### Autonomous Multi-Agent Multi-Zone Water Utility Pipeline

**UtilityGuard** is an end-to-end "Agentic Workflow" designed to completely automate the monitoring, classification, and mitigation of critical IoT infrastructure events (like pipe leaks and localized water shortages). 

Instead of acting as a simple chatbot, UtilityGuard deploys a collaborative **Multi-Agent System** that executes the three core pillars of autonomous engineering: **Perception, Reasoning, and Action**.

---

## 🚀 The AI Architecture

UtilityGuard removes the human-in-the-loop for time-critical infrastructure emergencies utilizing 5 specialized agents:

1. **👀 PerceptionAgent**: Monitors IoT sensors across 5 distinct geographic zones. It identifies statistical baseline deviations (e.g., pressure dropping, flow surging) long before a human operator would notice. 
2. **🧠 ReasoningAgent (Mistral LLM)**: The "brain" of the operation. It receives the sensor deviations and uses advanced LLM logic to classify whether the anomaly is a harmless fluctuation, a **LEAK**, or a **SHORTAGE**.
   - *Self-Correction Feature:* Built with robust fallback logic. If the Mistral LLM API rate limits or drops, it fails over to a highly-tuned mathematical rule-based engine to ensure the pipeline never stops defending the infrastructure.
3. **🎯 ManagerAgent**: The orchestrator. It receives the classifications from the ReasoningAgent, formulates a comprehensive defense plan, and delegates tasks to the execution sub-agents.
4. **⚡ ActionAgent**: Bypasses conversational chat and interacts directly with infrastructure APIs. It automates physical world changes (e.g., executing a POST request to close a physical valve based on an LLM's classification) and logs resolutions to the CRM.
5. **📨 NotificationAgent**: Integrating with **SendGrid** and **Slack Webhooks**, this agent routes intelligent summaries of exactly *why* decisions were made to relevant human repair operators.

---

## 💻 Tech Stack
- **Dashboard & UI**: Streamlit (Reactive, Object-Oriented Component UI).
- **LLM Provider**: Mistral AI (`mistral-small-latest`) via native HTTP integration (Cost-effective fast reasoning).
- **Communication Infrastructure**: Mocked IoT generation, automated CRM JSON patching, Logging standard libs.
- **Tools / APIs Built For**: SendGrid, Slack Webhooks, Internal Utility APIs.

## 🏃 Getting Started 

1. **Set Up the Environment**
Create an `.env` file in the root directory containing your LLM provider key:
```env
MISTRAL_API_KEY=your_key_here
```

2. **Run The UI**
```bash
python -m streamlit run dashboard.py
```

3. **Trigger an Autonomous Response**
Open the application at `http://localhost:8501`. Under the **Simulation** menu, intentionally inject a "Shortage" or "Leak" anomaly into any zone. You will instantly witness the multi-agent system analyze the spike, reason it in JSON, and close the required valve!

---
*Built for the 2026 Agentathon — "Don't just talk, Act."*
