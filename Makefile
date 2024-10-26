# SPDX-FileCopyrightText: 2021 Robin Schneider <robin.schneider@geberit.com>
#
# SPDX-License-Identifier: AGPL-3.0-only

SHELL ?= /bin/bash -o nounset -o pipefail -o errexit
MAKEFLAGS += --no-builtin-rules
.SUFFIXES:

PREFIX ?= /usr/local

.PHONY: test
test: test-reuse-spec
	nosetests
	command -v find_geberit_internal_strings >/dev/null 2>&1 && find_geberit_internal_strings

.PHONY: test-reuse-spec
test-reuse-spec:
	@reuse lint

.PHONY: install
install:
	install -d $(DESTDIR)$(PREFIX)/bin/
	install -m 0755 suma_automater $(DESTDIR)$(PREFIX)/bin/
	install -d $(DESTDIR)/etc/suma_automater
	rsync --ignore-existing example_config.yaml $(DESTDIR)/etc/suma_automater/config.yaml

.PHONY: install-systemd
install-systemd:
	install -d $(DESTDIR)/etc/systemd/system/
	install -m 0644 systemd/* $(DESTDIR)/etc/systemd/system/
	systemctl daemon-reload
