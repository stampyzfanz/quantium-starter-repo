import csv
from pathlib import Path


def clean_num(x: str) -> str:
	if x is None:
		return ""
	return x.replace("$", "").replace(",", "").strip()


def process_pink_morsel_sales(input_files, output_path: Path):
	rows_out = []

	for f in input_files:
		with f.open(newline="") as fh:
			reader = csv.DictReader(fh)
			for r in reader:
				if r.get("product") != "pink morsel":
					continue

				qty_raw = r.get("quantity") or ""
				price_raw = r.get("price") or ""

				try:
					qty = float(clean_num(qty_raw))
					price = float(clean_num(price_raw))
				except Exception:
					continue

				sales = qty * price
				date = r.get("date") or r.get("Date") or ""
				region = r.get("region") or r.get("Region") or ""

				rows_out.append({"sales": f"{sales:.2f}", "date": date, "region": region})

	# write output CSV with required headings
	if rows_out:
		with output_path.open("w", newline="") as out_fh:
			writer = csv.DictWriter(out_fh, fieldnames=["sales", "date", "region"])
			writer.writeheader()
			for row in rows_out:
				writer.writerow(row)

	print(f"Wrote {len(rows_out)} rows to {output_path}")


if __name__ == "__main__":
	repo_root = Path(__file__).resolve().parent.parent
	data_dir = repo_root / "data"
	output_path = data_dir / "pink_morsel_sales.csv"
	input_files = sorted(data_dir.glob("daily_sales_data_*.csv"))
	process_pink_morsel_sales(input_files, output_path)

