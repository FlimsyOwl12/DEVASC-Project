"""Exercise real ncclient/SSH/NETCONF against a loopback-only simulated device.

This is protocol interoperability evidence, not a Cisco router or WebEx run.
Install requirements-network.txt first. Host keys are ephemeral and pinned.
"""
from pathlib import Path
import socket
import sys
import tempfile
import threading
import xml.etree.ElementTree as ET

import paramiko
from ncclient import manager

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from network_automation.core import NC, AutomationError, Evidence, apply, desired, notify, prepare
from network_automation.simulator import SimulatedDevice, SimulatedNotifier
from network_automation.core import ChangeRequest

END = b']]>]]>'


class LabSSH(paramiko.ServerInterface):
    def __init__(self):
        self.ready = threading.Event()

    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL if (username, password) == ('protocol-test', 'dummy-lab-password') else paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'password'

    def check_channel_request(self, kind, channel_id):
        return paramiko.OPEN_SUCCEEDED if kind == 'session' else paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_subsystem_request(self, channel, name):
        if name == 'netconf':
            self.ready.set()
            return True
        return False


def serve(listener, key, errors):
    transport = channel = None
    try:
        connection, _ = listener.accept()
        transport = paramiko.Transport(connection)
        transport.add_server_key(key)
        server = LabSSH()
        transport.start_server(server=server)
        channel = transport.accept(15)
        if channel is None or not server.ready.wait(15):
            raise RuntimeError('NETCONF subsystem not requested')
        channel.settimeout(15)
        device = SimulatedDevice()
        hello = ET.Element(f'{{{NC}}}hello')
        caps = ET.SubElement(hello, f'{{{NC}}}capabilities')
        for cap in [NC] + device.server_capabilities:
            ET.SubElement(caps, f'{{{NC}}}capability').text = cap
        ET.SubElement(hello, f'{{{NC}}}session-id').text = '1'
        channel.sendall(ET.tostring(hello) + END)
        buffer = b''
        while True:
            while END not in buffer:
                data = channel.recv(65536)
                if not data:
                    return
                buffer += data
            xml, buffer = buffer.split(END, 1)
            root = ET.fromstring(xml)
            if root.tag == f'{{{NC}}}hello':
                continue
            reply = ET.Element(f'{{{NC}}}rpc-reply', {'message-id': root.attrib['message-id']})
            operation = list(root)[0]
            name = operation.tag.split('}')[-1]
            if name == 'get-config':
                reply.append(ET.fromstring(device.get_config('running').data_xml))
            elif name == 'lock':
                if device.lock_held:
                    raise RuntimeError('Duplicate lock')
                device.lock_held = True
                ET.SubElement(reply, f'{{{NC}}}ok')
            elif name == 'unlock':
                device.lock_held = False
                ET.SubElement(reply, f'{{{NC}}}ok')
            elif name == 'edit-config':
                config = operation.find(f'{{{NC}}}config')
                device.edit_config('running', ET.tostring(config, encoding='unicode'),
                                   operation.findtext(f'{{{NC}}}default-operation'),
                                   operation.findtext(f'{{{NC}}}error-option'))
                ET.SubElement(reply, f'{{{NC}}}ok')
            elif name == 'close-session':
                ET.SubElement(reply, f'{{{NC}}}ok')
            else:
                raise RuntimeError('Unexpected NETCONF operation')
            channel.sendall(ET.tostring(reply) + END)
            if name == 'close-session':
                return
    except Exception as error:
        errors.append(type(error).__name__)
    finally:
        if channel:
            channel.close()
        if transport:
            transport.close()
        listener.close()


def main():
    errors = []
    key = paramiko.ECDSAKey.generate()
    listener = socket.socket()
    listener.bind(('127.0.0.1', 0))
    listener.listen(1)
    listener.settimeout(20)
    port = listener.getsockname()[1]
    thread = threading.Thread(target=serve, args=(listener, key, errors), daemon=True)
    thread.start()
    try:
        with tempfile.TemporaryDirectory(prefix='activity5-protocol-') as directory:
            with manager.connect(host='127.0.0.1', port=port, username='protocol-test',
                                 password='dummy-lab-password', hostkey_verify=True,
                                 hostkey_b64=key.get_base64(), allow_agent=False,
                                 look_for_keys=False, timeout=15) as session:
                request = ChangeRequest('PALPAK-LAB', 'GigabitEthernet', '1', 'Protocol lab test', 100, '192.0.2.10/32')
                plan = prepare(session, request)
                evidence = Evidence(directory, simulated=True)
                apply(session, plan, evidence)
                assert evidence.record['after'] == desired(request)
                notify(SimulatedNotifier(), evidence)
                assert evidence.record['notification_status'] == 'simulated'
                assert 'private-secret' not in (evidence.directory/'before.xml').read_text()
        thread.join(5)
        if thread.is_alive() or errors:
            raise RuntimeError('Local protocol server did not complete cleanly: ' + ', '.join(errors))
        print('PASS: real ncclient, pinned SSH host key, NETCONF lock/edit/readback/unlock.')
        print('SIMULATED DEVICE AND NOTIFICATION: no Cisco hardware or WebEx service was contacted.')
        return 0
    finally:
        listener.close()


if __name__ == '__main__':
    raise SystemExit(main())
