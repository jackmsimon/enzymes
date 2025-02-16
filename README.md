# Enzyme Design with RFdiffusion and AI Program Search

This project aims to discover novel enzyme scaffolds around fixed catalytic motifs—particularly the **Ser–His–Asp** triad—using an **AlphaGo-style program search** combined with **automated web research**. It automates the end-to-end process from gathering relevant literature and insights to generating multiple RFdiffusion design scripts, each preserving the catalytic residues but varying the surrounding scaffold.

## Overview

### AlphaGo-Style Program Search
- Balances exploitation of known scaffold configurations with exploration of more radical alternatives.

### Deep Research Module
- Iteratively pulls and analyzes current literature on catalytic triads, refining design hypotheses before every generation step.

### RFdiffusion Integration
- Automatically builds Python scripts that call NVIDIA’s RFdiffusion endpoint to produce structures for each proposed scaffold.

## Features

- **Fixed Catalytic Motif**  
  Preserves the exact geometry of the Ser–His–Asp triad while letting the rest of the protein adapt.

- **Asynchronous Web Search**  
  Uses SERPAPI + LLM prompts to fetch and parse new research data, feeding those insights into the design module.

- **Agentic Pipeline**  
  Coordinates research, reasoning, and code generation steps to handle complex tasks (e.g. contig selection) without manual oversight.

- **Exploration/Exploitation**  
  Allows conservative designs that replicate known patterns alongside more adventurous scaffolds potentially yielding breakthroughs.
