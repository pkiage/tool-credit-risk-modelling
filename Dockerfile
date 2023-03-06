# read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# you will also find guides on how best to write your Dockerfile

FROM python:3.9

RUN apt update 

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user

# Switch to the "user" user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Copy the current directory contents into the container at $HOME/app setting the owner to the user
COPY --chown=user . $HOME/app

RUN apt install -y graphviz

# WORKDIR /code

COPY ./requirements.txt $HOME/app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r $HOME/app/requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]