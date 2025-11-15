# Base image with Python 3.11 and NodeJS 20
FROM nikolaik/python-nodejs:python3.11-nodejs20

# Update & install required packages
RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -u 10001 -m botuser


# Set working directory
WORKDIR /app

# Copy app code and VPN scripts
COPY --chown=10001:10001 . /app

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade --requirement requirements.txt

# Expose your port
EXPOSE 7860

# Switch to non-root user
USER 10001

# Run your bot
CMD ["python", "-u", "-m", "YukkiMusic"]
