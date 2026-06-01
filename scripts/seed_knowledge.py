"""Seed the Qdrant vector store with mock IT runbooks."""

from pathlib import Path

from src.infrastructure.vector_store import VectorStore


def _load_runbooks(data_dir: Path) -> list[dict]:
    runbooks = []
    for path in sorted(data_dir.glob("*.md")):
        content = path.read_text()
        title = path.stem.replace("-", " ").title()
        runbooks.append({"title": title, "content": content, "tags": [path.stem]})
    return runbooks


def main() -> None:
    data_dir = Path(__file__).resolve().parent.parent / "data" / "runbooks"
    if not data_dir.exists():
        msg = f"Runbooks directory not found: {data_dir}"
        raise FileNotFoundError(msg)

    runbooks = _load_runbooks(data_dir)
    if not runbooks:
        print("No runbooks found.")
        return

    store = VectorStore()
    store.ingest(runbooks)
    collection = store.client.get_collections().collections[0].name
    print(f"Ingested {len(runbooks)} runbooks into Qdrant collection '{collection}'.")


if __name__ == "__main__":
    main()
