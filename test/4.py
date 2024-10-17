import cmd
import subprocess
import os
from prompt_toolkit import prompt
from pygments import highlight
from pygments.lexers import BashLexer
from pygments.formatters import TerminalFormatter

"""
BASE TODO
- [x] base shell terminal
- [x] support cd command
- [x] support exit command
- [x] support syntax highlighting
- [x] launching external command-line programs
- [ ] real time acquisition of operational output

SENIOR TODO
- [ ] explain the results of command execution
- [ ] use `TAB` to adopt command auto completion
- [ ] use `:` to convert natural language input to shell commands
- [ ] use `?` to explain how to use a certain command
- [ ] use `>` to chat with llm
- [ ] use `<your task>` or ``` <your tasks> ``` to assign tasks
"""

class FullShell(cmd.Cmd):
    intro = 'Welcome to ShellGPT. Type help or ? to list commands.'
    prompt = '(ShellGPT) % '

    def do_exit(self, _):
        """Exit the shell."""
        print("Exiting the shell. Goodbye!")
        return True

    def do_cd(self, path):
        """Change the current directory."""
        try:
            os.chdir(path)
            print(f"Changed directory to {os.getcwd()}")
        except FileNotFoundError:
            print(f"No such directory: {path}")
        except Exception as e:
            print(f"Error: {e}")

    def default(self, line):
        """Execute the entered shell command."""
        try:
            # 检查是否是交互式命令
            #os.system(line)
            if line.startswith(("vim", "zellij", "lazygit", "nano", "python", "sqlite3")):
                os.system(line)
            else:
                # 使用 Popen 执行命令并捕获输出
                process = subprocess.Popen(line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()

                # 高亮输出
                if stdout:
                    print(highlight(stdout, BashLexer(), TerminalFormatter()))
                if stderr:
                    print(highlight(stderr, BashLexer(), TerminalFormatter()))
        except Exception as e:
            print(f"An error occurred: {e}")

    def cmdloop(self):
        """Override cmdloop to use prompt_toolkit for syntax highlighting."""
        while True:
            try:
                line = prompt(self.prompt)
                # 检查用户输入的命令是否是退出指令
                if line.strip().lower() in ["exit", "quit"]:
                    print("Exiting the shell. Goodbye!")
                    break
                self.onecmd(line)
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt")
            except EOFError:
                print("EOF received. Exiting the shell.")
                break

if __name__ == '__main__':
    FullShell().cmdloop()