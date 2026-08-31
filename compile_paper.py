#!/usr/bin/env python3
"""
Compile the original paper.tex to PDF with embedded figures
"""
import subprocess
import os
import shutil

# Set up paths
paper_dir = r"c:\myprojects\Kaisen\ResearchDocs\docs"
figures_dir = r"c:\myprojects\Kaisen\eval\figures"
output_pdf = os.path.join(paper_dir, "paper.pdf")

# Copy figures to paper directory
print("[*] Copying figures...")
for fig in ["01_roc_curves.pdf", "02_ablation_study.pdf", "03_detection_latency.pdf", 
            "04_confusion_matrix.pdf", "05_literature_comparison.pdf", "05_literature_comparison.png"]:
    src = os.path.join(figures_dir, fig)
    dst = os.path.join(paper_dir, fig)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"  ✓ {fig}")

# Update graphicspath in paper.tex
print("[*] Updating paper.tex...")
paper_tex = os.path.join(paper_dir, "paper.tex")
with open(paper_tex, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace graphicspath
content = content.replace(r'\graphicspath{{../eval/figures/}}', r'\graphicspath{{./}}')

with open(paper_tex, 'w', encoding='utf-8') as f:
    f.write(content)

# Find pdflatex
pdflatex_paths = [
    r"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe",
    "pdflatex"
]

pdflatex_cmd = None
for path in pdflatex_paths:
    if os.path.exists(path) or shutil.which(path):
        pdflatex_cmd = path
        break

if not pdflatex_cmd:
    print("[-] pdflatex not found!")
    exit(1)

print(f"[*] Using pdflatex: {pdflatex_cmd}")

# Compile twice
for i in range(2):
    print(f"[*] Compiling (pass {i+1}/2)...")
    result = subprocess.run(
        [pdflatex_cmd, "-interaction=nonstopmode", "-output-directory=" + paper_dir, paper_tex],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"[-] Compilation failed: {result.stderr}")
    else:
        print(f"  ✓ Pass {i+1} complete")

# Check result
if os.path.exists(output_pdf):
    size = os.path.getsize(output_pdf) / (1024 * 1024)
    print(f"\n✓ SUCCESS: PDF generated")
    print(f"  File: {output_pdf}")
    print(f"  Size: {size:.2f} MB")
else:
    print(f"\n✗ FAILED: PDF not created at {output_pdf}")
    # List what was created
    print(f"\n[*] Files in {paper_dir}:")
    for f in os.listdir(paper_dir):
        print(f"  - {f}")
