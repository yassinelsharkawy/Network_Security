#!/usr/bin/env python3
import os
import subprocess
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI_EXEC = os.path.join(BASE_DIR, 'networksecurity')
results = []

def record(test_name, success, message=''):
    status = 'PASS' if success else 'FAIL'
    color = '\x1b[92m' if success else '\x1b[91m'
    reset = '\x1b[0m'
    print(f'[{color}{status}{reset}] {test_name}: {message}')
    results.append((test_name, success, message))

def run_cmd(args, check_code=True, timeout=10):
    try:
        proc = subprocess.run([sys.executable, 'networksecurity.py'] + args, cwd=BASE_DIR, capture_output=True, text=True, timeout=timeout)
        return (proc.returncode, proc.stdout, proc.stderr)
    except subprocess.TimeoutExpired:
        return (-1, '', 'Timeout expired')
    except Exception as e:
        return (-2, '', str(e))
print('\n' + '=' * 65)
print('NetworkSecurity Validation Suite')
print('=' * 65 + '\n')
code, out, err = run_cmd(['--version'])
record('Global --version', code == 0 and 'NetworkSecurity' in out, out.strip())
code, out, err = run_cmd(['--help'])
record('Global --help', code == 0 and 'USAGE' in out, 'Help banner rendered')
code, out, err = run_cmd(['--list'])
record('Global --list', code == 0 and 'Interface & MAC' in out, 'Categorized tool list displayed')
code, out, err = run_cmd(['--check-deps'])
record('Global --check-deps', code == 0 and 'Checking NetworkSecurity Dependencies' in out, 'Dependencies audited')
all_tools = [('mac-changer', '--mac-changer'), ('scan', '--scan'), ('arp-spoof', '--arp-spoof'), ('arp-detector', '--arp-detector'), ('sniff', '--sniff'), ('dns-spoof', '--dns-spoof'), ('net-cut', '--net-cut'), ('code-injector', '--code-injector'), ('replace-downloads', '--replace-downloads'), ('crawler', '--crawler'), ('spider', '--spider'), ('extract-forms', '--extract-forms'), ('vuln-scanner', '--vuln-scanner'), ('brute-login', '--brute-login'), ('exec-cmd', '--exec-cmd'), ('wifi-passwords', '--wifi-passwords'), ('download', '--download'), ('download-exec', '--download-exec'), ('keylogger', '--keylogger'), ('listener', '--listener'), ('backdoor', '--backdoor')]
print('\nValidating Tool Help Parsers (Subcommands and Flags)...')
for tool, flag in all_tools:
    code, out, err = run_cmd([flag, '--help'])
    flag_ok = code == 0 and 'usage:' in out.lower()
    code2, out2, err2 = run_cmd([tool, '--help'])
    sub_ok = code2 == 0 and 'usage:' in out2.lower()
    record(f'Tool {tool} Help', flag_ok and sub_ok, f"Flag: {('OK' if flag_ok else 'ERR')}, Subcmd: {('OK' if sub_ok else 'ERR')}")
print('\nValidating Functional Runtime Execution on Safe Modules...')
code, out, err = run_cmd(['--mac-changer', '-i', 'lo', '--show'])
record('Module mac-changer (show MAC on lo)', code == 0 and 'Current MAC address' in out, out.strip())
code, out, err = run_cmd(['--exec-cmd', '-c', "echo 'TEST_OK'"])
record('Module exec-cmd (local echo)', code == 0 and 'TEST_OK' in out, 'Output captured successfully')
import tempfile
with tempfile.NamedTemporaryFile('w+', delete=False) as tf:
    tf.write('admin\ntest\n')
    temp_wordlist = tf.name
try:
    code, out, err = run_cmd(['--crawler', '-u', 'http://127.0.0.1:9999', '-w', temp_wordlist], timeout=5)
    record('Module crawler (offline target)', code == 0 and 'Crawl complete' in out, 'Graceful network failure handling')
    code, out, err = run_cmd(['--brute-login', '-u', 'http://127.0.0.1:9999', '-w', temp_wordlist], timeout=5)
    record('Module brute-login (offline target)', code == 1 and 'No valid password found' in out, 'Exits properly when not found')
finally:
    if os.path.exists(temp_wordlist):
        os.remove(temp_wordlist)
code, out, err = run_cmd(['--wifi-passwords', '--dry-run'])
record('Module wifi-passwords (dry-run)', code == 0, 'Executed platform extraction')
passed = sum((1 for _, ok, _ in results if ok))
total = len(results)
print('\n' + '=' * 65)
print(f'Validation Summary: {passed}/{total} tests PASSED')
print('=' * 65 + '\n')
if passed != total:
    sys.exit(1)
