# PhantomLedger recording script (2–3 minutes)

**0:00 — Open the app**  
Open `http://127.0.0.1:8000` in the browser.  
Say: “A repository is more than its current files. It carries experiments, reversals, notes, and decisions that can disappear from view. PhantomLedger is a local archaeology tool for recovering those traces.”

**0:18 — Create the demo history**  
Click **Create Haunted Demo Repository** and wait for the ledger to load.  
Say: “I’m creating a synthetic Git repository right here on this machine. It has an abandoned cache branch, an unfinished dashboard, an authentication transition, and a migration note that survives later commits.”

**0:38 — Show the analysis and ledger**  
Point at the repository path and stat cards, then scroll through several Memory Ledger cards and filters.  
Say: “The counts and findings come from Git commands. PhantomLedger has identified deleted files, a repeated edit trail, an explicit revert, an unmerged branch, and a long-lived TODO. These are deterministic findings, not model guesses.”

**1:00 — Open the reverted dashboard memory**  
Choose **Reverted** and select the dashboard revert memory. Point to commits, dates, files, and evidence.  
Say: “Here is the dashboard prototype’s historical echo. The evidence shows the introduction and the Git revert. The record displays the commit messages and file names so you can check the claim yourself.”

**1:25 — Ask Gemma**  
Click **Ask the Archivist**. If Ollama is installed, show the structured response; otherwise show the unavailable notice.  
Say: “Now Gemma receives only this memory’s selected Git evidence. It can explain what the record supports, but it cannot establish why someone made the change. Facts remain separate from interpretation, and unknowns are called out.”

**1:52 — Repository Speaks**  
Click **Repository Speaks** and point at its dated milestones.  
Say: “The chronicle is a readable sequence of deterministic milestones. It is grounded in the same Git history, so the repository tells its story through the traces developers left behind.”

**2:12 — Local model and open innovation**  
Say: “Gemma runs locally through Ollama. Repository data is not sent to a cloud AI provider. Open-weight AI matters here because developers can run and control the model alongside private code, while Git remains the source of truth.”

**2:35 — Close**  
Say: “PhantomLedger: your repository remembers what you forgot. The codebase has a memory. Now you can read it.”
