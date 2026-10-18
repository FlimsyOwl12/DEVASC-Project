"""Activity 5 validation, transaction, evidence, notification and chatbot checks."""
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET

from network_automation import core
from network_automation.__main__ import chatbot, live_session, main
from network_automation.simulator import SimulatedDevice, SimulatedNotifier


def request(**changes):
    values = dict(hostname='PALPAK-LAB', interface_type='GigabitEthernet', interface_name='1',
                  description='Activity 5 & lab', loopback=100, ipv4='192.0.2.10/32')
    values.update(changes)
    return core.ChangeRequest(**values)


class Activity5ValidationTests(unittest.TestCase):
    def test_request_rejects_unsafe_or_unsupported_values(self):
        for changes in [dict(hostname='bad hostname'), dict(hostname='-bad'), dict(hostname='a'*64),
                        dict(interface_type='username'), dict(interface_name='../secret'),
                        dict(description='bad\nline'), dict(description=''), dict(loopback=-1),
                        dict(loopback=True), dict(ipv4='::1/128'), dict(ipv4='bad'),
                        dict(ipv4='127.0.0.1/32'), dict(ipv4='224.0.0.1/32')]:
            with self.subTest(changes=changes), self.assertRaises(core.AutomationError):
                request(**changes)

    def test_payload_uses_native_model_and_escapes_description(self):
        root = ET.fromstring(core.payload(request()))
        native = core.native(root)
        self.assertEqual(native.findtext(f'{{{core.NATIVE}}}hostname'), 'PALPAK-LAB')
        self.assertEqual(native.findtext(f'{{{core.NATIVE}}}interface/{{{core.NATIVE}}}GigabitEthernet/{{{core.NATIVE}}}description'), 'Activity 5 & lab')
        primary = native.find(f'.//{{{core.NATIVE}}}primary')
        self.assertEqual(primary.attrib[f'{{{core.NC}}}operation'], 'replace')
        self.assertEqual(primary.findtext(f'{{{core.NATIVE}}}mask'), '255.255.255.255')

    def test_missing_interface_never_creates_plan(self):
        with self.assertRaises(core.AutomationError):
            core.prepare(SimulatedDevice(), request(interface_name='999'))

    def test_three_real_changes_are_required(self):
        for changes in [dict(hostname='LAB-OLD'), dict(description='Old lab description')]:
            with self.assertRaises(core.AutomationError):
                core.prepare(SimulatedDevice(), request(**changes))

    def test_native_model_and_atomic_edit_capabilities_are_required(self):
        for excluded in [core.NATIVE, core.CAP+'rollback-on-error', core.CAP+'writable-running']:
            device = SimulatedDevice()
            device.server_capabilities = [c for c in device.server_capabilities if not c.startswith(excluded)]
            with self.assertRaises(core.AutomationError):
                core.prepare(device, request())
            self.assertEqual(device.edits, 0)

    def test_configuration_parser_rejects_entities_bad_xml_and_missing_data(self):
        for xml in [None, '<broken', '<!DOCTYPE x><data/>', '<!ENTITY x "secret"><data/>', '<data/>']:
            with self.assertRaises(core.AutomationError):
                core.values(xml, request())

    def test_ambiguous_native_tree_is_rejected(self):
        with self.assertRaises(core.AutomationError):
            core.values(f'<data><native xmlns="{core.NATIVE}"/><native xmlns="{core.NATIVE}"/></data>', request())

    def test_redaction_hides_unknown_leaves_and_attributes(self):
        xml = SimulatedDevice().xml.replace('<description>', '<authentication token="secret-attribute"><name>hidden-login</name></authentication><description>')
        output = core.redacted(xml)
        for secret in ['private-user', 'private-secret', 'hidden-login', 'secret-attribute']:
            self.assertNotIn(secret, output)
        self.assertIn('LAB-OLD', output)
        self.assertIn('Old lab description', output)
        self.assertIn('[redacted]', output)


