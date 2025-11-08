# A* web crawler and map-colouring CSP solver

Two small assignments for the NI-UMI course (Artificial Intelligence) at FIT CTU, winter semester 2022/23. The tasks were set by the course. Each one is a single Python script in its own folder:

- `scraper/`: a web crawler that looks for a chain of links from one website to another with a modified A* search
- `csp/`: a constraint satisfaction solver for colouring the map of Australia, with three variants of backtracking search

Both need Python 3.10 or newer.

## Web crawler (`scraper/`)

Given a start URL and a target URL, the crawler looks for a chain of hyperlinks that leads from the start page to the target's website.

### Approach

- **Search:** pages are nodes and links are edges. The crawler keeps an open set of discovered pages and a closed set of visited ones. At each step it downloads the open page with the lowest g + h, parses it with Beautiful Soup and adds every `<a href>` link it hasn't seen yet to the open set.
- **Cost (g):** the number of links followed from the start page.
- **Heuristic (h):** a penalty for each link:
  - +10 if its host isn't in the `.edu` domain
  - +2 if it's on the same host as the page it was found on
  - +2 if it uses plain `http` instead of `https`

  This pushes the search towards `.edu` sites (the default target is MIT's) and away from staying on one site.
- **Filtering:** links that aren't valid URLs, or that end in a file extension such as `.pdf`, `.docx`, `.zip` or `.jpg`, are skipped.
- **Goal:** the search stops as soon as it finds a link whose URL contains the target's domain, taken as the last two parts of its host name (for example `mit.edu`). It then prints the path.

One run recorded in December 2022 went from `https://fit.cvut.cz/` to `http://web.mit.edu/` in about a minute and a half. On the way it passed through a FIT news article, a page on eurotech-universities.eu and two pages on polytechnique.edu.

### Running

```bash
cd scraper
python3 -m venv .venv
source .venv/bin/activate
pip install requests beautifulsoup4 validators
python main.py --start https://fit.cvut.cz/ --end https://www.mit.edu/
```

These two URLs are also the defaults. Include the `https://` or `http://` prefix. `requirements.txt` lists the same packages plus JupyterLab, left over from an experimental notebook that was later removed. The script logs every page it visits, with its score and the sizes of the open and closed sets, and finally prints the path and the time taken.

### Limitations

- **It is only loosely A\*.** The heuristic's penalties are much larger than the cost of a step, so the search acts mostly like greedy best-first search towards `.edu` sites. It also stops when the target is first discovered rather than when it's expanded, so the path isn't necessarily the shortest.
- **The goal check is loose.** Any URL that contains the last two parts of the target's host name counts. So `web.mit.edu` counts as reaching `www.mit.edu`, but for `www.bbc.co.uk` any `co.uk` link would count.
- **It isn't a polite crawler.** Requests have no timeout, there is no rate limiting and `robots.txt` is ignored. If no path is found, printing it fails with an `AttributeError`.

## CSP solver (`csp/`)

The problem is the map-colouring example from Russell and Norvig's *Artificial Intelligence: A Modern Approach*: colour the seven states and territories of Australia with three colours so that no two neighbours have the same colour.

- **Variables:** the regions WA, NT, SA, Q, NSW, V and T, stored as nodes of a graph
- **Domains:** red, green and blue
- **Constraints:** neighbouring regions must have different colours. Tasmania (T) has no neighbours.

All three solvers take the variables in a fixed order (the order of the map definition) and check every constraint after each assignment.

| Solver | Approach |
|---|---|
| `backtrack` (default) | Chronological backtracking. Tries red, green and blue in turn and backs up one level when none fits. |
| `backjump` | Backjumping. When a colour clashes, the variables involved in the clash form a conflict set, which is passed back up when a branch fails. If the current variable isn't in that set, changing its colour can't help, so the search returns straight away instead of trying its other colours. |
| `mac_backtrack` | Backtracking that maintains arc consistency. After each assignment, AC-3 runs over every arc of the graph and removes colours that the neighbouring domain can't support. A branch fails when a domain becomes empty. |

### Running

```bash
python3 csp/main.py --solver backjump    # backtrack, backjump or mac_backtrack
```

Only the standard library is needed. The script prints a detailed trace and ends with the colouring. `backtrack` and `backjump` both find WA red, NT green, SA blue, Q red, NSW green, V red and T red.

### Limitations

- **`mac_backtrack` never finishes.** In `revise`, `revised = True` sits outside the `if` that removes a colour, so AC-3's queue never empties. With that line moved inside the `if`, it finds the same colouring, but colours pruned by AC-3 still aren't restored when the search backtracks.
- **`backjump` doesn't clear a variable's colour after a failure,** so on harder graphs it can finish without a valid colouring.
- **The map is hard-coded.** On the Australia map, neither `backtrack` nor `backjump` ever hits a dead end, so their backtracking code is never exercised.

## Repository layout

| Path | Contents |
|---|---|
| `scraper/main.py` | The web crawler |
| `scraper/README.MD` | The original notes, with the full path from the example run |
| `scraper/requirements.txt` | Its Python dependencies |
| `csp/main.py` | The Australia map, the graph classes and the three solvers |
