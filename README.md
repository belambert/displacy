
# displaCy

Fork of spaCy's displaCy.

Span style input similar to what's described here:
https://spacy.io/usage/visualizers#manual-usage

Example input:

```json
{
    "text": "Welcome to the Bank of China.",
    "spans": [
        {"start_token": 3, "end_token": 6, "label": "ORG"},
        {"start_token": 5, "end_token": 6, "label": "GPE", "sublabel": "country", "tags": ["asia"]},
    ],
    "tokens": ["Welcome", "to", "the", "Bank", "of", "China", "."],
}
```

# TODO

- [ ] move color into classes
- [ ] move height into classes
- [ ] cleanup `_assemble_per_token_info()`?
- [ ] update docstrings
- [ ] add tests
- [ ] handle text direction and language?
- [ ] handle KB link stuff?
- [ ] remove "options"?
- [ ] deal with escape_html() and other stuff in utils
- [ ] wsgiref?
- [ ] better handling of CSS
