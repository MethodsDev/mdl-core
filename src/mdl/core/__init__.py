__version__ = "0.0.1"

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
        'error': dict(fg='red'),
        'exception': dict(fg='red'),
        'critical': dict(fg='red'),
        'debug': dict(fg='blue'),
        'warning': dict(fg='yellow'),
        'info': dict(fg='cyan'),
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


def config_logger(path, name):
    with importlib.resources.path(path, name) as log_config:
        with log_config.open() as fh:
            logging.config.dictConfig(tomllib.load(fh))
        log.debug(f"Loaded logging configuration from {log_config.absolute()}")
