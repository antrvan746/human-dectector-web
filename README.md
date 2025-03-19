# Human Detector Web Application

A full-stack web application for detecting the number of persons in uploaded images. Built with FastAPI, Next.js, and PostgreSQL.

## Features

- Image upload functionality
- Person detection (placeholder implementation)
- Persistent storage of detection results
- Modern, responsive UI

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. Clone the repository:
```bash
git clone <repository-url>
cd human-detector-web
```

2. Start the application using Docker Compose:
```bash
docker-compose up --build
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure

```
.
├── frontend/           # Next.js frontend application
├── backend/           # FastAPI backend application
├── docker-compose.yml # Docker Compose configuration
└── README.md         # This file
```

## Development

### Frontend
The frontend is built with Next.js and includes:
- TypeScript support
- Tailwind CSS for styling
- Axios for API calls

### Backend
The backend is built with FastAPI and includes:
- SQLAlchemy for database operations
- PostgreSQL database
- File upload handling
- CORS configuration

## API Endpoints

- `POST /api/detect`: Upload an image for person detection
- `GET /api/detections`: Get all previous detections

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request 