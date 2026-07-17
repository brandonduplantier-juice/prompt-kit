# PORTFOLIO WRITE-UP

You do this after every project: a card for the portfolio site, a repo README, a resume
bullet, and a LinkedIn line. This makes it one pass instead of four improvised ones.

**How to use:** fresh chat, paste `00-core/operating-rules.md`, then below the line.

---

> You are writing up a finished project for a job search. The operating rules above apply,
> plus these:
>
> - **Every number must come from something I gave you.** If a metric is not in my input,
>   you do not have it. Do not estimate, round up, or infer one. Ask.
> - **No adjectives about quality.** Not "robust", "comprehensive", "sophisticated",
>   "cutting-edge". The work is the claim.
> - **The finding leads, the tool follows.** A recruiter reads the outcome. The stack is a tag.
> - **Say plainly if the data is synthetic or public.** Do not let a reader think a teaching
>   dataset was a client engagement. This is a real disqualifier if it surfaces in an interview.
> - **No em-dashes or en-dashes.** Check the output before sending.
>
> ## Step 1: Interrogate before writing
>
> Ask me for anything missing from the input. Specifically, do not write until you have:
> the quantified outcome, the data source and whether it is real, the actual hard part, and
> what I would say when asked "why did you do it that way."
>
> If I gave you a project with no quantified outcome, tell me that directly. It will get
> asked about and there is no writing around it.
>
> ## Step 2: Find the real signal
>
> Tell me first, before any drafting:
> - Which part of this a hiring manager actually cares about, and which part I am proud of
>   that they will not care about. These are usually different.
> - Which skills claimed here are demonstrated versus merely present. A tag I cannot defend
>   in an interview is a liability, not an asset.
> - Which named skills from real job descriptions this project now lets me claim honestly.
>
> ## Step 3: Produce all four
>
> 1. **Portfolio card.** Title, one-line subtitle, a summary of two to three sentences
>    leading with the quantified finding, three highlight bullets covering what was hard
>    and how it was solved, and tags. Match the existing `PROJECTS` array object shape in
>    `src/App.jsx` if this is going to the React portfolio: `id`, `title`, `folder`, `date`,
>    `tags`, `summary`, `highlights`, `cover`, `repo`, `link`.
> 2. **Repo README.** Overview, the question, data source with its limits stated, method,
>    results with the numbers, how to reproduce (exact commands), and what it does not do.
> 3. **Resume bullet.** One line. Verb, what I built, the quantified result. Under 30 words.
> 4. **LinkedIn project entry.** Two sentences plus the skills to attach.
>
> ## Step 4: Interview prep
>
> The three hardest questions this project invites, and the honest answers. Include at least
> one question about a weakness in it. If the honest answer to any of them is bad, tell me
> now rather than letting me find out live.
>
> ## Step 5: Self-check
>
> Before sending, confirm each: no em-dash or en-dash present, every number traceable to my
> input, no quality adjectives, data provenance stated plainly, every tag defensible.
>
> ## Input
>
> {{ PROJECT: what it is, what it does }}
>
> {{ OUTCOME: the quantified result, exact numbers }}
>
> {{ DATA: source, real or synthetic, size, date }}
>
> {{ HARD_PART: what actually broke and how it got fixed }}
>
> {{ STACK: tools used }}
>
> {{ LINKS: live URL, repo URL }}
