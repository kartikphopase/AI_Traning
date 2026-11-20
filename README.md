[![JalSanchay CI](https://github.com/kartikphopase/AI_Traning/actions/workflows/ci.yml/badge.svg)](https://github.com/kartikphopase/AI_Traning/actions/workflows/ci.yml)

# JalSanchay

Product: JalSanchay

User: Final-year Civil Engineering student at Sanjivani.

Problem: A student needs to propose rooftop rainwater harvesting or groundwater recharge systems for the college hostel block and her family's bungalow in Kopargaon.

Data Source: Central Ground Water Board (CGWB) official manuals containing technical information, tables, formulas and figures about rooftop rainwater harvesting and groundwater recharge.

Project Goal: Help users understand and design suitable rooftop rainwater harvesting or recharge setups using official CGWB guidelines.


## Day 8 – RAG Evaluation Results

We evaluated two RAG configurations using a 15-question evaluation dataset.

| Configuration | Chunk Size | Overlap | Top-k | Keyword Coverage | Q6 Abstention |
|---|---:|---:|---:|---:|---|
| A | 1200 | 200 | 3 | 80.95% | Pass |
| B | 800 | 100 | 5 | **83.33%** | Pass |

### Winning Configuration

**Configuration B** was selected as the winner because it achieved the highest keyword coverage of 83.33%.

Both configurations successfully passed the Q6 abstention test, meaning the system correctly responded with "I don't know" when asked for current groundwater levels at an exact plot in Kopargaon.

*Note: Keyword coverage measures how many expected keywords were retrieved. It does not represent overall answer accuracy.*
