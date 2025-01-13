import sqlite
import requests



def load_env() -> dict[str, str]:
    return {
        "repositories": "https://github.com/marnagy/MastersProject"
    }