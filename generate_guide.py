"""
Script to concatenate guide sections into PROJECT_INTERVIEW_GUIDE.md
and convert to PROJECT_INTERVIEW_GUIDE.pdf via Edge headless.
"""
import os
import subprocess
import markdown

sections = [
    "guide_sections/sec_01_02.md",
    "guide_sections/sec_03.md",
    "guide_sections/sec_04.md",
    "guide_sections/sec_05.md",
    "guide_sections/sec_06.md",
    "guide_sections/sec_07.md",
    "guide_sections/sec_08_09.md",
    "guide_sections/sec_10_13.md",
    "guide_sections/sec_14_18.md",
    "guide_sections/sec_19_24.md",
    "guide_sections/sec_25.md",
    "guide_sections/sec_26_34.md"
]

combined_md = []
for s in sections:
    if os.path.exists(s):
        with open(s, "r", encoding="utf-8") as f:
            combined_md.append(f.read())
    else:
        print(f"Warning: {s} not found!")

full_md_content = "\n\n---\n\n".join(combined_md)

with open("PROJECT_INTERVIEW_GUIDE.md", "w", encoding="utf-8") as f:
    f.write(full_md_content)

print(f"PROJECT_INTERVIEW_GUIDE.md created successfully. Total size: {len(full_md_content)} characters.")

# Convert to HTML for PDF generation
html_body = markdown.markdown(
    full_md_content,
    extensions=["tables", "fenced_code", "toc"]
)

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Travel Agent - Engineering Interview Guide</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm 15mm 20mm 15mm;
            @bottom-right {{
                content: counter(page);
            }}
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 10.5pt;
            line-height: 1.5;
            color: #1f2937;
            background: #ffffff;
            margin: 0;
            padding: 0;
        }}
        h1, h2, h3, h4 {{
            color: #111827;
            font-weight: 700;
            page-break-after: avoid;
        }}
        h1 {{
            font-size: 20pt;
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 6px;
            margin-top: 24px;
        }}
        h2 {{
            font-size: 15pt;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 4px;
            margin-top: 20px;
            color: #1e40af;
        }}
        h3 {{
            font-size: 12pt;
            margin-top: 16px;
            color: #1f2937;
        }}
        h4 {{
            font-size: 11pt;
            margin-top: 12px;
        }}
        p, li {{
            color: #374151;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 14px 0;
            font-size: 9pt;
            page-break-inside: avoid;
        }}
        th, td {{
            border: 1px solid #d1d5db;
            padding: 6px 10px;
            text-align: left;
            vertical-align: top;
        }}
        th {{
            background-color: #f3f4f6;
            font-weight: 600;
            color: #111827;
        }}
        tr:nth-child(even) {{
            background-color: #f9fafb;
        }}
        code {{
            font-family: "Consolas", "Courier New", monospace;
            font-size: 9pt;
            background-color: #f3f4f6;
            padding: 2px 4px;
            border-radius: 4px;
            color: #b91c1c;
        }}
        pre {{
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #3b82f6;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 8.5pt;
            page-break-inside: avoid;
        }}
        pre code {{
            color: #1e293b;
            background-color: transparent;
            padding: 0;
        }}
        blockquote {{
            border-left: 4px solid #60a5fa;
            margin: 12px 0;
            padding: 6px 14px;
            background-color: #eff6ff;
            color: #1e40af;
            font-style: italic;
        }}
        hr {{
            border: none;
            border-top: 1px solid #e5e7eb;
            margin: 20px 0;
        }}
        .header-cover {{
            text-align: center;
            padding: 40px 0 20px 0;
            border-bottom: 2px solid #2563eb;
            margin-bottom: 30px;
        }}
        .header-cover h1 {{
            font-size: 26pt;
            border: none;
            color: #1e3a8a;
            margin-bottom: 8px;
        }}
        .header-cover p {{
            font-size: 12pt;
            color: #4b5563;
        }}
    </style>
</head>
<body>
    <div class="header-cover">
        <h1>AI Travel Agent</h1>
        <p>Comprehensive Software Engineering Interview Defense & System Guide</p>
    </div>
    {html_body}
</body>
</html>
"""

with open("temp_guide.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("temp_guide.html generated. Converting to PDF via Edge headless...")

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
html_abs = os.path.abspath("temp_guide.html")
pdf_abs = os.path.abspath("PROJECT_INTERVIEW_GUIDE.pdf")

res = subprocess.run([
    edge_path,
    "--headless",
    "--disable-gpu",
    f"--print-to-pdf={pdf_abs}",
    f"file:///{html_abs}"
], capture_output=True, text=True)

print(f"Edge return code: {res.returncode}")
if os.path.exists(pdf_abs):
    print(f"PROJECT_INTERVIEW_GUIDE.pdf generated successfully! Size: {os.path.getsize(pdf_abs)} bytes.")
else:
    print("Error: PDF was not generated!")

if os.path.exists("temp_guide.html"):
    os.remove("temp_guide.html")
