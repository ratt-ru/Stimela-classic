# -*- coding: future_fstrings -*-
class StimelaCabParameterError(Exception):
    pass

class StimelaRecipeExecutionError(Exception):
    pass

class StimelaBaseImageError(Exception):
    pass


class PipelineException(Exception):
    """ 
    Encapsulates information about state of pipeline when an
    exception occurs
    """

    def __init__(self, exception, completed, failed, remaining):
        message = ("Job '%s' failed: %s" % (failed.label, str(exception)))

        super(PipelineException, self).__init__(message)

        self._completed = completed
        self._failed = failed
        self._remaining = remaining

    @property
    def completed(self):
        return self._completed

    @property
    def failed(self):
        return self._failed

    @property
    def remaining(self):
        return self._remaining

