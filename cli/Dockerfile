
# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD https://github.com/freehci/freehci-appliance/archive/refs/heads/main.zip /app

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y unzip && \
    unzip main.zip && \
    cd freehci-appliance-main && \
    pip install --no-cache-dir -r requirements.txt

# Copy the configuration to the right place (NOTE: You must ensure that this file exists on the host machine)
COPY /etc/freehci/settings.json /etc/freehci/settings.json

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["uvicorn", "freehci-appliance-main/main:app", "--host", "0.0.0.0", "--port", "8000"]
