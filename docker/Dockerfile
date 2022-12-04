FROM python:3.10.8

WORKDIR /home/jupyter

# Install MuseScore for visualizations
RUN apt-get update && apt-get install musescore -y
ENV MUSE_SCORE_PATH=/usr/bin/mscore

# Install poetry
RUN pip install 'poetry==1.2.2'

COPY musii_kit musii_kit
COPY README.md README.md
COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
COPY script/install_kernel.sh install_kernel.sh
COPY examples /home/jupyter/examples

RUN useradd jupyter
RUN chown -R jupyter /home/jupyter

USER jupyter
RUN poetry run ./install_kernel.sh

WORKDIR /home/jupyter/examples

ENTRYPOINT ["poetry", "run", "jupyter", "notebook"]
CMD ["--ip=0.0.0.0"]