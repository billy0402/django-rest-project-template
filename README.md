# django-rest-project-template

My Django REST project template.

## Development environment

-   [macOS 12.7.2](https://www.apple.com/tw/macos/monterey/)
-   [Visual Studio Code 1.85.1](https://code.visualstudio.com/)
-   [Python 3.11.7](https://www.python.org/)
-   [Django 5.0.6](https://www.djangoproject.com/)
-   [Django REST framework 3.15.1](https://www.django-rest-framework.org/)

## Installation

```shell
$ make install
```

## Getting Started

```shell
$ cp .devcontainer/.env.example .devcontainer/.env

$ make dev-services-up

$ cp server/settings/.env.example server/settings/.env

$ make dev-server
```

## Lint

```shell
# style checking
$ make lint

# type checking
$ make typecheck
```

## Testing

```shell
$ make test
```

## Build

```shell
$ make build
```

## Bugs and suggestions

If you have found a bug or have a request for additional functionality, please use the issue tracker on GitHub.

https://github.com/billy0402/django-rest-project-template/issues

## License

Released under [MIT](/LICENSE) by [@billy0402](https://github.com/billy0402).
