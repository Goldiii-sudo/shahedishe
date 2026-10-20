@echo off
echo Cleaning choco lock files...
del /f "C:\ProgramData\chocolatey\lib\cc90e8a2a7849537173aca94b54173a516df4a34" 2>nul
echo Installing Tesseract OCR...
choco install tesseract -y
echo.
echo Done. Press any key to close.
pause
