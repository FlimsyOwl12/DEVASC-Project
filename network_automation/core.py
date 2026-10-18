"""IOS XE change plans, verification, redacted evidence and notifications."""

from dataclasses import asdict, dataclass, field
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import tempfile
import xml.etree.ElementTree as ET

import requests

NATIVE = 'http://cisco.com/ns/yang/Cisco-IOS-XE-native'
NC = 'urn:ietf:params:xml:ns:netconf:base:1.0'
CAP = 'urn:ietf:params:netconf:capability:'
ET.register_namespace('ios', NATIVE)
ET.register_namespace('nc', NC)
INTERFACE_TYPES = ('GigabitEthernet', 'TenGigabitEthernet', 'FastEthernet', 'Ethernet')


class AutomationError(Exception):
    """A safe diagnostic that never includes raw device/API replies."""


@dataclass(frozen=True)
class ChangeRequest:
    hostname: str
    interface_type: str
    interface_name: str
    description: str
    loopback: int
    ipv4: str

    def __post_init__(self):
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9-]{0,61}[A-Za-z0-9]|[A-Za-z]', self.hostname):
            raise AutomationError('Hostname must be 1–63 letters/digits/hyphens, starting with a letter.')
        if self.interface_type not in INTERFACE_TYPES:
            raise AutomationError('Unsupported interface type; use a documented IOS XE lab interface.')
        if not re.fullmatch(r'[0-9]+(?:/[0-9]+){0,3}(?:\.[0-9]+)?', self.interface_name):
            raise AutomationError('Invalid interface name.')
        if not 1 <= len(self.description) <= 128 or any(ord(c) < 32 or ord(c) == 127 for c in self.description):
            raise AutomationError('Description must contain 1–128 printable characters.')
        if isinstance(self.loopback, bool) or not isinstance(self.loopback, int) or not 0 <= self.loopback <= 2147483647:
            raise AutomationError('Loopback ID must be an integer from 0 to 2147483647.')
        try:
            address = ipaddress.IPv4Interface(self.ipv4)
        except (ValueError, TypeError):
            raise AutomationError('Provide an IPv4 address with a prefix, such as 192.0.2.10/32.') from None
        if address.ip.is_unspecified or address.ip.is_multicast or address.ip.is_loopback:
            raise AutomationError('Use an appropriate unicast lab address.')
        object.__setattr__(self, 'ipv4', str(address))


def parse(xml):
    if not isinstance(xml, str):
        raise AutomationError('The device returned no configuration XML.')
    if len(xml) > 8_000_000 or '<!DOCTYPE' in xml.upper() or '<!ENTITY' in xml.upper():
        raise AutomationError('Unsupported or oversized configuration XML.')
    try:
        return ET.fromstring(xml)
    except (ET.ParseError, TypeError):
        raise AutomationError('The device returned invalid configuration XML.') from None


def native(root):
    nodes = [root] if root.tag == f'{{{NATIVE}}}native' else root.findall(f'.//{{{NATIVE}}}native')
    if len(nodes) != 1:
        raise AutomationError('Expected exactly one Cisco-IOS-XE-native configuration tree.')
    return nodes[0]


def interface(root, kind, name):
    matches = [e for e in root.findall(f'{{{NATIVE}}}interface/{{{NATIVE}}}{kind}')
               if e.findtext(f'{{{NATIVE}}}name') == str(name)]
    if len(matches) > 1:
        raise AutomationError('Ambiguous interface configuration.')
    return matches[0] if matches else None


def values(xml, request):
    root = native(parse(xml))
    selected = interface(root, request.interface_type, request.interface_name)
    if selected is None:
        raise AutomationError('The selected physical interface does not exist; no changes were applied.')
    loop = interface(root, 'Loopback', request.loopback)
    addr = mask = None
    if loop is not None:
        primary = loop.find(f'{{{NATIVE}}}ip/{{{NATIVE}}}address/{{{NATIVE}}}primary')
        if primary is not None:
            addr = primary.findtext(f'{{{NATIVE}}}address')
            mask = primary.findtext(f'{{{NATIVE}}}mask')
    return {'hostname': root.findtext(f'{{{NATIVE}}}hostname'),
            'description': selected.findtext(f'{{{NATIVE}}}description'),
            'loopback_address': addr, 'loopback_mask': mask}


