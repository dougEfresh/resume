#!/usr/bin/env python3
import argparse
import base64
import itertools
import logging
import os
import shutil
import subprocess
import sys
import tempfile

import markdown

preamble = """\
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
"""

postamble = """\
</body>
</html>
"""

# https://unix.stackexchange.com/a/439956/20079
CHROME_GUESSES_LINUX = [
    "/".join((path, executable))
    for path, executable in itertools.product(
        (
            "/usr/local/sbin",
            "/usr/local/bin",
            "/usr/sbin",
            "/usr/bin",
            "/sbin",
            "/bin",
            "/opt/google/chrome",
        ),
        ("google-chrome", "chrome", "chromium", "chromium-browser"),
    )
]


def guess_chrome_path() -> str:
    guesses = CHROME_GUESSES_LINUX
    for guess in guesses:
        if os.path.exists(guess):
            logging.info("Found Chrome or Chromium at " + guess)
            return guess
    raise ValueError("Could not find Chrome. Please set CHROME_PATH.")


def make_html(page1: str , page2: str, prefix: str = "resume") -> str:
    """
    Compile md to HTML and prepend/append preamble/postamble.

    Insert <prefix>.css if it exists.
    """
    try:
        with open(prefix + ".css") as cssfp:
            css = cssfp.read()
    except FileNotFoundError:
        print(prefix + ".css not found. Output will by unstyled.")
        css = ""
    return "".join(
        (
            preamble.format(title='Douglas Chimento', css=css),
            '<div class=resume>',
            markdown.markdown(page1, extensions=["smarty"]),
            '</div>',
            '<div class=resume>',
            markdown.markdown(page2, extensions=["smarty"]),
            '</div>',
            postamble,
        )
    )


def write_pdf(html: str, prefix: str = "resume", chrome: str = "") -> None:
    """
    Write html to prefix.pdf
    """
    chrome = chrome or guess_chrome_path()

    html64 = base64.b64encode(html.encode("utf-8"))
    options = [
        "--headless",
        "--print-to-pdf-no-header",
        "--enable-logging=stderr",
        "--log-level=2",
    ]
    # https://bugs.chromium.org/p/chromium/issues/detail?id=737678
    if sys.platform == "win32":
        options.append("--disable-gpu")

    tmpdir = tempfile.TemporaryDirectory(prefix="resume.md_")
    options.append(f"--crash-dumps-dir={tmpdir.name}")
    options.append(f"--user-data-dir={tmpdir.name}")
    try:
        subprocess.run(
            [
                chrome,
                *options,
                f"--print-to-pdf={prefix}.pdf",
                "data:text/html;base64," + html64.decode("utf-8"),
            ],
            check=True,
        )
        logging.info(f"Wrote {prefix}.pdf")
    except subprocess.CalledProcessError as exc:
        if exc.returncode == -6:
            logging.warning(
                "Chrome died with <Signals.SIGABRT: 6> "
                f"but you may find {prefix}.pdf was created successfully."
            )
        else:
            raise exc
    finally:
        # We use this try-finally rather than TemporaryDirectory's context
        # manager to be able to catch the exception caused by
        # https://bugs.python.org/issue26660 on Windows
        try:
            shutil.rmtree(tmpdir.name)
        except PermissionError as exc:
            logging.warning(f"Could not delete {tmpdir.name}")
            logging.info(exc)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        help="markdown input file [resume.md]",
        default="resume.md",
        nargs="?",
    )
    parser.add_argument(
        "--no-html",
        help="Do not write html output",
        action="store_true",
    )
    parser.add_argument(
        "--no-pdf",
        help="Do not write pdf output",
        action="store_true",
    )
    parser.add_argument(
        "--chrome-path",
        help="Path to Chrome or Chromium executable",
    )
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args()

    if args.quiet:
        logging.basicConfig(level=logging.WARN, format="%(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    prefix, _ = os.path.splitext(args.file)

    with open('page1.md') as mdfp:
        p1 = mdfp.read()

    with open('page2.md') as mdfp:
        p2 = mdfp.read()

    html = make_html(p1, p2, prefix=prefix)

    if not args.no_html:
        with open(prefix + ".html", "w") as htmlfp:
            htmlfp.write(html)
            logging.info(f"Wrote {htmlfp.name}")

    if not args.no_pdf:
        write_pdf(html, prefix=prefix, chrome=args.chrome_path)
