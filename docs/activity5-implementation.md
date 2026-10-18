# Activity 5 — network programmability and automation

We built a terminal chatbot in `network_automation/` for the course's network-change workflow. It reads a Cisco IOS XE lab device's running configuration through NETCONF, previews three changes, applies them in one edit request, reads the values back and then posts an update to a WebEx Teams room. The program also save redacted before/after XML and a result file so the team can explain what happened.

The implementation and local checks are complete on this branch. **A real IOS XE device and WebEx room have not been supplied or tested.** The included demonstration and protocol lab are explicitly simulated. They must not be described as actual device configuration or a delivered WebEx message.

## What is implemented

| Requirement from Tab 1 | Implementation | Verification status |
| --- | --- | --- |
| Simple support chatbot | `show`, `change`, `apply`, `notify`, `schema`, `cancel`, `quit` | Offline command-flow tests and runnable example |
| Current running-config | `get_config(source='running')`; redacted XML display/report | Simulated device and real SSH/NETCONF exchange against a local fixture |
| Three changes | Hostname; existing physical interface description; lab loopback IPv4/prefix | All three values checked after the edit |
| New running-config | Second NETCONF retrieval; compare values with requested values | Positive and mismatch cases covered |
| YANG model | `palpak-change-request.yang`; adapter targets `Cisco-IOS-XE-native` | Request module validated with pyang; native namespace/payload checked |
| WebEx room communication | HTTPS Messages API; room ID, bearer token, timeout and message reference | API replies mocked; no actual account/room delivery yet |
| Evidence | `before.xml`, `after.xml`, `requested-change.xml`, `result.json`, `notification.txt` | Private/ignored output; simulated results labelled |
| Rubric and presentation | Workflow/evidence guide below | Official assessment and live demonstration remain team work |

The chatbot runs in a terminal. WebEx is the outbound update channel; this implementation does not host an inbound WebEx chatbot/webhook service.

## Run the demonstration now — no accounts needed

From the repository root, with the normal application dependencies installed:

```bash
python -m network_automation --demo --run-example
```

For the interactive demonstration:

```bash
python -m network_automation --demo
```

The fixed example starts from `LAB-OLD`, changes the hostname to `PALPAK-LAB`, updates `GigabitEthernet1`'s description and adds the documentation-range address `192.0.2.10/32` on `Loopback100`. It verifies the three requested values and records a **simulated** notification. It reads no `.env`, constructs no live device/API client and opens no network connection.

The default evidence goes under ignored `activity5-evidence/`, in a unique directory. `result.json` separates `configuration_status` from `notification_status` and includes `mode: SIMULATED`. Do not rename simulated evidence to live evidence. The example address is for demonstration; use an address approved for the actual lab when connecting to a real device.

## Connect the live lab

1. Obtain a course-authorized Cisco IOS XE device/VM with NETCONF enabled, a suitable login and its SSH host-key fingerprint. Confirm its software supports the native paths listed below and advertises `:writable-running` and `:rollback-on-error`. Other vendors/models are not supported by this adapter.
2. Verify the SSH host key using your lab administrator's fingerprint and place the trusted entry for the host/port in your normal SSH `known_hosts`. The application keeps host-key verification enabled; it does not silently trust an unknown server.
3. Install the optional client into your project environment:

   ```bash
   python -m pip install -r requirements-network.txt
   ```

4. Add these values to your existing private project-root `.env`, keeping the GraphHopper key as it is:

   ```dotenv
   NETCONF_HOST=your-lab-host
   NETCONF_PORT=830
   NETCONF_USERNAME=your-lab-user
   NETCONF_PASSWORD=your-private-password
   WEBEX_ACCESS_TOKEN=your-private-token
   WEBEX_ROOM_ID=your-team-room-id
   ```

   These are placeholders, not usable credentials. The actual `.env` remains ignored. Exported variables take precedence. If the device password is absent, the live client asks for it privately. The WebEx token and room must be configured before `apply` can edit the device.

