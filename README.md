# BugHog web experiment server

This standalone experiment server is intended to be used in conjunction with [BugHog](https://github.com/DistriNet/BugHog).
Nevertheless, should you discover other fitting purposes, you are free to use it for those as well.

If you intend to use this as part of the [BugHog](https://github.com/DistriNet/BugHog) framework, follow the instructions from there.

To add your own custom experiments to the server, follow these instructions.


## Usage

### Prerequisites

- Docker (tested with version 24.0.1)


### Installing

1. Clone this repository:

```bash
git clone https://github.com/DistriNet/BugHog-web.git
cd BugHog-web
```

2. Build image:

```bash
docker-compose build
```


### Starting

The experiment server is started with:

```bash
docker-compose up
```

To stop the server, execute the following:

```bash
docker-compose down
```


## Adding custom experiments


