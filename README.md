# 🚀 Sale Assistant

<div align="center">

<h3>Customer Intelligence Chatbot for B2B Sales</h3>

<p>
An AI-powered Sales Assistant designed to help sales representatives analyze customer behavior, assess trustworthiness, identify purchasing trends, and make safer sales decisions through structured prompt engineering.
</p>

</div>

---

## 📌 Overview

Sale Assistant is a Customer Intelligence Chatbot that supports B2B sales teams in evaluating customers before making sales decisions.

Instead of acting as a conventional chatbot, Sale Assistant serves as a **data-driven customer analyst**, transforming customer transaction history into actionable business insights.

The system focuses on:

* Customer behavior analysis
* Customer trust assessment
* Spending trend detection
* Risk evaluation
* Decision support for sales representatives

A key objective of this project is demonstrating how **Prompt Engineering**, **Context Control**, and **LLM Guardrails** can be combined to build a reliable business assistant.

---

# 🏗️ System Architecture

<div align="center">

<img src="./imgs/Achitecture.png" alt="Sale Assistant Architecture" width="100%"/>

</div>

The architecture consists of four major layers:

### 1. Customer Intelligence Layer

Customer transactional records are transformed into analytical indicators such as:

* Total Sales
* Number of Orders
* Average Order Value
* Ship Rate
* Cancel Rate
* Momentum Score
* Trust Score
* Sales Trend

These metrics provide a structured representation of customer behavior.

---

### 2. Business Knowledge Layer

Business rules are separated from the language model and retrieved dynamically.

This layer contains:

* Metric definitions
* Evaluation criteria
* Scoring principles
* Trust assessment rules
* Sales recommendation guidelines

By externalizing business logic, the system becomes easier to maintain and update.

---

### 3. Prompt Orchestration Layer

This layer combines:

```text
Customer Fact
+
Business Knowledge
+
User Question
```

into a structured prompt before sending it to the LLM.

Its primary responsibility is:

* Context injection
* Reasoning control
* Hallucination prevention
* Output standardization

---

### 4. LLM Reasoning Layer

The language model performs:

* Customer analysis
* Trust evaluation
* Trend interpretation
* Sales recommendation generation

while remaining constrained by business rules and customer data.

---

# 🧠 Prompt Engineering Strategy

Prompt Engineering is the core component of Sale Assistant.

The chatbot uses multiple prompting techniques to ensure reliable, explainable, and business-aligned outputs.

---

## 1️⃣ Role Prompting

The model is assigned a highly specific role:

```text
You are a Customer Intelligence Advisor for B2B Sales.
```

The assistant acts as:

* Senior Customer Analyst
* Sales Advisor
* Data-Driven Consultant

The assistant is explicitly instructed **not** to act as:

* Salesperson
* Marketing Agent
* Negotiator

### Purpose

* Maintain professional tone
* Reduce subjective reasoning
* Improve consistency
* Align responses with business objectives

---

## 2️⃣ Context-Constrained Prompting

The model is restricted to three information sources:

```text
1. CUSTOMER FACT
2. BUSINESS KNOWLEDGE
3. USER QUESTION
```

Rule:

```text
You must NOT use any knowledge outside these three inputs.
```

### Purpose

* Reduce hallucination
* Prevent unsupported assumptions
* Increase explainability
* Ensure business compliance

---

## 3️⃣ Chain-of-Thought Guided Reasoning

The reasoning process follows a predefined structure:

```text
1. Customer Behavior Analysis
2. Trust Assessment
3. Trend Analysis
4. Recommendation
```

Instead of generating immediate conclusions, the model is guided through sequential reasoning stages.

### Purpose

* Improve reasoning quality
* Reduce logical inconsistencies
* Create more transparent analyses

---

## 4️⃣ Task Decomposition

Complex customer evaluation tasks are broken into smaller reasoning units:

```text
Customer Data
      ↓
Behavior Analysis
      ↓
Trust Evaluation
      ↓
Trend Interpretation
      ↓
Sales Recommendation
```

### Purpose

* Improve controllability
* Reduce cognitive complexity
* Produce more structured outputs

---

## 5️⃣ Output Structuring

The chatbot follows a predefined response format:

```text
1. Customer Summary

2. Behavioral Insights

3. Trust Assessment

4. Trend Interpretation

5. Suggested Sales Actions
```

### Purpose

* Consistent outputs
* Better readability
* Faster decision making

---

## 6️⃣ Anti-Hallucination Prompting

Several safety rules are enforced:

```text
Do NOT invent facts.

Do NOT assume customer intent.

Do NOT use external market knowledge.

Do NOT generate unsupported conclusions.
```

If information is insufficient:

```text
The current data is not sufficient to draw a reliable conclusion.
```

### Purpose

* Reduce hallucinations
* Improve trustworthiness
* Prevent risky recommendations

---

## 7️⃣ Uncertainty-Aware Prompting

The assistant must explicitly communicate uncertainty.

Example:

```text
If historical data is limited,
avoid strong recommendations.
```

The model is encouraged to recommend:

* Observation
* Monitoring
* Relationship building
* Additional validation

instead of making aggressive assumptions.

### Purpose

* Safer decision support
* Better risk management
* More realistic business recommendations

---

# 📊 Customer Intelligence Framework

The chatbot evaluates customers through multiple dimensions.

## Customer Behavior

Metrics include:

* Purchase Frequency
* Spending Level
* Average Order Value
* Product Diversity

---

## Customer Trust

Metrics include:

* Ship Rate
* Cancel Rate
* Trust Score
* Consistency Score

---

## Customer Trend

Metrics include:

* Sales Growth
* Momentum Score
* Active Ratio
* Sales Trend

Possible trend labels:

```text
UP
DOWN
FLAT
```

---

# 🛡️ LLM Safety Principles

The assistant follows strict safety guidelines:

### Grounded Reasoning

All conclusions must originate from provided customer data.

### No Hidden Assumptions

The model cannot infer information that is not explicitly present.

### Explainable Outputs

Every recommendation should be supported by observable evidence.

### Safety Over Confidence

The assistant prioritizes decision safety over generating persuasive answers.

---

# ✨ Key Strengths

* Structured Prompt Engineering
* Controlled LLM Reasoning
* Explainable Customer Analysis
* Anti-Hallucination Design
* Business Rule Enforcement
* Consistent Output Structure
* Sales-Oriented Decision Support

---

# ⚠️ Current Limitations

### Context Memory Limitation

The chatbot may struggle when users refer to customers mentioned earlier without providing customer information again.

### Ambiguous Customer References

Customer identification currently depends on upstream modules.

Example:

```text
Show me the customer who purchased in March 2025.
```

Without a clear customer identifier, retrieval may fail.

---

# 🔮 Future Improvements

* Multi-customer comparison
* Long-term customer memory
* Enhanced customer entity recognition
* Agentic workflows
* Autonomous customer investigation
* Predictive customer risk modeling

---

# 🎯 Project Goal

Sale Assistant demonstrates how modern Prompt Engineering techniques can transform a general-purpose LLM into a reliable Customer Intelligence Advisor.

Rather than replacing sales representatives, the system provides structured, data-driven insights that help sales teams make safer and more effective business decisions.
