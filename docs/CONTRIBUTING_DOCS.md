# Contributing to Documentation

This guide explains how to work with the documentation for `colombian-grid`.

## Documentation Structure

The documentation is built using [MkDocs](https://www.mkdocs.org/) with the [Material theme](https://squidfunk.github.io/mkdocs-material/).

```
colombian-grid/
├── mkdocs.yml          # MkDocs configuration
├── docs/               # Documentation source files
│   ├── index.md        # Home page
│   ├── guia.md         # Quick Start Guide
│   ├── api-reference.md # API Reference (auto-generated)
│   ├── ejemplos.md     # Usage Examples
│   └── assets/         # Images and other assets
└── site/               # Generated documentation (not committed)
```

## Building Documentation Locally

### Prerequisites

Install documentation dependencies using `uv`:

```bash
uv sync --group docs
```

### Build the Documentation

To build the documentation once:

```bash
uv run mkdocs build
```

This generates the static site in the `site/` directory.

### Serve the Documentation Locally

To serve the documentation with live reloading:

```bash
uv run mkdocs serve
```

Then open your browser to [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Strict Mode

To build with warnings treated as errors (recommended before committing):

```bash
uv run mkdocs build --strict
```

## Documentation Guidelines

### Writing Guidelines

1. **Language**: Write documentation in Spanish as the primary audience is Colombian energy market participants.
2. **Code Examples**: Always include working code examples that can be copy-pasted.
3. **Type Hints**: Ensure all public API methods have proper return type annotations for auto-generated documentation.
4. **Docstrings**: Use Google-style docstrings for all public classes and methods.

### API Reference

The API reference is automatically generated from docstrings using `mkdocstrings`. To add a new class to the API reference:

1. Add proper docstrings to your class/methods
2. Update `docs/api-reference.md` with the mkdocstrings directive:

```markdown
::: colombian_grid.module.ClassName
    handler: python
    options:
      members:
        - method1
        - method2
```

### Adding New Pages

1. Create a new `.md` file in the `docs/` directory
2. Add it to the navigation in `mkdocs.yml`:

```yaml
nav:
  - Inicio: index.md
  - Your New Page: your-page.md
```

## Continuous Integration

Documentation is automatically built and deployed via GitHub Actions:

### On Pull Requests

- Documentation is built in strict mode to catch errors
- Build artifacts are uploaded for review
- Any warnings will cause the build to fail

### On Push to Main

- Documentation is built and deployed to GitHub Pages
- Available at: https://jccamargo94.github.io/colombian-grid/

## Troubleshooting

### Warning: No type or annotation for returned value

This warning occurs when a method doesn't have a return type annotation. Fix by adding type hints:

```python
# Before
async def get_data(self):
    return await self.fetcher.get()

# After
async def get_data(self) -> list:
    return await self.fetcher.get()
```

### Documentation not updating

1. Clear the site directory: `rm -rf site/`
2. Rebuild: `uv run mkdocs build`

### Missing dependencies

Ensure all documentation dependencies are installed:

```bash
uv sync --group docs
```

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [mkdocstrings](https://mkdocstrings.github.io/)
