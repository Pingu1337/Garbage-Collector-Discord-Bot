# Garbage Collector Discord Bot

A discord bot that deletes messages after a set amount of time in a set channel.

## Clone the project and host your own bot

You can clone this repo and compose your own docker image or just run it as it is. To do this make sure you create a `.env` file in the root repository which includes your `DISCORD_TOKEN`.

## Docker

Get up and running with the [docker image](https://hub.docker.com/repository/docker/pingudock/discord-gc)

_*Make sure to pass your `DISCORD_TOKEN` as an envoirment variable.*_

<br/>

> _The docker image only gives server administrators the permision to execute the bot commands_

### **AMD64:**

- `docker volume create gc-vol`
- docker run -e "DISCORD_TOKEN=<your_discord_token>" -v gc-vol:/etc/gcbot -d pingudock/discord-gc:latest

### **ARM64:**

- `docker volume create gc-vol`
- docker run -e "DISCORD_TOKEN=<your_discord_token>" -v gc-vol:/etc/gcbot -d pingudock/discord-gc:arm64
