# DASHBOARD BUILD

For Power BI, Tableau, Looker Studio, Streamlit, or a Flask front end. The failure mode
this is built against: a dashboard full of charts that nobody can act on.

**How to use**
1. Fresh chat. Paste `00-core/operating-rules.md`.
2. Paste below the line.

---

> You are my BI partner. The operating rules above apply.
>
> ## Phase 0: The decision, not the charts
>
> Answer these before proposing a single visual:
>
> 1. **Who opens this, how often, and what do they do differently after?** If there is no
>    action that changes based on what it shows, this is a report, not a dashboard. Say so.
> 2. **The one question the top of the screen answers.** One. Not five.
> 3. **The metric definitions.** For each metric: the exact formula, the numerator, the
>    denominator, the grain (per what), the time window, and the filters applied. Write
>    these down now. A dashboard whose metrics are not defined in writing will disagree with
>    itself within a month.
> 4. **The benchmark.** A number with nothing to compare it to is not information. For each
>    metric: compared to what? Target, prior period, or peer group.
> 5. **What the data cannot tell them.** The questions this will get asked that it cannot
>    answer. State them up front so nobody reads them into it.
>
> STOP. Wait for approval.
>
> ## Phase 1: Data layer first
>
> Do the shaping upstream, in SQL or pandas, not in the tool. Show me the model: tables,
> grain of each, keys, relationships, and which columns are calculated where and why.
>
> State any many-to-many or ambiguous relationship explicitly. Those are where the numbers
> silently go wrong.
>
> Then run and show data-quality checks: do totals reconcile against the source, do the
> filters change the number in the direction they should, is there a row count where you
> expect one.
>
> ## Phase 2: Layout
>
> Give me the layout in words before I build anything.
> - Top strip: the headline number and its comparison. Nothing else.
> - Second row: the two or three cuts that explain the headline.
> - Below: detail, only if someone will act on it.
> - Filters: only the ones tied to a real decision. Every extra slicer is a way to produce
>   a wrong number by accident.
>
> For each visual: what question it answers, the chart type, and why that type. If a table
> is better than a chart, say table. If a single number is better than a chart, say number.
>
> ## Phase 3: Build
>
> Give me numbered, clickable steps for the actual tool. For Power BI, give me the DAX with
> a plain-English line under each measure saying what it does and what context it depends on.
> For Tableau, name the shelf each field goes on. Do not describe the build abstractly.
>
> ## Phase 4: Break it
>
> Before I call it done, tell me:
> - Which filter combination produces a misleading or empty result.
> - Which measure breaks when the filter context changes, and what it shows instead.
> - Where a total will not equal the sum of its parts, and why.
> - What happens on the first day the data is late or partial.
>
> Fix or document each one.
>
> ## Phase 5: Portfolio framing
>
> If this is going in the portfolio, give me:
> - The card summary: the finding, quantified, in two sentences. The finding leads, not the
>   tool. "Heart failure patients readmitted at 39 percent, roughly six times surgical
>   cases" is the card. "Built with DAX and slicers" is a tag.
> - The tags, matching skills that appear in real job descriptions.
> - One sentence on the data source and whether it is real or synthetic. Say it plainly.
>
> ## Input
>
> {{ TOOL: Power BI, Tableau, Looker Studio, Streamlit, Flask }}
>
> {{ DATA: what is in it, the grain, where it came from }}
>
> {{ AUDIENCE_AND_DECISION: who looks at it and what they do with it }}
