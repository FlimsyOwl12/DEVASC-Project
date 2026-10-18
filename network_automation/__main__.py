"""Terminal chatbot for a live IOS XE lab or an isolated simulated demonstration."""

import argparse
from contextlib import contextmanager
import getpass
import json
import os
from pathlib import Path
import sys

from dotenv import load_dotenv

from .core import (AutomationError, ChangeRequest, Evidence, NATIVE, WebexNotifier,
                   apply, notify, prepare, redacted)
from .simulator import SimulatedDevice, SimulatedNotifier

ROOT = Path(__file__).resolve().parents[1]
HELP = '''Commands:
  show      Display the running configuration XML with private leaf values hidden.
  change    Enter the three-change request, then review old and new values.
  apply     Confirm and apply the prepared request; verify and send the update.
  notify    Retry only the last verified notification (check the room first).
  schema    Show the YANG model/capabilities and save the device schema if available.
  cancel    Clear the prepared request.
  quit      Close the session.
'''


@contextmanager
def live_session():
    host = os.getenv('NETCONF_HOST', '').strip()
    user = os.getenv('NETCONF_USERNAME', '').strip()
    if not host or not user:
        raise AutomationError('Set NETCONF_HOST and NETCONF_USERNAME for your authorized IOS XE lab.')
    try:
        port = int(os.getenv('NETCONF_PORT', '830'))
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        raise AutomationError('NETCONF_PORT must be between 1 and 65535.') from None
    try:
        from ncclient import manager
    except ImportError:
        raise AutomationError('Install live dependencies: python -m pip install -r requirements-network.txt') from None
    password = os.getenv('NETCONF_PASSWORD') or getpass.getpass('NETCONF password (not saved): ')
    try:
        session = manager.connect(host=host, port=port, username=user, password=password,
                                  hostkey_verify=True, allow_agent=False, look_for_keys=False,
                                  timeout=30)
    except Exception:
        raise AutomationError('NETCONF connection failed. Check the device, credentials and trusted SSH host key.') from None
    try:
        yield session
    finally:
        try:
            session.close_session()
        except Exception:
            pass


def read_request(read):
    try:
        return ChangeRequest(
            read('New hostname: ').strip(),
            read('Interface type [GigabitEthernet]: ').strip() or 'GigabitEthernet',
            read('Existing interface name [1]: ').strip() or '1',
            read('New interface description: ').strip(),
            int(read('Lab loopback ID [100]: ').strip() or '100'),
            read('Loopback IPv4/prefix: ').strip())
    except ValueError:
        raise AutomationError('The loopback ID must be an integer.') from None


def chatbot(session, notifier, evidence_root, simulated, read=input, write=print):
    write('SIMULATED MODE — no router or WebEx calls.' if simulated else 'LIVE MODE — authorized IOS XE lab and WebEx room.')
    write(HELP)
    plan = last = None
    failed = False
    while True:
        try:
            command = read('activity5> ').strip().lower()
            if command in ('quit', 'q', 'exit'):
                return 1 if failed else 0
            if command in ('help', '?', ''):
                write(HELP)
            elif command == 'show':
                write('RUNNING CONFIGURATION — redacted XML view; not a restorable backup')
                write(redacted(session.get_config(source='running').data_xml))
            elif command == 'change':
                plan = None
                request = read_request(read)
                plan = prepare(session, request)
                from .core import desired
                write(json.dumps({'before': plan.current, 'requested': desired(request)}, indent=2))
                write('Review the three changes. Use apply to continue or cancel to clear them.')
            elif command == 'cancel':
                plan = None
                write('Prepared request cleared.')
            elif command == 'apply':
                if plan is None:
                    raise AutomationError('Use change and review a plan first.')
                # Require notification configuration before any live device write.
                if notifier is None:
                    notifier = WebexNotifier(os.getenv('WEBEX_ACCESS_TOKEN'), os.getenv('WEBEX_ROOM_ID'))
                expected = 'APPLY ' + plan.request.hostname
                if read(f'Type {expected} to confirm: ').strip() != expected:
                    write('Cancelled; no configuration change sent.')
                    continue
                evidence = Evidence(evidence_root, simulated=simulated)
                write('Evidence directory: ' + str(evidence.directory))
                request_plan, plan = plan, None  # Do not accidentally reuse a stale request.
                apply(session, request_plan, evidence)
                last = evidence
                write('All three running-config values verified.')
                message = notify(notifier, evidence)
                failed = False
                write(('Simulated notification: ' if simulated else 'WebEx message: ') + message)
            elif command == 'notify':
                if last is None:
                    raise AutomationError('No verified change is available for notification.')
                if last.record['notification_status'] in ('sent', 'simulated'):
                    raise AutomationError('This change already has a recorded notification; no duplicate was sent.')
                if read('Check the room first. Type RETRY to send only the notification: ').strip() != 'RETRY':
                    write('Notification retry cancelled.')
                    continue
                write('Notification reference: ' + notify(notifier, last))
                failed = False
            elif command == 'schema':
                write('Device model: Cisco-IOS-XE-native (' + NATIVE + ')')
                write('Request model: network_automation/yang/palpak-change-request.yang')
                write('\n'.join(str(c) for c in session.server_capabilities))
                if simulated:
                    write('Simulation uses a limited native-model fixture; no real device schema was retrieved.')
                else:
                    evidence = Evidence(evidence_root)
                    schema = session.get_schema(identifier='Cisco-IOS-XE-native', format='yang').data
                    if not isinstance(schema, str) or 'module Cisco-IOS-XE-native' not in schema:
                        raise AutomationError('The device did not return the expected YANG module.')
                    evidence.write('Cisco-IOS-XE-native.yang', schema)
                    write('Device schema saved in ' + str(evidence.directory))
            else:
                write('Unknown command. Type help.')
        except (EOFError, KeyboardInterrupt):
            write('\nSession closed.')
            return 1 if failed else 0
        except AutomationError as error:
            failed = True
            write(str(error))
        except Exception:
            failed = True
            write('Operation failed. Inspect the device/evidence; raw server diagnostics are not displayed.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo', action='store_true', help='simulate the device and WebEx; no network or secrets')
    parser.add_argument('--run-example', action='store_true', help='run a fixed example; requires --demo')
    parser.add_argument('--evidence-dir', type=Path, default=ROOT / 'activity5-evidence')
    args = parser.parse_args(argv)
    if args.run_example and not args.demo:
        parser.error('--run-example is only available with --demo')
    if args.demo:
        # Demo never reads .env or constructs a real network client.
        read = input
        if args.run_example:
            commands = iter(['show', 'change', 'PALPAK-LAB', 'GigabitEthernet', '1',
                             'Activity 5 lab interface', '100', '192.0.2.10/32',
                             'apply', 'APPLY PALPAK-LAB', 'show', 'quit'])
            def read(prompt):
                value = next(commands)
                print(prompt + value)
                return value
        return chatbot(SimulatedDevice(), SimulatedNotifier(), args.evidence_dir, True, read=read)
    load_dotenv(ROOT / '.env')
    try:
        with live_session() as session:
            return chatbot(session, None, args.evidence_dir, False)
    except AutomationError as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
