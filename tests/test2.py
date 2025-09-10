# test2.py — robust CSV + per-row progress logs
import argparse, csv, json, os, sys, ast
import pandas as pd, requests

def call_api(api_url: str, prompt: str, multi_label: bool, timeout: float):
    r = requests.get(api_url, params={"prompt": prompt, "multi_label": str(multi_label).lower()}, timeout=timeout)
    r.raise_for_status()
    return r.json()

def parse_themes_cell(cell):
    if pd.isna(cell): return []
    txt = str(cell).strip()
    if not txt: return []
    try:
        data = json.loads(txt)
    except Exception:
        try:
            data = ast.literal_eval(txt)
        except Exception:
            return []
    out = []
    for item in data:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            try:
                out.append((str(item[0]), round(float(item[1]), 2)))
            except Exception:
                pass
    return out

def extract_topn(df_results: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    df = df_results.copy()
    df["themes_list"] = df["themes_json"].apply(parse_themes_cell)
    def get_theme(lst, idx):
        try: return lst[idx]
        except Exception: return (None, None)
    out = pd.DataFrame({"prompt": df["prompt"]})
    for i in range(n):
        tcol, pcol = f"theme{i+1}", f"prob{i+1}"
        out[tcol], out[pcol] = zip(*df["themes_list"].apply(lambda lst, i=i: get_theme(lst, i)))
    return out

def autodetect_text_col(df: pd.DataFrame):
    candidates = ["statement","statements","text","prompt","utterance","message","content","input","sentence","review","comment","body"]
    lower = {c.lower(): c for c in df.columns}
    for k in candidates:
        if k in lower: return lower[k]
    for c in df.columns:
        if df[c].dtype == "object": return c
    return df.columns[0]

def safe_read_csv(path: str, sep_arg: str | None):
    def try_read(sep, loose=False):
        kwargs = dict(dtype=str, engine="python")
        if sep is None:
            kwargs.update(dict(sep=None))  # auto-sniff
        else:
            kwargs.update(dict(sep=sep))
        if loose:
            kwargs.update(dict(on_bad_lines="skip"))
        return pd.read_csv(path, **kwargs)

    try:
        df = try_read(sep_arg, loose=False)
        return df, None, False
    except Exception:
        last_err = None

    for sep in [",", ";", "\t", "|"]:
        try:
            df = try_read(sep, loose=False)
            return df, sep, False
        except Exception as e:
            last_err = e

    try:
        total_lines = sum(1 for _ in open(path, "r", encoding="utf-8", errors="ignore"))
        df = try_read(sep_arg, loose=True)
        skipped = max((total_lines - 1) - len(df), 0)
        return df, None, skipped
    except Exception:
        for sep in [",", ";", "\t", "|"]:
            try:
                total_lines = sum(1 for _ in open(path, "r", encoding="utf-8", errors="ignore"))
                df = try_read(sep, loose=True)
                skipped = max((total_lines - 1) - len(df), 0)
                return df, sep, skipped
            except Exception as e:
                last_err = e

    raise RuntimeError(f"Failed to read CSV. Last error: {last_err}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True, help="Input CSV with statements")
    p.add_argument("--text-col", default=None, help="Column with text (auto-detected if omitted)")
    p.add_argument("--out", default=None, help="Output CSV for raw results (default: <csv>_results.csv)")
    p.add_argument("--out-top3", default=None, help="Output CSV for top-3 (default: <csv>_results_top3.csv)")
    p.add_argument("--url", default="http://127.0.0.1:8000/predict_theme", help="Endpoint URL")
    p.add_argument("--multi-label", default="true", choices=["true","false"])
    p.add_argument("--sep", default=None, help="Delimiter; if omitted, auto-detect")
    p.add_argument("--limit", type=int, default=0, help="Process only first N rows if >0")
    p.add_argument("--timeout", type=float, default=20.0, help="Per-request timeout (s)")
    args = p.parse_args()

    multi_label = args.multi_label == "true"

    in_path = os.path.abspath(args.csv)
    base = os.path.splitext(os.path.basename(args.csv))[0]
    out_path = os.path.abspath(args.out or f"{base}_results.csv")
    out_top3_path = os.path.abspath(args.out_top3 or f"{base}_results_top3.csv")

    print("=== Batch tester starting ===", flush=True)
    print(f"Input:  {in_path}", flush=True)
    print(f"Outputs:\n  - {out_path}\n  - {out_top3_path}", flush=True)
    print(f"URL: {args.url} | multi_label: {multi_label} | timeout: {args.timeout}s", flush=True)

    if not os.path.exists(in_path):
        print(f"[FATAL] Input CSV not found: {in_path}", file=sys.stderr); sys.exit(1)

    try:
        df_in, used_sep, skipped = safe_read_csv(in_path, args.sep)
    except Exception as e:
        print(f"[FATAL] Could not read CSV: {e}", file=sys.stderr); sys.exit(1)

    print(f"[INFO] Detected delimiter: {repr(used_sep) if used_sep is not None else 'auto'}", flush=True)
    if skipped:
        print(f"[WARN] Parsed in loose mode; skipped ~{skipped} malformed line(s).", flush=True)

    text_col = args.text_col or autodetect_text_col(df_in)
    if text_col not in df_in.columns:
        print(f"[FATAL] Text column '{text_col}' not in {list(df_in.columns)}", file=sys.stderr); sys.exit(1)
    print(f"[INFO] Using text column: {text_col}", flush=True)

    texts = df_in[text_col].astype(str)
    if args.limit > 0:
        texts = texts.head(args.limit)
    total = len(texts)
    print(f"[INFO] Loaded {len(df_in)} rows from CSV; will process {total} text rows.", flush=True)

    if total == 0:
        print("[FATAL] No non-empty texts to process. Check delimiter/column.", file=sys.stderr)
        sys.exit(1)

    # Step 1: call API -> results CSV
    ok, err = 0, 0
    with open(out_path, "w", newline="", encoding="utf-8") as f_out:
        w = csv.writer(f_out)
        w.writerow(["prompt", "themes_json"])
        for i, prompt in enumerate(texts, start=1):
            if not isinstance(prompt, str) or not prompt.strip():
                print(f"[{i}/{total}] (empty) — skipped", flush=True)
                continue

            preview = (prompt[:80] + "…") if len(prompt) > 80 else prompt
            print(f"[{i}/{total}] sending → {preview}", flush=True)

            try:
                resp = call_api(args.url, prompt.strip(), multi_label=multi_label, timeout=args.timeout)
                w.writerow([prompt, json.dumps(resp.get("themes", []), ensure_ascii=False)])
                print(f"[{i}/{total}] ✅ OK", flush=True)
                ok += 1
            except Exception as e:
                w.writerow([prompt, json.dumps({"error": str(e)})])
                print(f"[{i}/{total}] ❌ ERROR: {e}", file=sys.stderr, flush=True)
                err += 1

    print(f"[INFO] Raw results written to: {out_path}  (ok={ok}, err={err})", flush=True)

    # Step 2: expand top-3 -> results_top3 CSV
    df_results = pd.read_csv(out_path)
    if not {"prompt","themes_json"}.issubset(df_results.columns):
        print(f"[FATAL] Expected 'prompt' and 'themes_json' in {out_path}", file=sys.stderr); sys.exit(1)

    df_top3 = extract_topn(df_results, n=3)
    df_top3.to_csv(out_top3_path, index=False)
    print(f"[INFO] Top-3 results written to: {out_top3_path}", flush=True)
    print("=== Done ===", flush=True)

if __name__ == "__main__":
    main()
