import tempfile
import subprocess
import os
import platform

# CHANGE ONLY IF Windows soffice is NOT in PATH
SOFFICE_WINDOWS_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"

def get_libreoffice_cmd():
    system = platform.system().lower()

    if system == "windows":
        # Prefer full path (safe for Django & venv)
        if os.path.exists(SOFFICE_WINDOWS_PATH):
            return SOFFICE_WINDOWS_PATH
        return "soffice"
    else:
        # Linux / macOS
        return "libreoffice"


def convert_word_binary_to_pdf(word_binary_data):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".doc") as temp_word:
        temp_word.write(word_binary_data)
        temp_word_path = temp_word.name

    temp_pdf_path = temp_word_path.replace(".doc", ".pdf")
    libreoffice_cmd = get_libreoffice_cmd()

    try:
        command = [
            libreoffice_cmd,
            "--headless",
            "--nologo",
            "--norestore",
            "--invisible",
            "--nodefault",
            "--nolockcheck",
            "--nofirststartwizard",
            "--convert-to", "pdf",
            "--outdir", os.path.dirname(temp_word_path),
            temp_word_path,
        ]

        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        with open(temp_pdf_path, "rb") as pdf_file:
            return pdf_file.read()

    except Exception as e:
        print("Conversion failed:", e)
        return None

    finally:
        try:
            os.remove(temp_word_path)
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)
        except:
            pass
