#!/usr/bin/python
import sys, tty, termios

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    key = ""
    sys.stdout.write('Password :: ')
    while True:
        ch = getch()
        if ch == '\r':
            break
        key += ch
        sys.stdout.write('*')
    print
    print key

if __name__ == '__main__':
    main()
