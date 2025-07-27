# Use a slim Python image compatible with AMD64 architecture
FROM --platform=linux/amd64 python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install necessary Python packages
# pdfminer.six is used for PDF parsing and text extraction with layout information
RUN pip install pdfminer.six

# Copy the main application script into the container
COPY main.py .

# Create input and output directories as expected by the challenge
# These directories will be mounted as volumes during runtime
RUN mkdir -p input output

# Set the entrypoint for the container.
# This command will be executed when the container starts.
# It runs the main.py script which processes PDFs from /app/input
# and saves the results to /app/output.
ENTRYPOINT ["python", "main.py"]
