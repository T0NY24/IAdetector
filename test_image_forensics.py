"""
Test script para el módulo Image Forensics v3.0
UIDE Forense AI

⚠️ Este script NO usa app.py, ni video, ni audio.
Solo prueba el detector de imágenes.
"""

from modules.image_forensics import ImageForensicsDetector
from PIL import Image


def main():
    detector = ImageForensicsDetector(device="cpu")

    img = Image.open("samples/test.png").convert("RGB")

    result = detector.analyze(img)

    print("\n=== RESULTADO FORENSE ===")
    print("Veredicto:", result.verdict)
    print("Confianza:", result.confidence)

    print("\nScores:")
    for k, v in result.scores.items():
        print(f"  {k}: {v:.3f}")

    print("\nEvidencia:")
    for e in result.evidence:
        print(" -", e)

    if result.notes:
        print("\nNotas:", result.notes)


if __name__ == "__main__":
    main()
