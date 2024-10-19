import cmd
import subprocess
import os
import pty
from prompt_toolkit import prompt
from pygments import highlight
from pygments.lexers import BashLexer
from pygments.formatters import TerminalFormatter

from dotenv import load_dotenv, find_dotenv
#from langchain.chat_models import ChatOpenAI
#from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser

_ = load_dotenv(find_dotenv()) # read local .env file

"""
BASE TODO
- [x] base shell terminal
- [x] support cd command
- [x] support exit command
- [x] support syntax highlighting
- [x] launching external command-line programs
- [x] real time acquisition of operational output

SENIOR TODO
- [ ] explain the results of command execution
- [ ] use `TAB` to adopt command auto completion
- [ ] use `:` to convert natural language input to shell commands
- [ ] use `?` to explain how to use a certain command
- [x] use `>` to chat with llm
- [ ] use `<your task>` or ``` <your tasks> ``` to assign tasks
- [ ] support stream flush output
"""

class Model:
    llm_model = "gpt-3.5-turbo"
    chat = ChatOpenAI(temperature=0.0, model=llm_model)

    def __init__(self):
        pass

    def small_talk(self, user_message: str) -> str:
        template_string = """ You are a ShellGPT assistant, \
            primarily providing users with advice or help regarding terminal commands. \
            Additionally, you are also happy to engage in conversations with users.
            
            Now, the user talk that:

            ```{text}```
        """

        prompt_template = ChatPromptTemplate.from_template(template_string)
        full_message = prompt_template.format_messages(text=user_message)
        response = self.chat.invoke(full_message)

        return response.content



class Shell(cmd.Cmd):
    intro = 'Welcome to ShellGPT. Type help or ? to list commands.'
    prompt = '(ShellGPT) % '

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
            if line.startswith(">"):
                response = Model().small_talk(line)
                print(response)
            elif line.startswith(("vim", "zellij", "lazygit", "nano", "python", "sqlite3")):
                os.system(line)
            else:
                # 创建伪终端
                master_fd, slave_fd = pty.openpty()
                # 使用 subprocess.Popen 执行命令
                process = subprocess.Popen(line, shell=True, stdout=slave_fd, stderr=slave_fd, close_fds=True)
                # 关闭 slave_fd，因为它已经被子进程使用
                os.close(slave_fd)
                # 实时读取输出
                while True:
                    try:
                        output = os.read(master_fd, 1024).decode()
                        if not output:
                            break
                        # 高亮显示输出
                        print(highlight(output, BashLexer(), TerminalFormatter()), end='')
                    except OSError:
                        break
                # 关闭 master_fd
                os.close(master_fd)
                # 等待子进程结束
                process.wait()
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
    Shell().cmdloop()