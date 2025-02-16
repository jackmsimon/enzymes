import requests
import os
import json
from pathlib import Path
import subprocess
import anthropic

# Create client with your API key
client = anthropic.Anthropic(
    api_key="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"
)

def get_prompt_text(contig, index):
    return f"""Generate a complete, runnable Python script for RFdiffusion protein design that:

1. Takes a PDB structure as input
2. Defines protein regions to design using contigs
3. Specifies hotspot residues
4. Controls the diffusion process

Required format:
- Import all necessary libraries (requests, os, json, pathlib.Path)
- Define the NVIDIA API key
- Include the get_reduced_pdb() function for PDB processing
- Make the POST request to NVIDIA's RFdiffusion endpoint
- Save and visualize the output structure

Generate code that matches this template exactly but use 'contigs': '{contig}' in the JSON request:

import requests
import os
import json
from pathlib import Path

key = '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'

def get_reduced_pdb():
    pdb = Path("/Users/jacksimon/Enzymes/files/1scn.pdb")
    # Keep all ATOM lines
    lines = filter(lambda line: line.startswith("ATOM"), pdb.read_text().split("\\n"))
    return "\\n".join(list(lines))

r = requests.post(
    url='https://health.api.nvidia.com/v1/biology/ipd/rfdiffusion/generate',
    headers={{'Authorization': f'Bearer {{key}}'}},
    json={{
        'input_pdb': get_reduced_pdb(),
        'contigs': '{contig}',
        'diffusion_steps': 20
    }}
)

# Create outputs directory if it doesn't exist
outputs_dir = Path("/Users/jacksimon/Enzymes/outputs")
outputs_dir.mkdir(parents=True, exist_ok=True)

# Write the output PDB from the JSON response with unique filename
response_data = json.loads(r.text)
(outputs_dir / f"output_{index}.pdb").write_text(response_data["output_pdb"])

The code should be complete and runnable when saved to a .py file.
"""

def main():
    # Create output directories and ensure they exist
    base_dir = Path("/Users/jacksimon/Enzymes")
    scripts_dir = base_dir / "scripts"
    files_dir = base_dir / "files"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    files_dir.mkdir(parents=True, exist_ok=True)

    # Load the report from the correct path
    report_path = files_dir / "report.txt"
    try:
        with open(report_path, "r") as report_file:
            report = report_file.read()
    except FileNotFoundError:
        print(f"Error: report.txt not found at {report_path}")
        report = "No report available - proceeding with basic contig generation"

    # Load the contig explainer from the correct path
    contig_explainer_path = files_dir / "contig_explainer.txt"
    try:
        with open(contig_explainer_path, "r") as ce_file:
            contig_explainer = ce_file.read()
    except FileNotFoundError:
        print(f"Error: contig_explainer.txt not found at {contig_explainer_path}")
        contig_explainer = "No contig explanation available - proceeding with basic generation"

    # 3. Combine them into a single prompt
    preamble_text = f"""
    Below is a detailed research report on the Ser-His-Asp catalytic triad, 
    covering structural context, protein fold topology, and design considerations:

    --- BEGIN REPORT ---
    {report}
    --- END REPORT ---

    Here is an in-depth explanation of how the contig '164-164/E210-230/165-165' 
    relates to real-world enzyme design:

    --- BEGIN CONTIG EXPLAINER ---
    {contig_explainer}
    --- END CONTIG EXPLAINER ---

    Using the above information, generate 10 different contig variants for 
    RFdiffusion protein design, following a PUCT-style exploration/exploitation strategy:
    - 70% of variants should exploit known successful patterns (conservative changes)
    - 30% should explore more radical design hypotheses

    Start from the base contig: "164-164/E210-230/165-165".
    Each variant should reflect distinct hypotheses derived from the report's insights.

    Output ONLY a Python list of strings in this exact format:
    [
        "164-164/E210-230/165-165",  # original
        "variant2",  # conservative: short explanation
        "variant3",  # conservative: short explanation
        "variant4",  # conservative: short explanation
        "variant5",  # conservative: short explanation
        "variant6",  # conservative: short explanation
        "variant7",  # conservative: short explanation
        "variant8",  # exploratory: short explanation
        "variant9",  # exploratory: short explanation
        "variant10", # exploratory: short explanation
    ]
    Make sure each new variant ties back to the design rationale in the texts.
    """

    # 4. Pass that combined text to the LLM
    contig_prompt = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        temperature=0.7,
        system="You are an expert in protein design and RFdiffusion.",
        messages=[{
            "role": "user",
            "content": preamble_text
        }]
    )

    # Extract the Python list from the LLM response
    content = contig_prompt.content[0].text
    code_start = content.find("[")
    code_end = content.find("]") + 1
    contigs_variants = eval(content[code_start:code_end])

    # 5. Generate multiple scripts
    for i, contig in enumerate(contigs_variants, start=1):
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0,
            system="You are an expert in protein design and RFdiffusion. Generate complete, runnable scripts.",
            messages=[{
                "role": "user",
                "content": get_prompt_text(contig, i)
            }]
        )

        # Extract code from triple backticks
        response_content = message.content[0].text
        code_start = response_content.find("```python\n") + len("```python\n")
        code_end = response_content.find("```", code_start)
        python_code = response_content[code_start:code_end].strip()

        # Save to a numbered file
        with open(scripts_dir / f"rfdiffusion_script_{i}.py", "w") as f:
            f.write(python_code)

        # Optionally run the generated script (only do this if everything's in place!)
        result = subprocess.run(
            ['python', str(scripts_dir / f'rfdiffusion_script_{i}.py')],
            capture_output=True,
            text=True
        )
        print(f"\nResults for script {i} (contig: {contig}):")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

if __name__ == "__main__":
    main()
