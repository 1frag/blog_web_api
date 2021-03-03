# pull official base image
FROM python:3.9.1

# set work directory
WORKDIR /code

# copy requirements file
COPY requirements/requirements.txt /deps/requirements.txt

# install dependencies
RUN pip install -r /deps/requirements.txt

# copy project
COPY backend /code
