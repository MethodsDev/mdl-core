import importlib.resources
import logging
import logging.config

import click

try:
    import tomllib
except ImportError:
    import tomli as tomllib


log = logging.getLogger(__package__)


# custom version of click_log.ColorFormatter that supports formatting
class ColorFormatter(logging.Formatter):
    colors = {
        "error": dict(fg="red"),
        "exception": dict(fg="red"),
        "critical": dict(fg="red"),
        "debug": dict(fg="blue"),
        "warning": dict(fg="yellow"),
        "info": dict(fg="cyan"),
    }

    def format(self, record):  # noqa: A003
        formatted_msg = super().format(record)

        if self._fmt.find("levelname") > -1:
            level = record.levelname.lower()
            formatted_msg = formatted_msg.replace(
                record.levelname,
                click.style(level, **self.colors[level]),
                1,
            )

        return formatted_msg


# vendored copy of click_log.ClickHandler
class ClickHandler(logging.Handler):
    _use_stderr = True

    def emit(self, record):
        try:
            msg = self.format(record)
            click.echo(msg, err=self._use_stderr)
        except Exception:
            self.handleError(record)


def config_logger(package, name="logger.toml"):
    with importlib.resources.path(package, name) as log_config:
        with log_config.open("rb") as fh:
            logging.config.dictConfig(tomllib.load(fh))
        log.debug(f"Loaded logging configuration from {log_config.absolute()}")


# version of click_log.simple_verbosity_option that loads a config first
def verbosity_config_option(logger, pkg, *names, name="logger.toml", **kwargs):
    """A decorator that adds a `--verbose, -v` option to the decorated
    command.

    Name can be configured through ``*names``. Keyword arguments are passed to
    the underlying ``click.option`` decorator.
    """

    if not names:
        names = ["--verbose", "-v"]

    kwargs.setdefault("default", "INFO")
    kwargs.setdefault("metavar", "LVL")
    kwargs.setdefault("expose_value", False)
    kwargs.setdefault("help", "Either CRITICAL, ERROR, WARNING, INFO or DEBUG")
    kwargs.setdefault("is_eager", True)

    def decorator(f):
        def _set_level(ctx, param, value):
            x = getattr(logging, value.upper(), None)
            if x is None:
                raise click.BadParameter(
                    f"Must be CRITICAL, ERROR, WARNING, INFO or DEBUG, not {value}"
                )
            config_logger(pkg, name)
            logger.setLevel(x)

        return click.option(*names, callback=_set_level, **kwargs)(f)

    return decorator
