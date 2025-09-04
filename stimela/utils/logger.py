import sys
import logging

class MultiplexingHandler(logging.Handler):
    """handler to send INFO and below to stdout, everything above to stderr"""
    def __init__(self, info_stream=sys.stdout, err_stream=sys.stderr):
        super(MultiplexingHandler, self).__init__()
        self.info_handler = logging.StreamHandler(info_stream)
        self.err_handler = logging.StreamHandler(err_stream)
        self.multiplex = True

    def emit(self, record):
        handler = self.err_handler if record.levelno > logging.INFO and self.multiplex else self.info_handler
        handler.emit(record)
        # ignore broken pipes, this often happens when cleaning up and exiting
        try:
            handler.flush()
        except BrokenPipeError:
            pass

    def flush(self):
        try:
            self.err_handler.flush()
            self.info_handler.flush()
        except BrokenPipeError:
            pass

    def close(self):
        self.err_handler.close()
        self.info_handler.close()

    def setFormatter(self, fmt):
        self.err_handler.setFormatter(fmt)
        self.info_handler.setFormatter(fmt)

class ConsoleColors():
    WARNING = '\033[93m' if sys.stdin.isatty() else ''
    ERROR   = '\033[91m' if sys.stdin.isatty() else ''
    BOLD    = '\033[1m'  if sys.stdin.isatty() else ''
    DIM     = '\033[2m'  if sys.stdin.isatty() else ''
    GREEN   = '\033[92m' if sys.stdin.isatty() else ''
    ENDC    = '\033[0m'  if sys.stdin.isatty() else ''

    BEGIN = "<COLORIZE>"
    END   = "</COLORIZE>"

    @staticmethod
    def colorize(msg, *styles):
        style = "".join(styles)
        return msg.replace(ConsoleColors.BEGIN, style).replace(ConsoleColors.END, ConsoleColors.ENDC if style else "")

class ColorizingFormatter(logging.Formatter):
    """This Formatter inserts color codes into the string according to severity"""
    def __init__(self, fmt=None, datefmt=None, style="%", default_color=None):
        super(ColorizingFormatter, self).__init__(fmt, datefmt, style)
        self._default_color = default_color or ""

    def format(self, record):
        style = ConsoleColors.BOLD if hasattr(record, 'boldface') else ""
        if hasattr(record, 'color'):
            style += getattr(ConsoleColors, record.color or "None", "")
        elif record.levelno >= logging.ERROR:
            style += ConsoleColors.ERROR
        elif record.levelno >= logging.WARNING:
            style += ConsoleColors.WARNING
        return ConsoleColors.colorize(super(ColorizingFormatter, self).format(record), style or self._default_color)


class SelectiveFormatter(logging.Formatter):
    """Selective formatter. if condition(record) is True, invokes other formatter"""
    def __init__(self, default_formatter, dispatch_list):
        self._dispatch_list = dispatch_list
        self._default_formatter = default_formatter

    def format(self, record):
        for condition, formatter in self._dispatch_list:
            if condition(record):
                return formatter.format(record)
        else:
            return self._default_formatter.format(record)


