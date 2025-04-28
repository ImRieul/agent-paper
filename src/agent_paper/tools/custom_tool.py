from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

import pandas as pd


class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""

    argument: str = Field(..., description="Description of the argument.")


class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."


class FilePathModel(BaseModel):
    file_path: str = Field(..., description="The path to the file to read")


class DataReadToDataFrameTool(BaseTool):
    name: str = "Data Reader Tool"
    description: str = "Read data from a file(csv, excel, json, etc.) and return a pandas DataFrame"
    args_schema: Type[BaseModel] = FilePathModel

    def _run(self, file_path: str) -> str:
        if file_path.endswith(".csv"):
            return pd.read_csv(file_path)
        elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
            return pd.read_excel(file_path)
        elif file_path.endswith(".json"):
            return pd.read_json(file_path)
        elif file_path.endswith(".sav"):
            return pd.read_spss(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
