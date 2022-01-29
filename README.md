# Emotional App

Bachelor Thesis application. Created by Aleksandra Świerkowska, Mateusz Ogrodowczyk, Piotr Góreczny, Wiktor Górczak. Poznań 2022

## Setup
### Prerequisites
In order to run the application, you need to have GNU/Linux operating system with Docker installed.

### Build and run containers
Before the application can be started, you need to make sure that Docker is running on your machine. In case of most contemporary Linux distribution you can do it as follows:
```sh
sudo systemctl status docker
```
If it is not running, you can start it using:
```sh
sudo systemctl start docker
```

In order to build and run the application, enter the project's root directory and execute the following commands:
```sh
docker-compose build
docker-compose up
```

### Stopping the containers
The containers can be stopped simply by pressing `Ctrl+C` and then, typing the following command:
```sh
docker-compose down
```

## Using the application
You can enter the dashboard with your web browser of choice. By default, the FastAPI container should be listening at the port `8000` so you just need to use the following URL:
```
http://localhost:8000/
```
