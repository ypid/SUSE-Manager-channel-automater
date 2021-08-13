<!--
SPDX-FileCopyrightText: 2019-2021 Robin Schneider <robin.schneider@geberit.com>

SPDX-License-Identifier: CC-BY-SA-4.0
-->

# SUSE Manager channel automater

Patch managmenet in different phases. New package versions get merged from one
phase to the next to allow to test patches before they hit production servers.

The script implements [Advanced Patch Lifecycle Management with SUSE Manager](https://web.archive.org/web/20190501035733/https://www.suse.com/documentation/suse-best-practices/susemanager/data/susemanager.html) from 2019.

Hint: This script was written in early 2019. If you start out fresh consider
using Content Lifecycle from SUSE Manager 4.0. Still, this script has more
features than Content Lifecycle. It could be interesting to change the script
to work ontop of Content Lifecycle to get the best of both works.
The script basically implements Content Lifecycle itself for now.

## Configuration

The patch phases that should be created and managed need to be listed in the
configuration file `/etc/suma_automater/config.yaml`. This file also gives a
few more configuration options are features.

A commented example configuration will be installed when you run `make
install`.

## Naming conventions

The following naming convention is very important for `suma_automater` because
it bases all it’s logic on it. Examples: What is an archive channel? What to
merge into current update channels?

This makes the software channel and patch management very flexible but the
naming convention needs to be followed for it to work.

The channel label syntax is defined using ABNF. Refer to
https://tools.ietf.org/html/rfc5234 for details.

```ABNF
distribution-short-name = 1*(ALPHA / DIGIT)
release-version-number = 1*DIGIT
service-pack = "SP" 1*DIGIT
architecture = 1*(ALPHA / DIGIT / "_")
freeze-timestamp = date-time ; RFC 3339 and https://tools.ietf.org/html/rfc5424#section-6.2.3 compliend with the exception only a "persison" of day of month (%Y-%m-%d) is suggested.
vendor-immutable-word = "pool"  ; The vendor does not change the channel once it has been released.
vendor-mutable-word = "updates" ; Channel used to ship updates. Often based on immutable channel and thus update channel is to begin empty.
vendor-immutable-or-mutable-word = vendor-immutable-word / vendor-mutable-word

vendor-software-channel = distribution-short-name "-" release-version-number ["-" service-pack] "-" architecture
archive-software-channel =  ("archive") "-" vendor-software-channel "-" freeze-timestamp
third-party-software-parent-channel = "third_party-" (vendor-software-channel / "regex_match-" architecture)
third-party-label = 1*(ALPHA / DIGIT / "-") ; e.g. elastic-7.x
third-party-software-channel-short = "third_party-" third-party-label "-" vendor-immutable-or-mutable-word "-" architecture
third-party-software-channel = third-party-software-channel-short "-" vendor-software-channel

;; Not used anymore: Replaced by "current_update".
; org-name = 1*(ALPHA / DIGIT / "_")
; org-custom-software-channel = org-name "-" vendor-software-channel

current-update-software-channel = "current_update-" vendor-software-channel
; Ref: https://www.suse.com/documentation/suse-best-practices/susemanager/data/susemanager.html#sec_exception "cloned base channel for the version of SUSE Linux Enterprise Server"

current-update-patch-asap-channel = "current_update-patch_asap-" vendor-software-channel
current-update-patch-exceptions-channel = "current_update-patch_exceptions-" vendor-software-channel

current-update-third-party-channel = "current_update-third_party-" vendor-software-channel "-" third-party-label

landscape-name = 1*ALPHA
patch-phase = 1*ALPHA
current-updates-channel = current-update-software-channel "-" patch-phase

activation-key-description = 1*ALPHA ; based on current-updates-channel
vendor-manager-organization-id = 1*DIGIT
activation-key = vendor-manager-organization-id "-" activation-key-description
bootstrap-filename = "bootstrap-" activation-key ".sh"
```

### Examples

### Software channel labels

* `sles12-sp4-pool-x86_64`
* `sle-product-sles15-pool-x86_64`
* `sle12-sp4-sap-pool-x86_64`
* `current_updates-sles12-sp4-pool-x86_64`
* `current_updates-sle-ha12-sp4-pool-x86_64`
* `current_updates-sle-ha12-sp4-updates-x86_64-phase-3`
* `current_updates-patch_asap-sles12-sp4-pool-x86_64`
* `current_updates-patch_exceptions-sles12-sp4-pool-x86_64`
* `archive-sles12-sp4-pool-x86_64`
* `archive-2019-04-16-sle-ha12-sp4-updates-x86_64`

### Bootstrap script

* `bootstrap-1-sles12-sp4-x86_64-phase-3.sh`

### Third party repos

Third party repos can be setup and will be included into the patch phases the
same way as vendor channels. There are two options to include third party
channels.

#### Third party channel per product

You can define one third party channel for each product (for example
SLES12-SP4). You should choose this option when the third party repo is
different for every product.

Create a parent channel with channel label "third_party-sles12-sp4-pool-x86_64"
and channel name "Third Party - SLE12-SP4-SAP-Pool for x86_64". In that parent
channel create "third_party-elastic-7.x-sles12-sp4-pool-x86_64" for example.
This will be picked up by the script. An archive channel will be created from
this child channel.

#### Third party channel with regex match on product

Alternatively you can create one third party channel and specify a regex in the
channel details which defines which products should include this channel.

Create a parent channel with channel label like
"third_party-regex_match-x86_64" (syntax: third-party-software-parent-channel)
and channel name "Third party - Regex match based on channel summary". In that
parent channel create "third_party-elastic-7.x-updates-x86_64" (syntax:
third-party-software-channel-short) for example. In the channel summary,
specify a regex which is tested against vendor parent channel labels (for
example "sles12-sp4-pool-x86_64"). Example regex: `s/^sles?1[12]/`.
