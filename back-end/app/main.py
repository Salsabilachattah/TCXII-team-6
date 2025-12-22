"""
Simple CLI runner for the backend app.

Usage (PowerShell):
  python main.py ingest
  python main.py query --q "your question"

This script calls `rag.ingest.ingest_docs()` to build the vectorstore
and `rag.vectorstore.retrieve()` to query it.
"""
import argparse
import sys

from rag import ingest, vectorstore


def run_ingest():
	try:
		ingest.ingest_docs()
	except Exception as e:
		print("Ingestion failed:", e)
		raise


def run_query(q: str, k: int = 4):
	try:
		results = vectorstore.retrieve(q, k=k)
		if not results:
			print("No results found")
			return

		for i, doc in enumerate(results, start=1):
			# langchain Document has `page_content` and `metadata`
			content = getattr(doc, "page_content", str(doc))
			metadata = getattr(doc, "metadata", {}) or {}
			source = metadata.get("source")
			print(f"--- Result {i} (source={source}) ---\n{content}\n")
	except Exception as e:
		print("Query failed:", e)
		raise


def main():
	parser = argparse.ArgumentParser(description="Backend app CLI")
	sub = parser.add_subparsers(dest="cmd")

	sub.add_parser("ingest", help="Ingest docs to build vectorstore")

	qparser = sub.add_parser("query", help="Query the vectorstore")
	qparser.add_argument("--q", required=True, help="Query text")
	qparser.add_argument("--k", type=int, default=4, help="Number of results")

	args = parser.parse_args()

	if args.cmd == "ingest":
		run_ingest()
	elif args.cmd == "query":
		run_query(args.q, k=args.k)
	else:
		parser.print_help()
		sys.exit(1)


if __name__ == "__main__":
	main()

