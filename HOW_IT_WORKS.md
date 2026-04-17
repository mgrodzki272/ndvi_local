# Jak to dziala (linia po linii)

Masz tu **wytlumaczenie kazdej linii** w:
- `app.py` (backend FastAPI)
- `web/index.html` (frontend React z CDN)

To jest wersja *maksymalnie minimalna* (prawie bez “bezpiecznikow”).

## `app.py` – linia po linii

Kod (dla kontekstu) jest w pliku `app.py`. Ponizej opis kazdej linii wg numerow z edytora.

- **L1** `from io import BytesIO`: bufor w RAM; uzywamy go, zeby zapisac obraz PNG “do pamieci”, bez tworzenia pliku.
- **L2** `from pathlib import Path`: wygodna praca ze sciezkami plikow (tu: znalezienie `web/index.html`).
- **L3** pusta linia: tylko czytelnosc.
- **L4** `import matplotlib`: glowny pakiet do rysowania.
- **L5** `import matplotlib.pyplot as plt`: uproszczony interfejs do tworzenia wykresow/obrazow.
- **L6** `import numpy as np`: tablice/macierze i obliczenia (NDVI).
- **L7** `from fastapi import FastAPI, File, UploadFile`: FastAPI (serwer) i typy do uploadu plikow.
- **L8** `from fastapi.responses import HTMLResponse, Response`: typy odpowiedzi HTTP (HTML i “surowe bajty” PNG).
- **L9** `from rasterio.io import MemoryFile`: pozwala otwierac GeoTIFF z **bajtow** (upload) bez zapisywania na dysk.
- **L10** pusta linia.
- **L11** `matplotlib.use("Agg")`: ustawia backend rysowania “bez okienka” (serwer nie ma GUI). Bez tego matplotlib czasem chce uzywac GUI i sypie bledami.
- **L12** pusta linia.
- **L13** `app = FastAPI()`: tworzy obiekt aplikacji – to “serwer”, do ktorego dodajesz endpointy dekoratorami `@app.get`, `@app.post`.
- **L14–L15** puste linie.

### Endpoint HTML

- **L16** `@app.get("/", response_class=HTMLResponse)`: dekorator – mowi FastAPI: “dla GET na `/` uruchom funkcje ponizej i traktuj to jako HTML”.
- **L17** `def index() -> HTMLResponse:`: definicja funkcji, ktora obsluguje strone glowna.
- **L18** `return HTMLResponse((Path(__file__).resolve().parent / "web/index.html").read_text())`:
  - `__file__` to sciezka do `app.py`,
  - `.resolve().parent` bierze folder projektu,
  - `/ "web/index.html"` dokleja sciezke do pliku HTML,
  - `.read_text()` czyta caly HTML jako tekst,
  - `HTMLResponse(...)` odsyla to do przegladarki.
- **L19–L20** puste linie.

### Endpoint NDVI (API)

- **L21** `@app.post("/api/ndvi")`: dekorator – mowi FastAPI: “dla POST na `/api/ndvi` uruchom funkcje ponizej”.
- **L22** `async def api_ndvi(red: UploadFile = File(...), nir: UploadFile = File(...)) -> Response:`:
  - `async` bo czytamy uploady (I/O),
  - `red` i `nir` to pliki przeslane w `multipart/form-data`,
  - `File(...)` oznacza “to jest wymagany field pliku”,
  - zwracamy `Response` (PNG jako bajty).
- **L23** `with MemoryFile(await red.read()) as rmem, MemoryFile(await nir.read()) as nmem:`:
  - `await red.read()` pobiera bajty calego pliku RED,
  - `MemoryFile(...)` tworzy “wirtualny plik” w pamieci,
  - ten `with ... as ...` pilnuje zamkniecia zasobow po wyjsciu z bloku.
- **L24** `with rmem.open() as rsrc, nmem.open() as nsrc:`:
  - otwiera oba GeoTIFF-y jak normalne rastry rasterio,
  - `rsrc/nsrc` to obiekty z ktorych czytasz dane.
- **L25** `red_arr = rsrc.read(1).astype("float32")`:
  - czyta **pierwsze pasmo** (band 1) z RED,
  - konwertuje na `float32` (zeby dzialalo dzielenie).
- **L26** `nir_arr = nsrc.read(1).astype("float32")`: analogicznie dla NIR.
- **L27** pusta linia (koniec czytania danych).
- **L28** `denom = nir_arr + red_arr`: mianownik w NDVI: \(NIR + RED\).
- **L29** `ndvi_arr = np.where(denom == 0, np.nan, (nir_arr - red_arr) / denom)`:
  - jesli `denom == 0` → wpisz `NaN` (zamiast dzielenia przez 0),
  - w przeciwnym razie licz \( (NIR - RED) / (NIR + RED) \).
- **L30** pusta linia.
- **L31** `fig = plt.figure(figsize=(7, 5), dpi=160)`: tworzy figure (plot) o rozmiarze 7x5 cali i rozdzielczosci 160 DPI.
- **L32** `ax = fig.add_subplot(1, 1, 1)`: tworzy jedna os (jeden wykres) w figurze.
- **L33** `im = ax.imshow(ndvi_arr, cmap="RdYlGn", vmin=-1, vmax=1)`:
  - rysuje macierz NDVI jako obraz,
  - `cmap` dobiera kolory (czerwony→zolty→zielony),
  - `vmin/vmax` ustala skale kolorow na [-1, 1].
