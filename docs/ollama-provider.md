# Ollama-Provider – Lokale Uebersetzung

Seit Juni 2026 unterstuetzt die Werkbank auch **lokale Modelle** ueber
Ollama. Damit koennen Uebersetzungen ohne API-Key und ohne Internet
durchgefuehrt werden.

## Voraussetzungen

1. **Ollama installieren**  
   Download unter [ollama.com/download](https://ollama.com/download)  
   (Windows: Ollama laeuft als Hintergrunddienst auf `localhost:11434`)

2. **Modell pullen**  
   ```bash
   ollama pull gemma4:2b    # kleines Modell, CPU-geeignet
   ollama pull gemma4:12b   # groesseres Modell (empfohlen, braucht GPU)
   ```

3. **Ollama laeuft** (Standard-Port 11434)

## Verwendung

### CLI

```bash
# Mit Standard-Modell (gemma4:2b)
python tools/translate_chapter.py --book anna-karenina --chapter 001 --provider ollama

# Mit bestimmtem Modell
python tools/translate_chapter.py --book peter-i-buch-01 --chapter 005 --provider ollama --model ollama/gemma4:12b

# Batch-Lauf
python tools/translate_batch.py --book anna-karenina --missing --provider ollama --model ollama/gemma4:12b
```

### Dashboard

Im Dashboard unter `Provider` einfach **ollama** auswaehlen und in der
Modellgruppe `Ollama` das gewuenschte lokale Modell waehlen.

## Architektur

Der `OllamaClient` in `tools/lib/ollama_client.py` ist analog zum
`OpenRouterClient` aufgebaut:

- Sendet POST an `http://localhost:11434/api/chat`
- Erwartet das Ollama-Response-Format (`message.content`)
- Loggt `eval_count` statt Token (Ollama zaehlt anders)
- Unterstuetzt Retry bei Timeout/5xx (max_retries=2)

Der `--provider ollama` wurde in folgenden Komponenten ergaenzt:

| Komponente | Aenderung |
|---|---|
| `tools/lib/ollama_client.py` | **NEU** – der Client |
| `config/models.yaml` | Eintraege `ollama/gemma4:2b` und `ollama/gemma4:12b` |
| `tools/translate_chapter.py` | `choices` erweitert, Modellauswahl, Client-Init, Error-Handling |
| `tools/translate_batch.py` | `choices` erweitert, Modelluebergabe |
| `tools/dashboard.py` | Provider-Radio, `provider_action`, Batch-Logik, Stiltest |
| `README.md` | Provider-Liste erweitert |

## Fehlerbehandlung

- **Ollama nicht gestartet:** Connection-Refused → Fehlermeldung
- **Modell nicht vorhanden:** Ollama laedt es automatisch (erster Aufruf
  dauert entsprechend laenger)
- **5xx von Ollama:** automatischer Retry (2 Versuche)