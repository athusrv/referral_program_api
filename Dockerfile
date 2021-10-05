FROM python:3

# We copy just the requirements.txt first to leverage Docker cache
COPY ./setup.py /app/setup.py
WORKDIR /app

RUN pip install wheel
RUN python setup.py develop

COPY . /app

ENV FLASK_ENV development

EXPOSE 5000

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]