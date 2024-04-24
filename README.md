# SitTube

SitTube is a Python-based application that streams video data into a frame buffer and provides services to retrieve and store this data. The application is containerized using Docker and orchestrated with Docker Compose for ease of use and deployment.

## Prerequisites

- Docker
- Docker Compose
- Python 3.11

## Getting Started

1. Clone the repository to your local machine.

```bash
git clone https://github.com/alvarotroya/sittube.git
```

1. Navigate to the project directory.

```bash
cd sittube
```

1. Copy the `.env.example` file to `.env` and set the environment variables.
   See [Environment Variables](#environment-variables) for more information.

```bash
cp .env.example .env
```

1. Build and run the Docker containers using Docker Compose.

```bash
docker-compose build
docker-compose up
```

The application should now be running and accessible at `localhost:8000`.

## Environment Variables

The application uses the following environment variables, which should be set in a `.env` file in the project directory:

- `VIDEO_SOURCE`: The path to the video source.
- `TARGET_LOCATION`: The path to the target location for storing data.
- `FRAME_BUFFER_SIZE`: The size of the frame buffer (default is 50).