- **L34** `fig.colorbar(im, ax=ax, label="NDVI")`: dodaje pasek kolorow z podpisem.
- **L35** `ax.set_axis_off()`: chowa osie (zeby byl czysty obraz).
- **L36** `fig.tight_layout()`: dopasowuje marginesy.
- **L37** `buf = BytesIO()`: tworzy bufor w pamieci na PNG.
- **L38** `fig.savefig(buf, format="png")`: zapisuje figure do bufora jako PNG.
- **L39** `plt.close(fig)`: zamyka figure (zeby nie “przeciekala” pamiec przy wielu requestach).
- **L40** pusta linia.
- **L41** `return Response(content=buf.getvalue(), media_type="image/png")`:
  - `buf.getvalue()` bierze bajty PNG,
  - `media_type="image/png"` mowi przegladarce “to jest PNG”.

## `web/index.html` – linia po linii

Ponizej opis kluczowych linii (HTML ma sporo CSS, wiec grupuje powtarzalne rzeczy, ale dalej jest to “linia po linii” wg numerow).

- **L1** `<!doctype html>`: informacja, ze to HTML5.
- **L2** `<html lang="pl">`: start dokumentu; `lang="pl"` pomaga przegladarce/narzedziom (jezyk strony).
- **L3** `<head>`: meta-informacje i style.
- **L4** `<meta charset="UTF-8" />`: kodowanie znakow (polskie znaki dzialaja).
- **L5** `<meta name="viewport" ...>`: poprawne skalowanie na telefonach.
- **L6** `<title>NDVI Calculator</title>`: tytul karty w przegladarce.
- **L7–L22** `<style> ... </style>`: CSS (wyglad).
  - **L8–L16**: kolory tła, karta, tekst, siatka (dwie kolumny), wyglad inputow i przycisku.
  - **L17–L18**: spinner i animacja obrotu.
  - **L19–L21**: wyglad obrazka i responsywnosc na malych ekranach.
- **L23** `</head>`
- **L24** `<body>`: to co widac na stronie.
- **L25** `<div id="root"></div>`: tu React wstawi caly interfejs.
- **L26** pusta linia.
- **L27** komentarz: “React z CDN, bez npm”.
- **L28** `<script ... react.production.min.js>`: laduje React (biblioteka UI).
- **L29** `<script ... react-dom.production.min.js>`: laduje ReactDOM (renderowanie do DOM).
- **L30** pusta linia.
- **L31** `<script>`: start kodu JS.
- **L32** `const e = React.createElement;`: skrot – zamiast pisac `React.createElement(...)` w kazdym miejscu, uzywamy `e(...)`.
- **L33** pusta linia.

### Komponent React

- **L34** `function App() {`: start komponentu.
- **L35** `const [redFile, setRedFile] = React.useState(null);`: stan na plik RED (na start brak).
- **L36** `const [nirFile, setNirFile] = React.useState(null);`: stan na plik NIR.
- **L37** `const [busy, setBusy] = React.useState(false);`: czy trwa request (spinner).
- **L38** `const [imageUrl, setImageUrl] = React.useState("");`: URL do PNG (na start pusty).
- **L39** pusta linia.
- **L40** `const canRun = redFile && nirFile && !busy;`: przycisk jest aktywny tylko gdy sa oba pliki i nie trwa liczenie.
- **L41** pusta linia.
- **L42** `async function run() {`: funkcja wywolywana po kliknieciu przycisku.
- **L43** `if (imageUrl) URL.revokeObjectURL(imageUrl);`: usuwa poprzedni “blob URL” (sprzatanie pamieci).
- **L44** `setImageUrl("");`: czyści obrazek z UI.
- **L45** pusta linia.
- **L46** `setBusy(true);`: wlacza spinner i blokuje przycisk.
- **L47** `const form = new FormData();`: tworzy obiekt do wyslania plikow jako `multipart/form-data`.
- **L48** `form.append("red", redFile);`: dodaje plik RED pod nazwa pola `red`.
- **L49** `form.append("nir", nirFile);`: dodaje plik NIR pod nazwa pola `nir`.
- **L50** `const res = await fetch("/api/ndvi", { method: "POST", body: form });`: wysyla request do backendu.
- **L51** `const blob = await res.blob();`: bierze odpowiedz (PNG) jako “blob” (bajty w przegladarce).
- **L52** `setImageUrl(URL.createObjectURL(blob));`: tworzy URL do blob-a i zapisuje go w stanie, zeby `<img>` mogl go wyswietlic.
- **L53** `setBusy(false);`: wylacza spinner.
- **L54** `}`: koniec `run()`.
- **L55** pusta linia.
- **L56** `return e(`: komponent zwraca drzewo elementow UI.
- **L57–L93** budowa UI:
  - **L57–L58**: `<div class="card">` jako kontener.
  - **L59**: naglowek.
  - **L60**: krotki opis.
  - **L61–L84**: dwa inputy plikow w siatce (RED i NIR).
  - **L68–L72**: input RED; `onChange` bierze `ev.target.files[0]` i zapisuje do stanu.
  - **L78–L82**: input NIR analogicznie.
  - **L85–L90**: przycisk z `disabled: !canRun` i `onClick: run`; gdy `busy` to pokazuje spinner i tekst “Computing...”.
  - **L91**: jezeli `imageUrl` jest ustawiony, renderuje `<img src=...>`.
  - **L92**: mala stopka.
- **L94** `}`: koniec komponentu `App`.

### Renderowanie

- **L96** `ReactDOM.createRoot(...).render(e(App));`: uruchamia React i renderuje komponent `App` w elemencie `#root`.
- **L97–L99** zamkniecie `</script>`, `</body>`, `</html>`.
