## Git branch switching: simple guide

A short, safe workflow for switching branches and starting features.

### 1) Basics
- Create and switch to a new branch:
```bash
git switch -c feature/<short-name>
```
- Switch to an existing branch:
```bash
git switch <branch>
```

### 2) Before switching branches
Make sure your working directory is clean:
```bash
git status
```
If you have changes:
- Commit them:
```bash
git add -A
git commit -m "feat: short summary"
```
- Or temporarily stash them:
```bash
git stash push -u -m "wip: switching branches"
```
- After stash and checkout to the new branch, you can pop the latest stash:
```bash
git stash pop
```

### 3) Start a new feature from the latest main
```bash
git fetch origin
git switch main
git pull --rebase
git switch -c feature/<short-name>
```

### 4) Keep your feature branch up to date
```bash
git fetch origin
git rebase origin/main
# If conflicts appear: fix files, then
git add <fixed-file>
git rebase --continue
# If you need to stop the rebase:
git rebase --abort
```

### 5) Push and open a PR
```bash
git push -u origin feature/<short-name>
```

### 6) Check out an existing remote branch
```bash
git fetch origin
git switch --track origin/<branch>
```

### 7) After your PR is merged (cleanup)
```bash
git switch main
git pull --rebase
git branch -d feature/<short-name>          # delete local
git push origin --delete feature/<short-name>  # delete remote (if needed)
```

### Handy commands
```bash
git branch -vv   # show local branches with upstreams
git switch -     # go back to previous branch
git branch -m <new-name>   # rename current branch
```

### Quick tips
- Keep commits small and commit often.
- Avoid force-pushing shared branches.
- Ask for help if a rebase or conflict looks confusing.