5. For WebEx, the team needs an account or bot/integration with access to the target room and permission to create messages. The room ID and access token are separate from the GraphHopper key. Follow the [official WebEx messaging guide](https://developer.webex.com/docs/create-spaces-add-participants-post-messages-from-postman) to create/select a space and obtain access. Enter the token locally; do not send it to chat or commit it. Token lifetime and permissions depend on the credential type.
6. Start the live client:

   ```bash
   python -m network_automation
   ```

7. Use `show`, then `schema` to inspect the device and, when supported, retrieve its `Cisco-IOS-XE-native` YANG module into the private evidence folder. Use `change` and supply values for the lab's existing interface, a new hostname and a loopback/address. Review the displayed current/requested values.
8. Use `apply` and type the exact `APPLY <new-hostname>` confirmation. The client rechecks the configuration under a running lock, applies the request, retrieves the result and sends a WebEx success update only after all three values match. It does not copy running-config to startup-config.

A missing WebEx configuration blocks the write. A wrong/expired token or inaccessible room can still fail after the device changes were verified; in that case the evidence reports the device and notification states separately. Check the room before using `notify` to retry only the message. A timeout may mean the service accepted it but the reply was lost. The application never retries the configuration automatically and refuses to send another message for an already recorded success.

## Data model and transaction behavior

The application request model describes the six requested inputs; it is not a replacement for the router's YANG model and is not installed on the router. The Python validator applies its hostname, interface, description, loopback and IPv4 constraints. The device is authoritative for native-model validity.

| Changed value | Native-model path |
| --- | --- |
| Hostname | `/native/hostname` |
| Interface description | `/native/interface/{interface-type}[name=...]/description` |
| Loopback IPv4 | `/native/interface/Loopback[name=...]/ip/address/primary/{address,mask}` |

The native namespace is `http://cisco.com/ns/yang/Cisco-IOS-XE-native`. All three requested changes must differ from their previewed values. The physical interface must already exist. Values are XML-escaped; unknown interface types and malformed requests are rejected.

The live adapter requires writable running plus rollback-on-error. It locks running, rejects a stale preview, and sends one `edit-config` with `default-operation=merge` and `error-option=rollback-on-error`. The loopback primary address is replaced as a unit so an older primary address is not retained. It then retrieves running again and checks the three values. Devices with only a candidate workflow need another adapter; this client fails before writing instead of pretending to support them.

Rollback-on-error is the server's handling of an edit RPC error. It does **not** establish that a transport failure or a failed post-edit readback rolled back. Those cases are recorded as `uncertain_review_device`; inspect the device before applying anything else. A confirmed value match is recorded as `verified`. A failed notification never changes that state to “device unchanged.”

Reports use redacted XML: configuration structure remains, and hostname/interface name/description and IPv4 fields are visible; other leaf values and attributes are hidden. This is not a full restorable configuration backup. Location/interface data may still be private. Keep reports outside tracked files and review them before sharing. Use the default ignored evidence path, or choose a private path outside the repository with `--evidence-dir`.

## Verification completed on October 18, 2026

- The full offline suite passes **100 tests**: the original 69 plus 31 Activity 5 cases. The shared runner now clears NETCONF/WebEx variables as well as the GraphHopper key and blocks HTTP/socket connections.
- The no-account example completes preview, edit, readback and a simulated message without reading dotenv or calling a real endpoint.
- `pyang` validates the request model.
- The optional protocol check uses the real ncclient, a pinned ephemeral ECDSA SSH key and a loopback-only NETCONF fixture. It verifies lock → read → edit → readback → unlock/close. The device and notification remain simulated; no real router or WebEx account was contacted.
- GitHub has a separate protocol/YANG job on Python 3.10 and 3.14, alongside the shared offline suite. The existing Jenkins job discovers the new offline tests after this branch merges; its historic 69-test reports remain valid for their earlier commits.

To reproduce the optional protocol/model checks:

```bash
python -m pip install -r requirements-network-dev.txt
pyang network_automation/yang/palpak-change-request.yang
python scripts/verify_activity5_transport.py
```

The protocol check opens only a loopback socket; it is separate from the network-blocked unittest runner. It needs no device credentials and keeps its generated SSH key in memory.

## Evidence still needed from the live environment

- [x] Application objectives and code, request model and documented native mapping.
- [x] Offline tests, simulated demonstration and local SSH/NETCONF interoperability check.
- [ ] Record the actual device/VM/software and advertised native model/capabilities.
- [ ] Retrieve the real current running-config, execute the three agreed changes and retain the verified new running-config.
- [ ] Save the actual WebEx message reference/screenshot, or the instructor's explicit deferral for the collaboration portion.
- [ ] Present the live results and complete the official rubric/reflection from actual team experience.

The user confirmed that no WebEx account/room/access is available yet. Code and local validation are ready; live room delivery cannot be marked done until that access is supplied.

Sources: [ncclient manager API](https://ncclient.readthedocs.io/en/v0.7.1/manager.html), [Cisco native YANG model](https://github.com/YangModels/yang/blob/main/vendor/cisco/xe/17151/Cisco-IOS-XE-native.yang), [Cisco NETCONF/YANG lab](https://ciscolearning.github.io/cisco-learning-codelabs/posts/yangsuite-netconf/), and [WebEx Messages API](https://developer.webex.com/messaging/docs/api/v1/messages).
