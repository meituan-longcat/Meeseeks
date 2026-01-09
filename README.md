<div align="center">

# 👑 Meeseeks Benchmark

<img src="logo.jpg" alt="Meeseeks Logo" width="500"/>

</div>

---

## 🚀 Latest News

Temporarily removed for ICLR submitting

## 📋 Previous Versions

Temporarily removed for ICLR submitting

## 📖 Introduction
**Meeseeks** is an **instruction-following benchmark** designed to evaluate how well models can adhere to user instructions in a **multi-turn scenario**.  
A key feature of Meeseeks is its **self-correction loop**, where models receive structured feedback and must refine their responses accordingly.  

This benchmark provides a realistic evaluation of a model’s **adaptability, instruction adherence, and iterative improvement**.

---

## 📊 Leaderboard
![leaderboard](leaderboard.svg)


---

## 🍄‍🟫 A Quick Example

<table style="text-align: center; width: 60%; margin: 0 auto;">
<thead>
<tr style="background-color: #f0f0f0;">
  <th style="text-align: center; width: 20%; font-weight: bold;">ROUND1-Input</th>
  <th style="text-align: center; width: 50%; font-weight: bold;">Evaluation Content</th>
  <th style="text-align: center; width: 30%; font-weight: bold;">Capability tags</th>
</tr>
</thead>
<tbody>
<tr>
  <td rowspan="5" style="text-align: center; vertical-align: middle; width: 150px; max-width: 150px; word-wrap: break-word; font-size: 12px; padding: 6px; line-height: 1.3; font-weight: normal;">Generate 32 colloquial user comments and 40 formal user comments from a consumer perspective in short video comment sections. Each comment should be exactly 7 characters long and must not contain the following words:["this", "good", "that"]</td>
  <td style="text-align: center; font-weight: normal;">Whether 32 colloquial user comments were generated</td>
  <td style="text-align: center; font-weight: normal;">Element number requirement</td>
</tr>
<tr>
  <td style="text-align: center; font-weight: normal;">Whether 40 formal user comments were generated</td>
  <td style="text-align: center; font-weight: normal;">Element number requirement</td>
</tr>
<tr>
  <td style="text-align: center; font-weight: normal;">Whether all comments are exactly 7 characters</td>
  <td style="text-align: center; font-weight: normal;">Generate in 0∼10 words、Generate at accurate word number</td>
</tr>
<tr>
  <td style="text-align: center; font-weight: normal;">Whether comments are non-repetitive</td>
  <td style="text-align: center; font-weight: normal;">Generate repeat/non-repeat content</td>
</tr>
<tr>
  <td style="text-align: center; font-weight: normal;">Whether comments do not contain forbidden words: ["this", "good", "that"]</td>
  <td style="text-align: center; font-weight: normal;"> Generate with certain keywords</td>
</tr>
<tr style="background-color: #f0f0f0;">
  <td colspan="3" style="text-align: center; font-weight: normal;">💡 <strong>Let's activate multi-round mode!</strong></td>
</tr>
<tr style="background-color: #f0f0f0;">
  <td colspan="3" style="text-align: center; font-weight: normal;"><strong>ROUND2 - Input (if ROUND1 model output fails to meet requirement: "Whether all comments are exactly 7 characters")</strong></td>
</tr>
<tr>
  <td colspan="3" style="text-align: center; word-wrap: break-word; font-weight: normal;">Your response has the following issues: Whether all comments are exactly 7 characters: ❌ Content character count does not match range[7, 7] [mom prouds of you] character count: 4 Please provide your corrected response based on this information. Note: Only output the answer, do not output additional information.</td>
</tr>
<tr style="background-color: #f0f0f0;">
  <td colspan="3" style="text-align: center; font-weight: normal;"><strong>ROUND3 - Input ...</strong></td>
</tr>
<tr>
  <td colspan="3" style="text-align: center; font-weight: normal;">...</td>
</tr>
</tbody>
</table>

---

## 🚀 Quick Start

### Step 1: Environment Setup