class Activity5TransactionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.device = SimulatedDevice()
        self.plan = core.prepare(self.device, request())
        self.evidence = core.Evidence(self.temp.name, simulated=True)

    def test_atomic_edit_verifies_all_changes_and_writes_private_evidence(self):
        record = core.apply(self.device, self.plan, self.evidence)
        self.assertEqual(record['configuration_status'], 'verified')
        self.assertEqual(record['after'], core.desired(request()))
        self.assertEqual(self.device.edits, 1)
        self.assertFalse(self.device.lock_held)
        for name in ['before.xml', 'after.xml', 'requested-change.xml', 'result.json']:
            path = self.evidence.directory / name
            self.assertTrue(path.exists())
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertNotIn('private-secret', path.read_text())
        self.assertEqual(record['mode'], 'SIMULATED')

    def test_stale_preview_aborts_before_edit(self):
        self.device.xml = self.device.xml.replace('LAB-OLD', 'LAB-CHANGED')
        with self.assertRaisesRegex(core.AutomationError, 'fresh plan'):
            core.apply(self.device, self.plan, self.evidence)
        self.assertEqual(self.device.edits, 0)
        self.assertFalse(self.device.lock_held)

    def test_rpc_failure_does_not_expose_server_secrets(self):
        self.device.edit_config = Mock(side_effect=RuntimeError('private-secret password=secret'))
        with self.assertRaises(core.AutomationError) as caught:
            core.apply(self.device, self.plan, self.evidence)
        self.assertNotIn('private-secret', str(caught.exception))
        self.assertEqual(self.evidence.record['configuration_status'], 'uncertain_review_device')
        self.assertFalse(self.device.lock_held)

    def test_negative_acknowledgment_is_not_success(self):
        self.device.edit_config = Mock(return_value=Mock(ok=False))
        with self.assertRaises(core.AutomationError):
            core.apply(self.device, self.plan, self.evidence)
        self.assertNotEqual(self.evidence.record['configuration_status'], 'verified')

    def test_readback_mismatch_prevents_success_notification(self):
        self.device.edit_config = Mock(return_value=Mock(ok=True))
        with self.assertRaises(core.AutomationError):
            core.apply(self.device, self.plan, self.evidence)
        notifier = Mock()
        with self.assertRaises(core.AutomationError):
            core.notify(notifier, self.evidence)
        notifier.send.assert_not_called()

    def test_evidence_failure_prevents_device_write(self):
        self.evidence.save = Mock(side_effect=OSError('disk full'))
        with self.assertRaises(OSError):
            core.apply(self.device, self.plan, self.evidence)
        self.assertEqual(self.device.edits, 0)

    def test_notification_failure_keeps_verified_device_state_separate(self):
        core.apply(self.device, self.plan, self.evidence)
        with self.assertRaises(core.AutomationError):
            core.notify(Mock(send=Mock(side_effect=RuntimeError('secret'))), self.evidence)
        self.assertEqual(self.evidence.record['configuration_status'], 'verified')
        self.assertEqual(self.evidence.record['notification_status'], 'failed_or_unknown')
        self.assertEqual(self.device.edits, 1)
        core.notify(SimulatedNotifier(), self.evidence)
        self.assertEqual(self.device.edits, 1)
        self.assertEqual(self.evidence.record['notification_status'], 'simulated')

    def test_simulated_notification_remains_explicitly_simulated(self):
        core.apply(self.device, self.plan, self.evidence)
        notifier = SimulatedNotifier()
        core.notify(notifier, self.evidence)
        self.assertTrue(notifier.messages[0].startswith('[SIMULATED]'))
        self.assertEqual(self.evidence.record['notification_status'], 'simulated')


