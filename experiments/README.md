# Adding your own experiments and proofs of concept

Experiments are added to the server by adding HTML and JSON files to the `experiments` folder.
The file structure is as follows:

```
experiments
|-- pages
|   |-- [project 1]
|   |   |-- [experiment 1]
|   |   |-- [experiment 2]
|   |   |-- ...
|   |   |-- [experiment N]
|   |-- [ project 2]
|   |-- ...
|   |-- [project N]
|-- resources
```

Experiments are grouped within projects.
These projects can be used to represent sets of related experiments.

Each experiment defines at least one domain, and each domain in turn defines at least one webpage.


## Experiments

The file structure within an experiment folder is as follows:

```
...
[experiment 1]
|-- [domain 1]
    |-- [page 1]
        |-- headers.json
        |-- index.html
    |-- [page 2]
        |-- headers.json
        |-- index.js
|-- [domain 2]
|-- url_queue.txt
...
```

### Domains

> :warning: Each experiment defines one or more domains.

Domain names supported by the framework are:
- `leak.test`
- `a.test`
- `sub.a.test`
- `sub.sub.a.test`
- `b.test`
- `adition.com` (tracking domain)

If you would like to have other domain names supported, feel free to open a GitHub issue.

#### Webpages

> :warning: Each domain defines one or more webpages.

A webpage is defined by an index file, i.e. the resource that is loaded when the page's URL is visited.

The following file extensions are supported:
- `index.html`
- `index.js`

The endpoint at which a resource is hosted is constructed as follows:
```
https://[domain]/[project]/[experiment]/[page]
```

> Example: the example file at `experiments/pages/templates/example/a.test/main/index.html` is accessible through the URL `https://a.test/templates/example/main`.

Each webpage can be supplied with response headers.
This is done by creating a file `headers.json` in the following format:

```json
[
    {
        "key": "Header name",
        "value": "Header value"
    }
]
```

> :warning: `headers.json` files cannot be empty.


### URL queue

> :warning: Each experiment defines exactly one URL queue, unless it is trivial which URLs should be visited.

### Example


## Resources

Other functional requirements require modifications to the source code.
Feel free to make suggestions using GitHub Issues.
