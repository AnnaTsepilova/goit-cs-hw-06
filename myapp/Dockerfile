# Base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /myapp

# Copy files
COPY . /myapp

# Install dependencies
RUN pip install --no-cache-dir -r /myapp/requirements.txt

# Expose ports
EXPOSE 3000
EXPOSE 5000

# Run the app
CMD ["python", "main.py"]
