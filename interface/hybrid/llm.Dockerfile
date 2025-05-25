FROM python:3.9

# Set the working directory to /app
WORKDIR .

# Copy the current directory contents into the container at /app
ADD . .

# COPY llm.py .
RUN rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install openai flask

EXPOSE 50

CMD ["python", "llm.py"]
