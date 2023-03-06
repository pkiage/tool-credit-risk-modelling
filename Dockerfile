# read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# you will also find guides on how best to write your Dockerfile

FROM python:3.9

RUN apt update 

RUN apt install -y graphviz

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]