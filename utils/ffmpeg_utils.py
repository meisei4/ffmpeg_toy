import subprocess
import sys


def run_command(cmd: list) -> None:
    """Run a command via subprocess and exit on error."""
    print("Running command:")
    print(" ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("Command failed!")
        sys.exit(1)


def copy_file(input_file: str, output_file: str) -> None:
    """Copy file directly without processing."""
    print("No processing parameters provided; copying file directly.")
    cmd = ["ffmpeg", "-y", "-i", input_file, "-c", "copy", output_file]
    run_command(cmd)