class Activity5WebexTests(unittest.TestCase):
    def test_missing_or_invalid_credentials_are_rejected(self):
        for token, room in [('', 'room'), ('token', ''), ('token\n', 'room')]:
            with self.assertRaises(core.AutomationError):
                core.WebexNotifier(token, room)

    def test_message_uses_fixed_https_endpoint_without_redirects(self):
        reply = Mock(status_code=200)
        reply.json.return_value = {'id': 'message-reference'}
        with patch.object(core.requests, 'post', return_value=reply) as post:
            self.assertEqual(core.WebexNotifier('dummy-token', 'dummy-room').send('Verified update'), 'message-reference')
        args, kwargs = post.call_args
        self.assertEqual(args, ('https://webexapis.com/v1/messages',))
        self.assertEqual(kwargs['json'], {'roomId': 'dummy-room', 'text': 'Verified update'})
        self.assertFalse(kwargs['allow_redirects'])
        self.assertEqual(kwargs['headers']['Authorization'], 'Bearer dummy-token')
        self.assertEqual(kwargs['timeout'], 20)

    def test_api_failure_and_missing_message_reference_do_not_succeed(self):
        for status, body in [(401, {'secret': 'dummy-token'}), (429, {}), (302, {}), (200, {}), (200, [])]:
            reply = Mock(status_code=status)
            reply.json.return_value = body
            with patch.object(core.requests, 'post', return_value=reply), self.assertRaises(core.AutomationError) as caught:
                core.WebexNotifier('dummy-token', 'dummy-room').send('Verified update')
            self.assertNotIn('dummy-token', str(caught.exception))

    def test_timeout_is_reported_without_request_details(self):
        with patch.object(core.requests, 'post', side_effect=core.requests.Timeout('dummy-token')), self.assertRaises(core.AutomationError) as caught:
            core.WebexNotifier('dummy-token', 'dummy-room').send('Verified update')
        self.assertNotIn('dummy-token', str(caught.exception))


class Activity5ChatbotTests(unittest.TestCase):
    def run_chat(self, commands, simulated=True, notifier=None):
        device = SimulatedDevice()
        with tempfile.TemporaryDirectory() as folder:
            stream = io.StringIO()
            with redirect_stdout(stream):
                code = chatbot(device, notifier, folder, simulated,
                               read=lambda prompt: next(commands), write=print)
            reports = [json.loads(p.read_text()) for p in Path(folder).glob('*/result.json')]
        return device, code, stream.getvalue(), reports

    def commands(self, confirm='APPLY PALPAK-LAB'):
        return iter(['change', 'PALPAK-LAB', '', '', 'Lab description', '', '192.0.2.10/32',
                     'apply', confirm, 'quit'])

    def test_cancelled_confirmation_does_not_edit(self):
        device, code, text, reports = self.run_chat(self.commands('NO'), notifier=SimulatedNotifier())
        self.assertEqual(device.edits, 0)
        self.assertEqual(code, 0)
        self.assertEqual(reports, [])

    def test_missing_live_webex_settings_prevent_any_configuration_write(self):
        with patch.dict(os.environ, {'WEBEX_ACCESS_TOKEN': '', 'WEBEX_ROOM_ID': ''}):
            device, code, text, reports = self.run_chat(self.commands(), simulated=False)
        self.assertEqual(device.edits, 0)
        self.assertEqual(code, 1)
        self.assertEqual(reports, [])
        self.assertIn('WEBEX_ACCESS_TOKEN', text)

    def test_demo_run_cannot_read_dotenv_or_use_live_transport(self):
        with tempfile.TemporaryDirectory() as folder, patch('network_automation.__main__.load_dotenv') as dotenv, patch('network_automation.__main__.live_session') as live, redirect_stdout(io.StringIO()) as out:
            self.assertEqual(main(['--demo', '--run-example', '--evidence-dir', folder]), 0)
            dotenv.assert_not_called()
            live.assert_not_called()
            records = list(Path(folder).glob('*/result.json'))
            self.assertEqual(len(records), 1)
            record = json.loads(records[0].read_text())
            self.assertEqual(record['configuration_status'], 'verified')
            self.assertEqual(record['notification_status'], 'simulated')
            self.assertIn('SIMULATED MODE', out.getvalue())
            self.assertNotIn('private-secret', out.getvalue())

    def test_notification_retry_does_not_repeat_configuration_edit(self):
        notifier = Mock()
        notifier.send.side_effect = [RuntimeError('timeout'), 'message-2']
        commands = list(self.commands())[:-1] + ['notify', 'RETRY', 'quit']
        device, code, text, reports = self.run_chat(iter(commands), notifier=notifier)
        self.assertEqual(device.edits, 1)
        self.assertEqual(reports[0]['notification_status'], 'simulated')
        self.assertEqual(code, 0)

    def test_quit_and_unknown_commands_do_not_write(self):
        device, code, text, records = self.run_chat(iter(['unknown', 'help', 'quit']))
        self.assertEqual(device.edits, 0)
        self.assertEqual(code, 0)
        self.assertIn('Unknown command', text)

    def test_successful_notification_cannot_be_sent_twice(self):
        notifier = SimulatedNotifier()
        commands = list(self.commands())[:-1] + ['notify', 'quit']
        device, code, text, records = self.run_chat(iter(commands), notifier=notifier)
        self.assertEqual(device.edits, 1)
        self.assertEqual(len(notifier.messages), 1)
        self.assertIn('no duplicate was sent', text)

    def test_live_mode_requires_an_explicit_device(self):
        with patch.dict(os.environ, {'NETCONF_HOST': '', 'NETCONF_USERNAME': ''}):
            with self.assertRaises(core.AutomationError), live_session():
                self.fail('Must not connect')

    def test_run_example_cannot_be_used_in_live_mode(self):
        with redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as error:
            main(['--run-example'])
        self.assertEqual(error.exception.code, 2)


