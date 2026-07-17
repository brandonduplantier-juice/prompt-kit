# GIT WORKFLOW (PowerShell)

~instructions~

## 1. Start a new repo from a template

1. Copy the template folder to where the project will live.

```powershell
Copy-Item -Recurse "C:\Users\brand\prompt-kit\templates\flask-service" "C:\Users\brand\my-projects\NEW-PROJECT"
cd "C:\Users\brand\my-projects\NEW-PROJECT"
```

2. Rename the gitignore file. It ships as `gitignore.txt` so that copying the template does
   not accidentally hide files.

```powershell
Rename-Item gitignore.txt .gitignore
```

3. Create the virtual environment and install. A virtual environment is a private Python
   install for this project only, so one project's packages cannot break another's.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

4. Confirm the scaffold runs before you change anything.

```powershell
python -m pytest -q
```

5. Create `.env` from the example and fill in real values. `.env` is gitignored.

```powershell
Copy-Item .env.example .env
notepad .env
```

6. Initialize git and push. Create the empty repo on GitHub first, with no README and no
   gitignore, or step 7 will conflict.

```powershell
git init
git add -A
git commit -m "Initial commit from flask-service template"
git branch -M main
git remote add origin https://github.com/brandonduplantier-juice/NEW-PROJECT.git
git push -u origin main
```

## 2. Add the prompt kit to your GitHub

1. Extract the zip.

```powershell
Expand-Archive -Force "D:\users\brand\downloads\prompt-kit-v1.zip" "C:\Users\brand\prompt-kit"
```

2. Confirm the files landed.

```powershell
Get-ChildItem -Recurse "C:\Users\brand\prompt-kit" | Select-Object FullName
```

3. Create an empty repo named `prompt-kit` at https://github.com/new. Do not let GitHub add
   a README, a license, or a gitignore.

4. Initialize and push.

```powershell
cd "C:\Users\brand\prompt-kit"
git init
git add -A
git commit -m "Add prompt kit: operating rules, prompts, templates, conventions"
git branch -M main
git remote add origin https://github.com/brandonduplantier-juice/prompt-kit.git
git push -u origin main
```

5. Verify the push landed.

```powershell
git log --oneline -1
git remote -v
```

## 3. Everyday commits

```powershell
git add -A
git commit -m "Message here"
git push
```

Note: a commit message containing a dollar sign needs a backtick in front of it in
PowerShell, or PowerShell tries to read it as a variable and eats it.

```powershell
git commit -m "Fix `$49k quoting bug"
```

## 4. Check before you push

1. Confirm no secret is about to be committed.

```powershell
git diff --cached | Select-String -Pattern "api_key|secret|token|password" -CaseSensitive:$false
```

2. Confirm no em-dash or en-dash is in the changed files. This greps the whole repo.

```powershell
Get-ChildItem -Recurse -File -Include *.md,*.py,*.txt | Select-String -Pattern "[\u2013\u2014]"
```

No output means clean.

3. Confirm `.env` is not tracked.

```powershell
git ls-files | Select-String -Pattern "\.env$"
```

No output means clean. If it prints `.env`, stop and fix it before pushing.

```powershell
git rm --cached .env
git commit -m "Remove .env from tracking"
```

Then rotate the key. Removing it from tracking does not remove it from history, and the
key is already exposed.

## 5. When Render does not redeploy

1. Confirm the push actually reached GitHub.

```powershell
git log --oneline -1
git status
```

2. If the branch is not `main`, Render is watching a branch you did not push to. Check the
   branch Render is configured to auto-deploy from.

3. Check the Render build log for a missing environment variable. That is the most common
   cause of a build that succeeds locally and fails on deploy.

## Notes

1. The `warning: LF will be replaced by CRLF` message on Windows is normal and is not an
   error. Ignore it.
2. `*.bak` is in the gitignore. Backup files should never be committed.
3. Never force push to `main` on a repo that is auto-deploying. There is no undo on the
   deploy that follows.
