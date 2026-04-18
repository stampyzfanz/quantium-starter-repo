# Quantium starter repo
This repo contains everything you need to get started on the program! Good luck!

## Python setup with uv

Set up the virtual environment and install dependencies:

```bash
uv venv
source .venv/bin/activate
uv sync
```

To add more packages later:

```bash
uv add <package>
```

## Run the dashboard

Start the Dash app from the repository root:

```bash
source .venv/bin/activate
python dash/app.py
```

Then open the local URL shown in the terminal (typically `http://127.0.0.1:8050/`).