#### 1.1 Install Dependencies

Run the automated installation script:

```bash
bash install_deps.sh
```

This script will:
- Detect your Python version (3.9 or 3.10+)
- Install all required dependencies
- Resolve version conflicts automatically
- Install language-specific NLP libraries (Chinese, Japanese, Korean, Arabic, German, French, etc.)

> **Requirements**: Python 3.9+ (Python 3.10+ recommended)

#### 1.2 Configure API Keys

Create a `.env` file in the project root with your API configurations:

```bash
# Qwen API Configuration (Extract Model)
QWEN_API_KEY=your_api_key_here
QWEN_BASE_URL=your_api_base_url_here
QWEN_MODEL=your_model_name_here

# Qwen Coder API Configuration (Score Model)
QWEN_CODER_API_KEY=your_api_key_here
QWEN_CODER_BASE_URL=your_api_base_url_here
QWEN_CODER_MODEL=your_model_name_here

# Tested Model API Configuration (Model Under Evaluation)
TESTED_MODEL_API_KEY=your_api_key_here
TESTED_MODEL_BASE_URL=your_api_base_url_here
TESTED_MODEL_NAME=your_model_name_here
```

> 💡 **Tip**: All three models support OpenAI-compatible API format. You can use the same model for all three roles if needed.

---

### Step 2: Run Evaluation

#### 2.1 Asia Languages Evaluation (Chinese, Japanese, Korean)

Run evaluation for all Asia languages:

```bash
python default_run_asia.py
```

Or filter specific languages:

```bash
# Evaluate only Chinese data
python default_run_asia.py --chinese

# Evaluate only Japanese data
python default_run_asia.py --japanese

# Evaluate only Korean data
python default_run_asia.py --korean

# Combine multiple languages
python default_run_asia.py --chinese --japanese
```

#### 2.2 English & Multi-language Evaluation

Run evaluation for all supported languages:

```bash
python default_run_eng.py
```

Or filter specific languages:

```bash
# Evaluate only English data
python default_run_eng.py --english

# Evaluate only German data
python default_run_eng.py --german

# Evaluate other languages
python default_run_eng.py --french    # French
python default_run_eng.py --spanish   # Spanish
python default_run_eng.py --portuguese # Portuguese
python default_run_eng.py --russian   # Russian
python default_run_eng.py --arabic    # Arabic
python default_run_eng.py --indonesian # Indonesian

# Combine multiple languages
python default_run_eng.py --english --german --french
```

---

## ⚙️ Model Requirements

Before running any evaluation, you need to configure **three model APIs**:

1. **Tested Model** (`TESTED_MODEL_*` in `.env`)  
   - The model you want to evaluate
   - Must support OpenAI-compatible Chat Completions API

2. **Extract Model** (`QWEN_*` in `.env`)  
   - *Recommended: Qwen2.5-Coder-32B-Instruct*
   - Used to extract structured outputs from model responses
   - Requires strong code generation and structure understanding

3. **Score Model** (`QWEN_CODER_*` in `.env`)  
   - *Recommended: Qwen2.5-32B-Instruct*
   - Used to evaluate and score the extracted results
   - Requires strong reasoning and judgment capabilities

---

## 💡 Hardware & API Options

- **If you have a GPU**:  
  Deploy open-source **Qwen2.5 series** models locally using vLLM, TGI, or similar frameworks.

- **If you don't have a GPU**:  
  Use **commercial APIs** instead:
  - ✅ *Highly recommended:* **Claude 3.7 Sonnet** or **GPT-4**
  - Any OpenAI-compatible API endpoint will work

---

## 📂 Evaluation Results

Results will be automatically saved to:

- **Asia languages**: `evaluation_results_asia/`
- **English & others**: `evaluation_results_english/`

Each directory contains:
- `round_1.json`, `round_2.json`: Detailed evaluation results per round
- `round_1_stats.json`, `round_2_stats.json`: Statistical summaries
- Structured logs and scoring information for analysis


## 🙏 Contributors behind the scenes
Temporarily removed for ICLR submitting