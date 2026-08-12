import json
import os
import shutil
import subprocess
import tempfile


SLITHER_TIMEOUT = 60


def run_slither_scan(contract_path: str) -> dict:
    """
    Run Slither static analysis.

    The Solidity contract is analyzed statically.
    It is never deployed or executed.
    """

    if not os.path.exists(contract_path):
        raise RuntimeError(
            f"Contract file does not exist: {contract_path}"
        )

    temp_dir = tempfile.mkdtemp(
        prefix="contractshield_"
    )

    try:
        analysis_contract_path = os.path.join(
            temp_dir,
            "contract.sol",
        )

        shutil.copyfile(
            contract_path,
            analysis_contract_path,
        )

        output_path = os.path.join(
            temp_dir,
            "slither-output.json",
        )

        command = [
            "slither",
            analysis_contract_path,
            "--json",
            output_path,
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=SLITHER_TIMEOUT,
        )

        if os.path.exists(output_path):
            with open(
                output_path,
                "r",
                encoding="utf-8",
            ) as f:
                slither_data = json.load(f)

            return {
                "success": True,
                "data": slither_data,
            }

        error_message = (
            result.stderr.strip()
            or result.stdout.strip()
            or "Slither analysis failed."
        )

        return {
            "success": False,
            "error": error_message,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": (
                f"Slither analysis timed out "
                f"after {SLITHER_TIMEOUT} seconds."
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }

    finally:
        shutil.rmtree(
            temp_dir,
            ignore_errors=True,
        )