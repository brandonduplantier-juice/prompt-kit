# <Project Name>

One line: the finding, quantified.

## Question

## Data

Source, size, date range. State plainly whether it is real or synthetic, and say who
collected it and why. A teaching dataset is fine. Letting someone think it was a client
engagement is not.

## Method

Short. Full detail lives in METHODS.md.

## Results

The numbers, with denominators and uncertainty. Every figure here must be reproducible
by running the scripts below.

## Limitations

What this does not show. Write this section honestly, it is the section that gets read
in an interview.

## Reproduce

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python 01_load.py
python 02_clean.py
python 03_analyze.py
```

## Stack
