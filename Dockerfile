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
#RUN chmod +x app/start_vpn.sh

# Run the VPN script when the container starts

COPY vpnbook /vpnbook
COPY start_vpn.sh /start_vpn.sh
RUN chmod +x /start_vpn.sh

# Create /dev/net directory and /dev/net/tun device
#RUN mkdir -p /dev/net && \
    #mknod /dev/net/tun c 10 200 && \
    #chmod 600 /dev/net/tun


RUN pip3 install --no-cache-dir --upgrade --requirement requirements.txt

# Expose your port
EXPOSE 7860
#CMD ["sh","/start_vpn.sh"]
CMD ["python", "-u","-m", "YukkiMusic"]
