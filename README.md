# NDVI Calculator (FastAPI + minimal UI)

Minimalny projekt do policzenia NDVI z dwoch plikow GeoTIFF (RED + NIR).

- Backend: `app.py` (FastAPI, obliczenia w Pythonie)
- Frontend: `web/index.html` (minimalny UI w przegladarce)
- Lokalne dane testowe: wrzuc pliki `.tif` do `ndvi/` (nie sa w repozytorium — GitHub ma limit ~100 MB na plik)

## Wymagania

- conda env `ndvi` z zainstalowanym: `rasterio`, `numpy`, `matplotlib`
- Python pakiety serwerowe: z `server_requirements.txt`

## Uruchomienie lokalnie

```bash
conda activate ndvi
cd /ścieżka do folderu roboczego
pip install -r server_requirements.txt
uvicorn app:app --reload --port 8000
```

Otworz w przegladarce:
- `http://127.0.0.1:8000`

Wgraj dwa pliki GeoTIFF:
- RED band (np. Sentinel-2 B04)
- NIR band (np. Sentinel-2 B08)

Backend zwraca podglad NDVI jako PNG (nie zapisuje wyniku na dysk).

<img width="892" height="636" alt="image" src="https://github.com/user-attachments/assets/8cbaa4d0-5536-47a2-8e22-81f747b39f3c" />

