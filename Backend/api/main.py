from pathlib import Path
import pandas as pd
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Backend.algorithm.pipeline import run_pipeline


app = FastAPI(
    title="Trading Dashboard API",
    version="1.0.0"
)


# =====================================================================
# CORS
# =====================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================================
# PATH CONFIG
# =====================================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DATE = "2026-01-01"

MARKET_CAP_PATH = (
    BASE_DIR
    / "sample_data"
    / "market_cap"
    / f"{DATA_DATE}.csv"
)

VOLUME_PATH = (
    BASE_DIR
    / "sample_data"
    / "trading_volume"
    / f"{DATA_DATE}.csv"
)


# =====================================================================
# HEALTH
# =====================================================================

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# =====================================================================
# PIPELINE API
# =====================================================================

@app.get("/api/pipeline")
def get_pipeline():

    market_cap_df = pd.read_csv(MARKET_CAP_PATH)

    volume_df = pd.read_csv(VOLUME_PATH)

    result = run_pipeline(
        market_cap_df,
        volume_df
    )

    return result


# =====================================================================
# TEST API
#
# Frontend KHÔNG tự chạy test.
# Frontend chỉ gọi endpoint này.
#
# Endpoint này thực sự chạy:
#     python -m pytest Backend/tests
#
# Sau đó đọc file JUnit XML để lấy kết quả từng test.
# =====================================================================

@app.get("/api/tests")
def run_tests():

    # Tạo file XML tạm để pytest ghi kết quả
    temp_file = tempfile.NamedTemporaryFile(
        suffix=".xml",
        delete=False
    )

    xml_path = Path(temp_file.name)

    temp_file.close()

    try:

        # -------------------------------------------------------------
        # Chạy pytest thật
        # -------------------------------------------------------------

        command = [
            sys.executable,
            "-m",
            "pytest",
            "Backend/tests",
            "-q",
            "--junitxml",
            str(xml_path),
        ]

        process = subprocess.run(
            command,
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        # -------------------------------------------------------------
        # Đọc kết quả JUnit XML
        # -------------------------------------------------------------

        tests = []

        total = 0
        passed = 0
        failed = 0
        skipped = 0

        if xml_path.exists():

            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Có thể là <testsuites> hoặc <testsuite>
            suites = []

            if root.tag == "testsuite":
                suites = [root]

            elif root.tag == "testsuites":
                suites = root.findall("testsuite")

            for suite in suites:

                for testcase in suite.findall("testcase"):

                    total += 1

                    name = testcase.attrib.get(
                        "name",
                        "unknown"
                    )

                    classname = testcase.attrib.get(
                        "classname",
                        ""
                    )

                    duration = testcase.attrib.get(
                        "time",
                        "0"
                    )

                    status = "passed"

                    if testcase.find("failure") is not None:
                        status = "failed"
                        failed += 1

                    elif testcase.find("error") is not None:
                        status = "error"
                        failed += 1

                    elif testcase.find("skipped") is not None:
                        status = "skipped"
                        skipped += 1

                    else:
                        passed += 1

                    tests.append({
                        "name": name,
                        "classname": classname,
                        "duration": float(duration),
                        "status": status,
                    })

        # -------------------------------------------------------------
        # Kết quả tổng
        # -------------------------------------------------------------

        return {
            "success": process.returncode == 0,
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "tests": tests,
            "stdout": process.stdout,
            "stderr": process.stderr,
        }

    finally:

        # Xóa XML tạm sau khi đọc xong
        if xml_path.exists():
            xml_path.unlink()