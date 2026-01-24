# x2q.net

A minimal single-page personal site built with Hugo.

## Structure

```
.
├── config.toml          # Site configuration
├── content/             # Content (empty for single-page)
├── layouts/
│   ├── _default/
│   │   └── baseof.html  # Base template
│   ├── partials/
│   │   ├── head.html    # HTML head
│   │   ├── header.html  # Site header
│   │   └── footer.html  # Site footer
│   └── index.html       # Homepage
└── static/
    ├── CNAME            # GitHub Pages domain
    ├── favicon.svg      # Site favicon
    └── robots.txt       # Robots file
```

## Development

```bash
hugo server
```

## Build

```bash
hugo --minify
```

## Deploy

Push to `main` branch. GitHub Pages will build and deploy automatically.

## License

MIT
