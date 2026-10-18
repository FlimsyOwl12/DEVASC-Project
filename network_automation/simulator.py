"""Stateful, explicitly simulated IOS XE and WebEx adapters; no network calls."""
from contextlib import contextmanager
from copy import deepcopy
from types import SimpleNamespace
import xml.etree.ElementTree as ET

from .core import CAP, NATIVE, NC, interface, native, parse

INITIAL_XML = f'''<data xmlns="{NC}"><native xmlns="{NATIVE}">
<hostname>LAB-OLD</hostname><username><name>private-user</name><secret>private-secret</secret></username>
<interface><GigabitEthernet><name>1</name><description>Old lab description</description></GigabitEthernet>
</interface></native></data>'''


class SimulatedDevice:
    server_capabilities = [NATIVE + '?module=Cisco-IOS-XE-native',
                           CAP + 'writable-running:1.0', CAP + 'rollback-on-error:1.0']

    def __init__(self):
        self.xml = INITIAL_XML
        self.edits = 0
        self.lock_held = False

    @contextmanager
    def locked(self, target):
        if self.lock_held or target != 'running':
            raise RuntimeError('Datastore lock conflict')
        self.lock_held = True
        try:
            yield
        finally:
            self.lock_held = False

    def get_config(self, source):
        if source != 'running':
            raise ValueError('Only running is simulated')
        return SimpleNamespace(data_xml=self.xml)

    def edit_config(self, target, config, default_operation, error_option):
        if not self.lock_held or (target, default_operation, error_option) != ('running', 'merge', 'rollback-on-error'):
            raise RuntimeError('Invalid simulated transaction')
        tree, incoming = parse(self.xml), native(parse(config))
        dest = native(tree)
        dest.find(f'{{{NATIVE}}}hostname').text = incoming.findtext(f'{{{NATIVE}}}hostname')
        for entry in incoming.find(f'{{{NATIVE}}}interface'):
            kind = entry.tag.split('}')[-1]
            name = entry.findtext(f'{{{NATIVE}}}name')
            previous = interface(dest, kind, name)
            if kind == 'Loopback':
                if previous is None:
                    previous = ET.SubElement(dest.find(f'{{{NATIVE}}}interface'), f'{{{NATIVE}}}Loopback')
                    ET.SubElement(previous, f'{{{NATIVE}}}name').text = name
                old_ip = previous.find(f'{{{NATIVE}}}ip')
                if old_ip is not None:
                    previous.remove(old_ip)
                previous.append(deepcopy(entry.find(f'{{{NATIVE}}}ip')))
            else:
                description = previous.find(f'{{{NATIVE}}}description')
                if description is None:
                    description = ET.SubElement(previous, f'{{{NATIVE}}}description')
                description.text = entry.findtext(f'{{{NATIVE}}}description')
        for e in tree.iter():
            e.attrib.clear()
        self.xml = ET.tostring(tree, encoding='unicode')
        self.edits += 1
        return SimpleNamespace(ok=True)


class SimulatedNotifier:
    def __init__(self):
        self.messages = []

    def send(self, text):
        self.messages.append(text)
        return 'SIMULATED-message-' + str(len(self.messages))
