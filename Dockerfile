FROM python:3
ADD . /mbcrawl/
WORKDIR /mbcrawl
RUN pip install -r requirements.txt
RUN groupadd -r mbcrawl && useradd -r -g mbcrawl mbcrawl && chown -R mbcrawl /mbcrawl
EXPOSE 6023
USER mbcrawl