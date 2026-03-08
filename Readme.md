`django-admin startproject <project-name>` to start a project  
`./.venv/scripts/activate.bat` to activate the virtual environment  
`py manage.py runserver` to run the app  
`python -m venv djangovenv` to create a virtual environment

## Django Backend — Quick Start

This repository contains a Django backend with a `userAuth` app (MongoDB + JWT).

Core setup and common commands (these exact command snippets are preserved below and should not be removed):

`django-admin startproject <project-name>` to start a project  
`./.venv/scripts/activate.bat` to activate the virtual environment  
`py manage.py runserver` to run the app  
`python -m venv djangovenv` to create a virtual environment  
to run that environment `djangoenv/Scripts/activate`  
to push the code to github `git push origin master`

Recommended quick workflow

1. Create and activate the virtual environment (example):

```powershell
python -m venv djangovenv
```

On Windows (PowerShell):

```powershell
djangovenv\Scripts\Activate.ps1
```

On Windows (cmd):

```cmd
djangovenv\Scripts\activate.bat
```

2. Install dependencies (inside venv):

```powershell
pip install -r requirements.txt
```

3. Run the development server:

```powershell
py manage.py runserver
```

4. Git notes

- If your local branch is `master` and you want to push to `main`, either push `master` directly:

```bash
git push origin master
```

- Or rename the branch to `main` (recommended modern default) and push:

```bash
git branch -m master main
git push origin main
```

Notes

- The project uses MongoDB Atlas for persistence. Connection URI is configured in `userAuth/views.py`.
- API reference is in `docs/api-guide.md`.
- When changing API shapes or routes, update `docs/api-guide.md` (see `.github/copilot-instructions.md`).

If you want, I can also create a `requirements.txt` and add a short start script.
