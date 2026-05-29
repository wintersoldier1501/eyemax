@echo off
set JAVA_HOME=C:\Users\Accesorizate1\java\17.0.13+11
set PATH=C:\Users\Accesorizate1\java\17.0.13+11\bin;C:\Users\Accesorizate1\PortableGit\cmd;%PATH%
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
..\.venv\Scripts\python.exe -c "import ssl; ssl._create_default_https_context = ssl._create_unverified_context; import flet_cli.cli; flet_cli.cli.main()" build apk --no-rich-output --yes -v
