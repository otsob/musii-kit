FROM python:3.12

WORKDIR /home/jupyter

# Install Rust
ENV CARGO_HOME=/home/jupyter/.cargo
ENV RUSTUP_HOME=/home/jupyter/.rustup
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="${CARGO_HOME}/bin:${PATH}"

# Install poetry
RUN pip install 'poetry==2.3.3'

COPY musii_kit musii_kit
COPY README.md README.md
COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
COPY install_kernel.sh install_kernel.sh
COPY examples /home/jupyter/examples

RUN useradd jupyter
RUN chown -R jupyter /home/jupyter
USER jupyter

RUN poetry run ./install_kernel.sh --no-cache

# Remove
RUN rustup self uninstall -y
WORKDIR /home/jupyter/examples

ENTRYPOINT ["poetry", "run", "jupyter", "notebook"]
CMD ["--ip=0.0.0.0"]
