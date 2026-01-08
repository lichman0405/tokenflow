# Installation

Choose your preferred language and follow the installation instructions below.

## Go

### Prerequisites

- Go 1.21 or higher

### Install

```bash
go get github.com/lichman0405/tokenflow/go
```

### Verify Installation

```bash
cd go
go build ./...
```

## Python

### Prerequisites

- Python 3.8 or higher
- pip

### Install from Source

```bash
cd python
pip install -e .
```

### Install from PyPI (when published)

```bash
pip install tokenflow
```

### Verify Installation

```bash
python -c "from oauth import copilot; print('TokenFlow installed successfully!')"
```

## TypeScript

### Prerequisites

- Node.js 16.0 or higher
- npm or yarn

### Install

```bash
cd ts
npm install
npm run build
```

### Install as Package (when published)

```bash
npm install tokenflow
```

### Verify Installation

```bash
npm run build
# Should compile without errors
```

## Next Steps

Once installed, proceed to the [Quick Start Guide](quickstart.md) to begin using TokenFlow.
