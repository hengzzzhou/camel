# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
from typing import List, Literal, Optional

from camel.interpreters import InternalPythonInterpreter
from camel.toolkits import FunctionTool
from camel.toolkits.base import BaseToolkit


class CodeExecutionToolkit(BaseToolkit):
    r"""A tookit for code execution.

    Args:
        sandbox (str): the environment type used to execute code.
        verbose (bool): whether to print the output of the code execution.
        unsafe_mode (bool):  If `True`, the interpreter runs the code
            by `eval()` without any security check. (default: :obj:`False`)
        import_white_list (List[str]): a list of allowed imports.
    """

    def __init__(
        self,
        sandbox: Literal[
            "internal_python", "jupyter", "docker"
        ] = "internal_python",
        verbose: bool = False,
        unsafe_mode: bool = False,
        import_white_list: Optional[List[str]] = None,
    ) -> None:
        # TODO: Add support for docker and jupyter.
        self.verbose = verbose
        self.unsafe_mode = unsafe_mode
        self.import_white_list = import_white_list or list()
        if sandbox == "internal_python":
            self.interpreter = InternalPythonInterpreter(
                unsafe_mode=self.unsafe_mode,
                import_white_list=self.import_white_list,
            )
        else:
            raise RuntimeError(
                f"The sandbox type `{sandbox}` is not supported."
            )

    def execute_code(self, code: str) -> str:
        r"""Execute a given code snippet.

        Args:
            code (str): The input code to the Code Interpreter tool call.

        Returns:
            str: The text output from the Code Interpreter tool call.
        """
        output = self.interpreter.run(code, "python")
        # ruff: noqa: E501
        content = f"Executed the code below:\n```py\n{code}\n```\n> Executed Results:\n{output}"
        if self.verbose:
            print(content)
        return content

    def get_tools(self) -> List[FunctionTool]:
        r"""Returns a list of FunctionTool objects representing the
        functions in the toolkit.

        Returns:
            List[FunctionTool]: A list of FunctionTool objects
                representing the functions in the toolkit.
        """
        return [FunctionTool(self.execute_code)]