def desired(request):
    address = ipaddress.IPv4Interface(request.ipv4)
    return {'hostname': request.hostname, 'description': request.description,
            'loopback_address': str(address.ip), 'loopback_mask': str(address.netmask)}


def fingerprint(xml):
    root = parse(xml)
    for e in root.iter():
        if not e.text or not e.text.strip():
            e.text = None
        e.tail = None
    return hashlib.sha256(ET.tostring(root)).hexdigest()


def payload(request):
    root = ET.Element(f'{{{NC}}}config')
    config = ET.SubElement(root, f'{{{NATIVE}}}native')
    ET.SubElement(config, f'{{{NATIVE}}}hostname').text = request.hostname
    interfaces = ET.SubElement(config, f'{{{NATIVE}}}interface')
    selected = ET.SubElement(interfaces, f'{{{NATIVE}}}{request.interface_type}')
    ET.SubElement(selected, f'{{{NATIVE}}}name').text = request.interface_name
    ET.SubElement(selected, f'{{{NATIVE}}}description').text = request.description
    loop = ET.SubElement(interfaces, f'{{{NATIVE}}}Loopback')
    ET.SubElement(loop, f'{{{NATIVE}}}name').text = str(request.loopback)
    primary = ET.SubElement(ET.SubElement(ET.SubElement(loop, f'{{{NATIVE}}}ip'),
                                       f'{{{NATIVE}}}address'), f'{{{NATIVE}}}primary',
                            {f'{{{NC}}}operation': 'replace'})
    wanted = desired(request)
    ET.SubElement(primary, f'{{{NATIVE}}}address').text = wanted['loopback_address']
    ET.SubElement(primary, f'{{{NATIVE}}}mask').text = wanted['loopback_mask']
    return ET.tostring(root, encoding='unicode')


def redacted(xml):
    """Preserve the config tree; expose only target-independent lab config fields.

    Every other leaf value is hidden, including unknown secret-bearing fields.
    Output is a redacted XML view, not a full restorable backup.
    """
    root = parse(xml)
    tree = native(root)
    allowed = {id(e) for e in tree.findall(f'{{{NATIVE}}}hostname')}
    for group in tree.findall(f'{{{NATIVE}}}interface'):
        for entry in group:
            for path in ('name', 'description', 'ip/address/primary/address', 'ip/address/primary/mask'):
                expanded = '/'.join(f'{{{NATIVE}}}{part}' for part in path.split('/'))
                allowed.update(id(e) for e in entry.findall(expanded))
    for e in root.iter():
        # Attributes can also hold private data; the display never needs them.
        e.attrib.clear()
        if not len(e) and e.text and e.text.strip() and id(e) not in allowed:
            e.text = '[redacted]'
    ET.indent(root)
    return ET.tostring(root, encoding='unicode')


def check_capabilities(session):
    caps = [str(c) for c in session.server_capabilities]
    if not any(c.split('?')[0] == NATIVE for c in caps):
        raise AutomationError('This implementation requires the Cisco-IOS-XE-native device model.')
    for name in ('writable-running', 'rollback-on-error'):
        if not any(c.split('?')[0] == f'{CAP}{name}:1.0' for c in caps):
            raise AutomationError(f'The device must advertise :{name}; no change was attempted.')


@dataclass
class Plan:
    request: ChangeRequest
    current: dict
    baseline: str = field(repr=False)


def prepare(session, request):
    check_capabilities(session)
    current_xml = session.get_config(source='running').data_xml
    current = values(current_xml, request)
    wanted = desired(request)
    changed = [current['hostname'] != wanted['hostname'],
               current['description'] != wanted['description'],
               (current['loopback_address'], current['loopback_mask']) !=
               (wanted['loopback_address'], wanted['loopback_mask'])]
    if not all(changed):
        raise AutomationError('Choose three actual changes: hostname, description and loopback address must each differ.')
    return Plan(request, current, fingerprint(current_xml))


