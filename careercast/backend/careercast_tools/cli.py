"""Local file-based CLI; credentials and user databases are not required."""
import argparse
import json
import sys
from pathlib import Path
from . import __version__


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(value, path=None):
    text = json.dumps(value, indent=2, ensure_ascii=False)
    if path:
        Path(path).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="careercast", description="CareerCast structured-profile tools")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ["profile", "predict", "recommend", "gap-report", "export", "batch", "cohort"]:
        cmd = commands.add_parser(name)
        cmd.add_argument("input", help="UTF-8 profile JSON (list for batch/cohort)")
        cmd.add_argument("--output")
        if name in ["predict", "recommend", "export", "batch", "cohort"]:
            cmd.add_argument("--k", type=int, default=5, choices=range(1, 11))
        if name in ["gap-report", "export"]:
            cmd.add_argument("--career", required=name == "gap-report")
        if name == "gap-report":
            cmd.add_argument("--format", choices=["json", "csv"], default="json")
    parse = commands.add_parser("parse", help="Extract entities from a local PDF/DOCX resume")
    parse.add_argument("input"); parse.add_argument("--output")
    serve = commands.add_parser("serve", help="Start the authenticated REST API")
    serve.add_argument("--host", default="127.0.0.1"); serve.add_argument("--port", type=int, default=8000)
    review = commands.add_parser("review", help="Start the optional Streamlit review app")
    review.add_argument("--api-url", default="http://127.0.0.1:8000")
    review.add_argument("--port", type=int, default=8501)
    args = parser.parse_args(argv)
    try:
        if args.command == "review":
            import os
            from streamlit.web import cli as streamlit_cli
            os.environ["CAREERCAST_API_URL"] = args.api_url
            sys.argv = ["streamlit", "run", str(Path(__file__).with_name("review.py")), "--server.address", "127.0.0.1", "--server.port", str(args.port)]
            streamlit_cli.main()
            return
        if args.command == "serve":
            import uvicorn
            uvicorn.run("app.main:app", host=args.host, port=args.port)
            return
        if args.command == "parse":
            from app.parser import extract_text, parse_resume
            source = Path(args.input)
            result = parse_resume(extract_text(source.read_bytes(), source.name))
            write_json(result, args.output)
            return
        source = read_json(args.input)
        if args.command in ["batch", "cohort"]:
            from .batch import predict_batch, cohort_summary
            result = predict_batch(source, args.k)
            write_json(cohort_summary(result) if args.command == "cohort" else result, args.output)
            return
        from app.schemas import ProfileBase
        profile = ProfileBase.model_validate(source).model_dump()
        if args.command == "profile":
            write_json(profile, args.output)
        elif args.command == "gap-report":
            from app.gaps import gap_report, gap_csv
            result = gap_report(profile, args.career)
            if args.format == "csv":
                if not args.output:
                    parser.error("CSV export requires --output")
                Path(args.output).write_text(gap_csv(result), encoding="utf-8")
            else:
                write_json(result, args.output)
        else:
            from app.intelligence import predict
            result = predict(profile, args.k)
            if args.command == "export":
                if not args.output:
                    parser.error("PDF export requires --output")
                if args.career and args.career not in {r["career"] for r in result["recommendations"]}:
                    raise ValueError("Select a recommended career or increase --k")
                from app.pdf_report import build_career_pdf
                Path(args.output).write_bytes(build_career_pdf(profile, result, args.career))
            else:
                write_json(result, args.output)
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
