from displacy.main import serve


def main():

    text = "Welcome to the Bank of China. Welcome to the Bank of China. Welcome to the Bank of China."

    span_ex = {
        "text": text,
        "spans": [
            {"start_token": 0, "end_token": 10, "label": "ORG"},
            {
                "start_token": 15,
                "end_token": 28,
                "label": "GPE",
                "sublabel": "sublabel",
                "tags": ["active"],
            },
        ],
        "tokens": list(text),
    }

    serve([span_ex] * 5, auto_select_port=True)


if __name__ == "__main__":
    main()