class Evidence:
    def __init__(self, root, simulated=False):
        parent = Path(root).expanduser()
        parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.directory = Path(tempfile.mkdtemp(prefix='activity5-', dir=parent))
        self.record = {'mode': 'SIMULATED' if simulated else 'LIVE',
                       'configuration_status': 'not_applied', 'notification_status': 'not_sent'}
        self.save()

    def write(self, name, text):
        # Names are internal constants, not chatbot-provided paths.
        path = self.directory / name
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
            stream.write(text)

    def save(self):
        self.write('result.json', json.dumps(self.record, indent=2) + '\n')


def apply(session, plan, evidence):
    """One atomic edit-config RPC under a running lock, followed by readback.

    A transport failure or post-edit mismatch leaves state uncertain. It is
    never reported as success and must be inspected before another change.
    """
    check_capabilities(session)
    evidence.record['requested_changes'] = asdict(plan.request)
    evidence.save()  # Confirm the report path is writable before any mutation.
    with session.locked('running'):
        before = session.get_config(source='running').data_xml
        if fingerprint(before) != plan.baseline:
            raise AutomationError('Running configuration changed since the preview. Create a fresh plan.')
        evidence.write('before.xml', redacted(before))
        evidence.write('requested-change.xml', payload(plan.request))
        evidence.record['configuration_status'] = 'attempted_unverified'
        evidence.save()
        try:
            reply = session.edit_config(target='running', config=payload(plan.request),
                                        default_operation='merge', error_option='rollback-on-error')
            if not reply.ok:
                raise AutomationError('The device did not acknowledge the change.')
            after = session.get_config(source='running').data_xml
            evidence.write('after.xml', redacted(after))
            observed = values(after, plan.request)
            if observed != desired(plan.request):
                raise AutomationError('Readback did not match all three requested changes.')
        except Exception:
            evidence.record['configuration_status'] = 'uncertain_review_device'
            evidence.save()
            raise AutomationError('Change was not verified. Inspect the device and evidence; do not blindly reapply.') from None
        evidence.record.update(configuration_status='verified', before=plan.current, after=observed)
        evidence.save()
    return evidence.record


class WebexNotifier:
    def __init__(self, token, room_id):
        if not token or not room_id or any(c in token + room_id for c in '\r\n'):
            raise AutomationError('Set WEBEX_ACCESS_TOKEN and WEBEX_ROOM_ID locally before applying changes.')
        self._token, self._room_id = token, room_id

    def send(self, text):
        try:
            reply = requests.post('https://webexapis.com/v1/messages',
                                  headers={'Authorization': f'Bearer {self._token}'},
                                  json={'roomId': self._room_id, 'text': text},
                                  timeout=20, allow_redirects=False)
            if reply.status_code not in (200, 201):
                # Require a message reference as well as an accepted creation status.
                raise AutomationError('WebEx did not accept the message; check room membership/token/permissions.')
            message_id = reply.json().get('id')
            if not isinstance(message_id, str) or not message_id.strip():
                raise AutomationError('WebEx returned no message reference.')
            return message_id
        except (requests.RequestException, ValueError, TypeError, AttributeError):
            raise AutomationError('WebEx notification failed; device status is recorded separately.') from None


def notify(notifier, evidence):
    if evidence.record['configuration_status'] != 'verified':
        raise AutomationError('Cannot announce success for an unverified configuration.')
    mode = evidence.record['mode']
    change = evidence.record['requested_changes']
    text = (f'[{mode}] Activity 5: verified three running-config changes. '
            f'Hostname: {change["hostname"]}; {change["interface_type"]}{change["interface_name"]} '
            f'description updated; Loopback{change["loopback"]}: {change["ipv4"]}. '
            'Running configuration was read back and checked; startup-config was not changed.')
    try:
        message_id = notifier.send(text)
    except Exception:
        evidence.record['notification_status'] = 'failed_or_unknown'
        evidence.save()
        raise AutomationError('Configuration is verified but notification failed or is uncertain. Inspect the room before retrying; do not reapply.') from None
    evidence.record.update(notification_status='simulated' if mode == 'SIMULATED' else 'sent',
                           message_id=message_id)
    evidence.write('notification.txt', text + '\n')
    evidence.save()
    return message_id
