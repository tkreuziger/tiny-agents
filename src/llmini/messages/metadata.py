import datetime as dt


def make_metadata(**metadata_kwargs: str) -> dict[str, str]:
    return {
        "created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **metadata_kwargs,
    }
