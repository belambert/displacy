
from displacy import serve


def main():

    span_ex = {
        "text": "Welcome to the Bank of China.",
        "spans": [
            {"start_token": 3, "end_token": 6, "label": "ORG"},
            {"start_token": 5, "end_token": 6, "label": "GPE"},
        ],
        "tokens": ["Welcome", "to", "the", "Bank", "of", "China", "."],
        }

    serve(span_ex, style="span", auto_select_port=True, manual=True)

if __name__ == "__main__":
    main()