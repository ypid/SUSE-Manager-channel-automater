#!/usr/bin/python3

# SPDX-FileCopyrightText: 2021 Robin Schneider <robin.schneider@geberit.com>
#
# SPDX-License-Identifier: AGPL-3.0-only

# -*- coding: utf-8 -*-
# NOQA

import unittest
import unittest.mock

from nose.tools import assert_equal, assert_not_equal, assert_raises_regexp  # NOQA

from suma_automater import SuMaAutomater


class Test(unittest.TestCase):

    def setUp(self):
        self.a = SuMaAutomater(
            dry_run=True,
            config={},
        )
        self.a._xml_rpc = unittest.mock.Mock()
        self.a._xml_rpc_key = 'secret'
        self.a._xml_rpc.channel = unittest.mock.Mock()
        self.a._xml_rpc.channel.software = unittest.mock.Mock()

    def test_get_matching_third_party_channels(self):
        my_channels = [
            {'id': 12131, 'label': 'third_party-custom_repo', 'name': 'Third party - custom_repo - SLES', 'arch_name': 'x86_64', 'arch_label': 'channel-x86_64', 'summary': '^sles', 'description': '', 'checksum_label': 'sha256', 'last_modified': '*left_out*', 'maintainer_name': '', 'maintainer_email': '', 'maintainer_phone': '', 'support_policy': '', 'gpg_key_url': '', 'gpg_key_id': '', 'gpg_key_fp': '', 'gpg_check': False, 'yumrepo_last_sync': '*left_out*', 'contentSources': [{'id': 650, 'label': 'custom-sle15', 'sourceUrl': 'https://suse-manager.example.net/pub/repositories/custom/sle/15/', 'type': 'yum', 'hasSignedMetadata': False, 'sslContentSources': []}], 'end_of_life': '', 'parent_channel_label': 'third_party-regex_match-x86_64', 'clone_original': ''}
        ]
        self.a._xml_rpc.channel.software.getDetails = unittest.mock.MagicMock(return_value=my_channels[0])

        assert_equal(
            len(self.a._get_matching_third_party_channels([{'label': my_channels[0]['label']}], {'label': 'sles-something'})),
            1,
        )

    #  def test_delete_unknown_child_channels(self):

    #      self.a._ensure_channel_is_deleted = unittest.mock.MagicMock()

    #      self.a._delete_unknown_child_channels()

    #      assert_equal(
    #          self.a._ensure_channel_is_deleted.call_count,
    #          1,
    #      )


if __name__ == '__main__':
    unittest.main()
