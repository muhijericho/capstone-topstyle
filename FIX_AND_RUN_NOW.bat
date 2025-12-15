@echo off
echo Clearing Python cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
echo Cache cleared!
echo.
echo Starting Django server...
python manage.py runserver
pause























