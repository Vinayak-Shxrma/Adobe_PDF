### 🧩 Connecting the Dots Challenge - Round 1A: PDF Outline Extractor
This project presents a smart and adaptable solution for Round 1A of the Connecting the Dots Challenge. Its core objective is to accurately extract a structured outline, encompassing the document title and hierarchical headings like H1, H2, and H3, from a diverse range of PDF files.

Unlike simplistic methods that rely solely on font sizes, this solution employs a sophisticated combination of layout analysis, style profiling, and contextual rules to genuinely comprehend the inherent structure of a document.

### 💡 Key Strategy: Style Recognition + Layout Heuristics
The solution dynamically ascertains the structure of each PDF by meticulously analyzing its font styles, overall layout, and spacing. This comprehensive approach ensures remarkable adaptability across various document formats and stylistic conventions.

### 🧱 Step 1: Rich Text Element Extraction (extract_text_elements)
Leveraging pdfminer.six, the program systematically processes each page to extract comprehensive metadata for every line of text. This includes:

- ✅ Full text content

- ✅ Page number

- ✅ Font name (e.g., Arial-Bold, TimesNewRoman)

- ✅ Rounded font size

- ✅ Bold detection (inferred from font name keywords such as "Bold", "Bd", etc.)

- ✅ Position coordinates (x0, y0, x1, y1)

- ✅ Width and height of the text block

This wealth of information is paramount for understanding not just the textual content, but crucially, how it is presented.

### 🧬 Step 2: Style Analysis and Heading Mapping
Each unique combination of:

```json
(font name, rounded font size, bold status)
is treated as a distinct style signature.
```
The algorithm then ranks these unique styles based on the following criteria:

- Font size (largest first)

- Boldness (bold styles prioritized over regular)

- Frequency (most common styles ranked higher)

From this intelligent analysis, the system dynamically assigns labels such as:

- TITLE

- H1, H2, H3

- BODY (representing standard paragraph text)

This dynamic approach eliminates the necessity for hardcoded font thresholds, significantly enhancing the system's flexibility.

### 🏷️ Step 3: Accurate Title Detection
The document title typically represents the most prominent text on the first page. The algorithm identifies the title by:

- Verifying the presence of the TITLE style on page 1.
- Prioritizing text that appears at the top of the page (indicated by a higher y0 coordinate).
- Selecting the largest and boldest candidate text block.
- Crucially, removing this identified title from the remaining elements to prevent any confusion during the subsequent outline extraction process.

### 📘 Step 4: Building the Outline Hierarchy
The actual outline (comprising H1, H2, and H3 headings) is constructed through a meticulous process:

### 🚫 Step 4.1: Filter Out Non-Headings
The system intelligently skips lines that are highly likely to be non-headings, such as:

- Lines that are either too short or excessively long.
- Purely numeric lines (e.g., page numbers).
- Decorative or repetitive elements (e.g., “Page X”, footers).

### 🧭 Step 4.2: Use Layout and Font to Confirm Headings
Confirmation of headings is achieved through a combination of layout and font analysis:

- Vertical spacing: An unusually large vertical gap between two consecutive lines strongly suggests that the new line is a heading.
- Font check: Valid headings must possess a larger font size than body text or must be explicitly bold.
- No duplicates: The system meticulously avoids repeating the same heading due to minor stylistic variations.

### 🛠️ Tech Stack and Tools
```json pdfminer.six``` - Essential for extracting structured text and layout information from PDFs.

```collections.Counter``` - Utilized for efficiently ranking styles by their frequency.

```re (regex)``` - Employed for powerful pattern-based filtering of unwanted lines.

```json``` - For exporting the extracted, structured results.

### 🐳 Running the Project in Docker
This solution is designed to run within a Docker container, adhering to the challenge's requirements for portability and network isolation.

### 🔧 Prerequisites
- Install Docker Desktop or Docker CLI.

### 📁 Folder Structure

```
AdobeHackathon/
├── Dockerfile
├── main.py
├── README.md
└── input/
    ├── sample1.pdf
    └── report2.pdf
```
Place your PDF files within the input/ folder.

### 🧱 Build Docker Image
Execute the following commands in your terminal:
```
cd /path/to/AdobeHackathon
docker build --platform linux/amd64 -t pdfoutline:1a .
```
This command constructs the Docker image using your Dockerfile and installs all necessary libraries.

### 🚀 Run the Container
```
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  --network none \
  pdfoutline:1a
  ```
- --rm deletes the container automatically after execution.

- Input and output folders are securely mounted to the container.

- --network none ensures complete network isolation, preventing any internet access.

### 📂 Output
Your results will be generated in a newly created output/ folder:
```
output/
├── sample1.json
└── report2.json
Each JSON file will contain the extracted outline in the following format:
```
```

Edit
{
  "title": "Document Title",
  "outline": [
    {"level": "H1", "text": "Section Heading"},
    {"level": "H2", "text": "Subsection"},
    ...
  ]
}
```
### ✅ Summary
This advanced approach transcends simplistic font-based rules by:

- Dynamically learning document styles.

- Utilizing spacing and boldness to intelligently infer headings.

- Demonstrating robust functionality across a wide variety of document types.

It is meticulously optimized for accuracy, flexibility, and offline execution, making it an ideal solution for real-world document processing and hackathon constraints.

### Built for adaptability. Designed for accuracy.