# Web-based Collaborative Real-time Code Editor

## Using Redis Docker Image (for Redis Channel Layer Used by Django Channels Library)

![Docker Image](https://img.shields.io/docker/v/mohsen2000/redis/latest)

To start using the Redis Docker image, follow these steps:

---

**Step 1:** Pull the Docker Image

```bash
docker pull mohsen2000/redis:latest
```
**Step 2:** Step 2: Run the Container

```bash
docker run --name your-redis-container -d mohsen2000/redis:latest
```

## Getting Started with the Django Project

To get your Django project up and running in development mode, follow these steps:

---

**Step 1:** Clone the Repository

```bash
git clone https://github.com/mohsen-y/editor.git
cd editor/app/
```
**Step 2:** Set Up a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```
**Step 3:** Install Dependencies

```bash
pip install -r requirements.txt
```
**Step 4:** Configure the Database

```bash
python manage.py migrate
```
**Step 5:** Start the Development Server

```bash
python manage.py runserver
```

## Accessing your Application
Open your web browser and go to http://127.0.0.1:8000/.
