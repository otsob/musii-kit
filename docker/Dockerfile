FROM python:3.11

WORKDIR /home/jupyter

# Install Rust
ENV CARGO_HOME=/home/jupyter/.cargo
ENV RUSTUP_HOME=/home/jupyter/.rustup
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="${CARGO_HOME}/bin:${PATH}"

# Install poetry
RUN pip install 'poetry==1.4.2'

COPY musii_kit musii_kit
COPY README.md README.md
COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
COPY install_kernel.sh install_kernel.sh
COPY examples /home/jupyter/examples

RUN useradd jupyter
RUN chown -R jupyter /home/jupyter
USER jupyter

RUN poetry config installer.modern-installation false
RUN poetry run ./install_kernel.sh --no-cache

# Remove
RUN rustup self uninstall -y
WORKDIR /home/jupyter/examples

ENTRYPOINT ["poetry", "run", "jupyter", "notebook"]
CMD ["--ip=0.0.0.0"]