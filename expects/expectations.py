# -*- coding: utf-8 -*


class Expectation(object):
    def __init__(self, parent):
        self._parent = parent

        self.init()

    def init(self):
        pass

    @property
    def actual(self):
        return self._parent.actual

    @property
    def negative(self):
        return self._parent.negative

    def _assert(self, result, error_message):
        assert not result if self.negative else result, error_message


class Equal(Expectation):
    def __call__(self, expected):
        self._assert(self.actual == expected, self.error_message(repr(expected)))

    def error_message(self, tail):
        return self._parent.error_message('equal {}'.format(tail))


class Be(Expectation):
    def init(self):
        self.equal = Equal(self)

    def __call__(self, expected):
        self._assert(self.actual is expected, self.error_message(repr(expected)))

    def a(self, expected):
        self.__instance_of(expected, 'a')

    def an(self, expected):
        self.__instance_of(expected, 'an')

    def __instance_of(self, expected, article):
        self._assert(isinstance(self.actual, expected), self.error_message(
            '{} {} instance'.format(article, expected.__name__)))

    @property
    def true(self):
        self(True)

    @property
    def false(self):
        self(False)

    @property
    def none(self):
        self(None)

    def error_message(self, tail):
        return self._parent.error_message('be {}'.format(tail))


class Have(Expectation):
    def property(self, *args):
        def error_message(tail):
            return self.error_message('property {}'.format(tail))

        name = args[0]

        try:
            expected = args[1]
        except IndexError:
            pass
        else:
            try:
                value = getattr(self.actual, name)
            except AttributeError:
                pass
            else:
                self._assert(value == expected, error_message('{} with value {} but was {}'.format(
                    repr(name), repr(expected), repr(value))))

                return

        self._assert(hasattr(self.actual, name), error_message(repr(name)))

    def properties(self, *args, **kwargs):
        try:
            kwargs = dict(*args, **kwargs)
        except (TypeError, ValueError):
            for name in args:
                self.property(name)
        finally:
            for name, value in kwargs.items():
                self.property(name, value)

    def error_message(self, tail):
        return self._parent.error_message('have {}'.format(tail))


class RaiseError(Expectation):
    def __call__(self, expected, message=None):
        assertion = self._build_assertion(expected, message)

        if assertion is not None:
            self._assert(*assertion)

    def _build_assertion(self, expected, message):
        def error_message(tail):
            return self.error_message('{} {}'.format(
                expected.__name__, tail))

        try:
            self.actual()
        except expected as exc:
            exc_message = str(exc)

            if message is not None:
                return message == exc_message, error_message(
                    'with message {} but message was {}'.format(repr(message), repr(exc_message)))
            else:
                return True, error_message('but {} raised'.format(type(exc).__name__))
        except Exception as err:
            return False, error_message('but {} raised'.format(type(err).__name__))
        else:
            return False, error_message('but {} raised'.format(None))

    def error_message(self, tail):
        return self._parent.error_message('raise {}'.format(tail))


class To(Expectation):
    def init(self):
        self.be = Be(self)
        self.have = Have(self)
        self.equal = Equal(self)
        self.raise_error = RaiseError(self)

    def error_message(self, tail):
        message = 'not to' if self.negative else 'to'

        return self._parent.error_message('{} {}'.format(message, tail))