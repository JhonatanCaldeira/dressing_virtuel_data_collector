# Use an official Python runtime as a parent image
FROM python-base:3.10-slim

# Install supervisord
RUN apt-get update && apt-get install -y supervisor
RUN mkdir -p /var/log && chmod -R 777 /var/log

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
COPY ./ /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5000 5005 5010

# Add supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]