# Copyright 2012 Red Hat, Inc.
# Copyright 2013 IBM Corp.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""Translation function factory
"""

import gettext
import os

import six

from oslo.i18n import _contextualmessage
from oslo.i18n import _lazy
from oslo.i18n import _locale
from oslo.i18n import _message
from oslo.i18n import _pluralmessage


__all__ = [
    'TranslatorFactory',
]

# magic gettext number to separate context from message
CONTEXT_SEPARATOR = "\x04"


class TranslatorFactory(object):
    "Create translator functions"

    def __init__(self, domain, localedir=None):
        """Establish a set of translation functions for the domain.

        :param domain: Name of translation domain,
                       specifying a message catalog.
        :type domain: str
        :param localedir: Directory with translation catalogs.
        :type localedir: str
        """
        self.domain = domain
        if localedir is None:
            variable_name = _locale.get_locale_dir_variable_name(domain)
            localedir = os.environ.get(variable_name)
        self.localedir = localedir

    def _make_translation_func(self, domain=None):
        """Return a translation function ready for use with messages.

        The returned function takes a single value, the unicode string
        to be translated.  The return type varies depending on whether
        lazy translation is being done. When lazy translation is
        enabled, :class:`Message` objects are returned instead of
        regular :class:`unicode` strings.

        The domain argument can be specified to override the default
        from the factory, but the localedir from the factory is always
        used because we assume the log-level translation catalogs are
        installed in the same directory as the main application
        catalog.

        """
        if domain is None:
            domain = self.domain
        t = gettext.translation(domain,
                                localedir=self.localedir,
                                fallback=True)
        # Use the appropriate method of the translation object based
        # on the python version.
        m = t.gettext if six.PY3 else t.ugettext

        def f(msg):
            """oslo.i18n.gettextutils translation function."""
            if _lazy.USE_LAZY:
                return _message.Message(msg, domain=domain)
            return m(msg)
        return f

    def _make_contextual_translation_func(self, domain=None):
        "Return a translation function ready for use with context messages."
        if domain is None:
            domain = self.domain
        t = gettext.translation(domain,
                                localedir=self.localedir,
                                fallback=True)
        # Use the appropriate method of the translation object based
        # on the python version.
        m = t.gettext if six.PY3 else t.ugettext

        def f(ctx, msg):
            """oslo.i18n.gettextutils translation with context function."""
            if _lazy.USE_LAZY:
                return _contextualmessage.ContextualMessage(
                    ctx, msg, domain=domain)

            msgctx = "%s%s%s" % (ctx, CONTEXT_SEPARATOR, msg)
            s = m(msgctx)
            if CONTEXT_SEPARATOR in s:
                # Translation not found
                return msg
            return s
        return f

    def _make_plural_translation_func(self, domain=None):
        "Return a plural translation function ready for use with messages"
        if domain is None:
            domain = self.domain
        t = gettext.translation(domain,
                                localedir=self.localedir,
                                fallback=True)
        # Use the appropriate method of the translation object based
        # on the python version.
        m = t.ngettext if six.PY3 else t.ungettext

        def f(msgsingle, msgplural, msgcount):
            """oslo.i18n.gettextutils plural translation function."""
            if _lazy.USE_LAZY:
                return _pluralmessage.PluralMessage(
                    msgsingle, msgplural, msgcount, domain=domain)
            return m(msgsingle, msgplural, msgcount)
        return f

    @property
    def primary(self):
        "The default translation function."
        return self._make_translation_func()

    @property
    def contextual_form(self):
        "The contextual translation function."
        return self._make_contextual_translation_func()

    @property
    def plural_form(self):
        "The plural translation function."
        return self._make_plural_translation_func()

    def _make_log_translation_func(self, level):
        return self._make_translation_func(self.domain + '-log-' + level)

    @property
    def log_info(self):
        "Translate info-level log messages."
        return self._make_log_translation_func('info')

    @property
    def log_warning(self):
        "Translate warning-level log messages."
        return self._make_log_translation_func('warning')

    @property
    def log_error(self):
        "Translate error-level log messages."
        return self._make_log_translation_func('error')

    @property
    def log_critical(self):
        "Translate critical-level log messages."
        return self._make_log_translation_func('critical')
