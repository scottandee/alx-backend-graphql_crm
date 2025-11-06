# Testing the Celery Setup
This readme describes the steps to test celery setup

## Prerequisites
- Python environment (virtualenv or venv recommended)
- Redis running and accessible (default: redis://localhost:6379/0)
- Project dependencies installed (requirements.txt)

## Quick start

1. Install Redis (one of these options)
    - System:  
      ```bash
      sudo apt-get install redis-server
      sudo systemctl start redis
      ```
    - Docker:
      ```bash
      docker run -d --name redis -p 6379:6379 redis:6
      ```

2. Install Python dependencies
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3. Run database migrations
    ```bash
    python manage.py migrate
    ```

4. Start the Celery worker (run in a new terminal)
    ```bash
    celery -A crm worker -l info
    ```

5. Start Celery Beat (run in a new terminal)
    ```bash
    celery -A crm beat -l info
    ```

6. Verify logs
    - The process writes logs to `/tmp/crm_report_log.txt`. Inspect them with:
      ```bash
      tail -f /tmp/crm_report_log.txt
      ```