class Activity5LiveConnectionTests(unittest.TestCase):
    def test_live_adapter_verifies_host_key_and_closes_session(self):
        import types
        fake_manager = Mock()
        session = fake_manager.connect.return_value
        module = types.ModuleType('ncclient')
        module.manager = fake_manager
        environment = {'NETCONF_HOST': '192.0.2.20', 'NETCONF_PORT': '830',
                       'NETCONF_USERNAME': 'test-user', 'NETCONF_PASSWORD': 'dummy-device-password'}
        with patch.dict(os.environ, environment), patch.dict('sys.modules', {'ncclient': module}):
            with live_session() as connected:
                self.assertIs(connected, session)
        kwargs = fake_manager.connect.call_args.kwargs
        self.assertTrue(kwargs['hostkey_verify'])
        self.assertFalse(kwargs['allow_agent'])
        self.assertFalse(kwargs['look_for_keys'])
        self.assertEqual(kwargs['port'], 830)
        session.close_session.assert_called_once()

    def test_live_adapter_does_not_expose_connection_exceptions(self):
        import types
        module = types.ModuleType('ncclient')
        module.manager = Mock(connect=Mock(side_effect=RuntimeError('dummy-device-password')))
        environment = {'NETCONF_HOST': '192.0.2.20', 'NETCONF_USERNAME': 'test-user',
                       'NETCONF_PASSWORD': 'dummy-device-password'}
        with patch.dict(os.environ, environment), patch.dict('sys.modules', {'ncclient': module}), self.assertRaises(core.AutomationError) as caught:
            with live_session():
                self.fail('Must not connect')
        self.assertNotIn('dummy-device-password', str(caught.exception))

    def test_invalid_port_is_rejected_before_connecting(self):
        for port in ['0', '-1', '65536', 'not-a-port']:
            with patch.dict(os.environ, {'NETCONF_HOST': '192.0.2.20', 'NETCONF_USERNAME': 'user', 'NETCONF_PORT': port}), self.assertRaises(core.AutomationError):
                with live_session():
                    self.fail('Must not connect')
