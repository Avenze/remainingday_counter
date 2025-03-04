# remainingday_counter
A simple Python app utilizing ntfy.sh for counting down until a defined date finishes.
Stupid project I made in school for counting down until our year finishes.

# Running using Docker Compose
1. Add this docker-compose.yml
2. Set environment variables
3. Start using docker compose up

```yml
version: '3.8'

services:
  counterapp:
    image: 'ghcr.io/avenze/remainingday_counter:master'
    container_name: counterapp
    environment:
      - NTFY_SERVER=http://ntfy-server:5001  # Modify this with your actual server URL
      - NTFY_TOPIC=counterapp # Might want to modify this, OPTIONAL
      - SKIP_DATES=2025-04-07,2025-04-08,2025-04-09,2025-04-10,2025-04-11,2025-04-14,2025-04-15,2025-04-16,2025-04-17,2025-04-18,2025-04-21,2025-05-01,2025-05-02,2025-05-29,2025-05-30,2025-06-05,2025-06-06
```
