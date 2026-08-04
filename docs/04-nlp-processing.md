"""# FASE 4 — Procesamiento de Noticias (NLP)

## Objetivo

Procesar y enriquecer noticias con limpieza, deduplicación, NER (extracción de entidades), clasificación y análisis de sentimiento.

---

## Arquitectura

### Pipeline NLP

```
Raw News Article
    ↓
[1] Cleaning
    - Strip HTML
    - Remove URLs & emails
    - Normalize whitespace
    ↓
[2] Deduplication
    - Levenshtein similarity
    - Remove duplicates
    ↓
[3] Language Detection
    - Detect language (es, en, etc)
    ↓
[4] Named Entity Recognition
    - Extract: Countries, companies, people, products
    - Extract keywords (noun chunks)
    ↓
[5] Classification
    - TF-IDF + Logistic Regression
    - Categories: OPEC, refinery, geopolitics, supply, demand, other
    ↓
[6] Sentiment Analysis
    - Negative (-1), neutral (0), positive (1)
    - Confidence score
    ↓
Enriched News Article
```

---

## Componentes

### 1. NewsClener (`cleaner.py`) ✅

Limpieza y normalización de texto:

```python
strip_html()              # Remover tags HTML
normalize_whitespace()    # Normalizar espacios/saltos
remove_urls()            # Remover URLs
remove_email()           # Remover emails
remove_extra_punctuation() # Limpiar puntuación
clean_text()             # Pipeline completo
```

### 2. NewsDeduplicator (`deduplicator.py`) ✅

Deduplicación usando similitud:

```python
hash_title()             # Hash rápido de títulos
levenshtein_distance()   # Distancia editorial
similarity_score()       # Score 0-1
is_duplicate()          # Detectar duplicados
deduplicate_batch()     # Limpiar lote
```

**Algoritmo**: Levenshtein distance con early termination.

### 3. LanguageDetector (`lang_detector.py`) ✅

Detección de idioma:

```python
detect_language()        # Detectar idioma
detect_probabilities()   # Probabilidades por idioma
is_supported_language()  # Verificar soporte
```

**Soporta**: Español (es), Inglés (en), Francés, Portugués, Alemán.

### 4. NamedEntityRecognizer (`ner.py`) ✅

Extracción de entidades con spaCy:

```python
extract_entities()       # Extraer: países, empresas, personas
extract_keywords()       # Extraer noun phrases
```

**Modelos**: es_core_news_sm (español), en_core_web_sm (inglés).

### 5. NewsClassifier (`classifier.py`) ✅

Clasificación TF-IDF + Logistic Regression:

```python
train()                 # Entrenar en ejemplos etiquetados
classify()              # Clasificar artículo
classify_with_confidence() # Con scores de confianza
is_relevant()          # ¿Es relevante para precios combustible?
```

**Categorías**:
- opec — Anuncios OPEP
- refinery — Problemas refinería
- geopolitics — Eventos geopolíticos
- supply — Temas suministro
- demand — Temas demanda
- other — Otros

### 6. SentimentAnalyzer (`sentiment.py`) ✅

Análisis de sentimiento:

```python
train()                 # Entrenar en ejemplos etiquetados
analyze()              # Sentimiento (-1, 0, 1)
analyze_with_score()   # Con score continuo -1 a 1
is_negative()          # ¿Es negativo?
is_positive()          # ¿Es positivo?
```

### 7. NewsProcessingPipeline (`pipeline.py`) ✅

Orquestador que ejecuta todos los pasos:

```python
process_single()       # Procesar 1 artículo
process_batch()        # Procesar lote
deduplicate_batch()    # Desduplicar lote
```

---

## Archivos Creados

**Componentes NLP** (7 archivos):
- `nlp/cleaner.py` — Limpieza de texto
- `nlp/deduplicator.py` — Deduplicación
- `nlp/lang_detector.py` — Detección de idioma
- `nlp/ner.py` — Extracción de entidades
- `nlp/classifier.py` — Clasificación
- `nlp/sentiment.py` — Análisis de sentimiento
- `nlp/pipeline.py` — Pipeline completo

**Tests** (1 archivo):
- `tests/unit/test_nlp_components.py` — Tests de componentes

---

## Uso

### Procesar Un Artículo

```python
from petro.nlp.pipeline import NewsProcessingPipeline

pipeline = NewsProcessingPipeline()

result = await pipeline.process_single(
    title="Precios del petróleo suben por crisis OPEP",
    content="Los precios del Brent han subido..."
)

print(result)
# {
#     "title": "...",
#     "content": "...",
#     "language": "es",
#     "entities": {"countries": ["..."], "companies": [...]},
#     "keywords": ["..."],
#     "classification": "opec",
#     "sentiment": {"sentiment": 1, "score": 0.85, ...}
# }
```

### Procesar Lote

```python
articles = [
    {"title": "...", "content": "..."},
    {"title": "...", "content": "..."},
]

results = await pipeline.process_batch(articles)
```

### Desduplicar

```python
titles = ["Oil prices rise", "Oil prices rise today", "Gas prices fall"]
unique, indices = await pipeline.deduplicate_batch(titles, threshold=0.85)
```

---

## Integración con BD

En FASE 8 (Automatización), los resultados se guardan:

```python
# Tabla: news
news = News(
    title=result["title"],
    content=result["content"],
    language=result["language"],
    classification=result["classification"],
    entities=result["entities"],  # JSON
    sentiment_score=result["sentiment"]["score"],
    is_duplicate=0,
)
```

---

## Testing

```bash
# Tests de NLP
pytest tests/unit/test_nlp_components.py -v
```

Cubre:
- Limpieza de HTML
- Normalización de whitespace
- Deduplicación
- Detección de idioma
- Similitud de textos

---

## Mejoras Futuras

1. **Transformers BERT**: Clasificación más exacta (requiere más recursos)
2. **Análisis de sentimiento con BERT**: Mayor precisión
3. **Extracción de eventos**: Fecha/hora de eventos
4. **Relaciones entre entidades**: ¿Quién afecta a quién?
5. **Sumarización automática**: Generar resumen de artículo
6. **Fact-checking**: Validar afirmaciones
7. **Caching de embeddings**: Redis para embeddings vectoriales

---

## Stack Técnico

- **Limpieza**: regex, HTMLParser
- **Similitud**: Levenshtein (editdistance)
- **Idiomas**: langdetect
- **NER**: spaCy
- **Clasificación**: scikit-learn (TF-IDF + LogisticRegression)
- **Sentimiento**: scikit-learn (TF-IDF + LogisticRegression)

---

**Estado**: ✅ Completada  
**Archivos**: 8 (7 componentes + 1 test)  
**Líneas de código**: ~1500  
**Tests**: 12+ casos unitarios
"""
