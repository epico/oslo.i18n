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
"""Private Plural Message class for lazy translation support.
"""


import gettext
import locale
import os

import six

from oslo.i18n import _locale
from oslo.i18n import _message
from oslo.i18n import _translate


class PluralMessage(_message.Message):
    def __new__(cls, msgsingle, msgplural, msgcount,
                msgtext=None, params=None,
                domain='oslo', *args):
        if not msgtext:
            msgtext = PluralMessage._translate_msgid_plural(
                msgsingle, msgplural, msgcount, domain)
        msg = super(PluralMessage, cls).__new__(cls, msgtext)
        msg.msgsingle = msgsingle
        msg.msgplural = msgplural
        msg.msgcount = msgcount
        msg.domain = domain
        msg.params = params
        return msg

    def translate(self, desired_locale=None):
        "Translate this message to the desired locale."

        translated_message = PluralMessage._translate_msgid_plural(
            self.msgsingle, self.msgplural, self.msgcount,
            self.domain, desired_locale)
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
    def _translate_msgid_plural(msgsingle, msgplural, msgcount,
                                domain, desired_locale=None):
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
        translator = lang.ngettext if six.PY3 else lang.ungettext

        translated_message = translator(msgsingle, msgplural, msgcount)
        return translated_message
