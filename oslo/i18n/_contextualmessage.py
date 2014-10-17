# Copyright 2014 Red Hat, Inc.
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
"""Private Contextual Message class for lazy translation support.
"""

import gettext
import locale
import os

import six

from oslo.i18n import _locale
from oslo.i18n import _message
from oslo.i18n import _translate

# magic gettext number to separate context from message
CONTEXT_SEPARATOR = "\x04"


class ContextualMessage(_message.Message):
    def __new__(cls, msgctx, msgid, msgtext=None, params=None,
                domain='oslo', *args):
        if not msgtext:
            msgtext = ContextualMessage._translate_msgid_ctx(
                msgctx, msgid, domain)
        msg = super(ContextualMessage, cls).__new__(cls, msgtext)
        msg.msgctx = msgctx
        msg.msgid = msgid
        msg.domain = domain
        msg.params = params
        return msg

    def translate(self, desired_locale=None):
        "Translate this message to the desired locale."

        translated_message = ContextualMessage._translate_msgid_ctx(
            self.msgctx, self.msgid, self.domain, desired_locale)
        if self.params is None:
            # No need for more translation
            return translated_message

        # This Message object may have been formatted with one or more
        # Message objects as substitution arguments, given either as a single
        # argument, part of a tuple, or as one or more values in a dictionary.
        # When translating this Message we need to translate those Messages too
        translated_params = _translate.translate_args(self.params,
                                                      desired_locale)

        translated_message = translated_message % translated_params

        return translated_message

    @staticmethod
    def _translate_msgid_ctx(msgctx, msgid, domain, desired_locale=None):
        if not desired_locale:
            system_locale = locale.getdefaultlocale()
            # If the system locale is not available to the runtime use English
            desired_locale = system_locale[0] or 'en_US'

        locale_dir = os.environ.get(
            _locale.get_locale_dir_variable_name(domain)
        )
        lang = gettext.translation(domain,
                                   localedir=locale_dir,
                                   languages=[desired_locale],
                                   fallback=True)
        translator = lang.gettext if six.PY3 else lang.ugettext

        msg_with_ctx = "%s%s%s" % (msgctx, CONTEXT_SEPARATOR, msgid)
        translated_message = translator(msg_with_ctx)

        if CONTEXT_SEPARATOR in translated_message:
            # Translation not found
            translated_message = msgid

        return translated_message
