FROM python:3.10
WORKDIR /api
ADD requirements.txt /api/requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
ADD . /api
ENTRYPOINT ["python", "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0"]
