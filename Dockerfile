#FROM dperson/openvpn-client
FROM nikolaik/python-nodejs:python3.9-nodejs18
RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends ffmpeg \
    && apt-get install -y openvpn \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY . /app

RUN chmod 777 /app
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

EXPOSE 1000
RUN pip3 install --no-cache-dir --upgrade --requirement requirements.txt
# Run the VPN script when the container starts

#CMD ["sh","/start_vpn.sh"]
CMD ["python", "-u","-m", "YukkiMusic"]