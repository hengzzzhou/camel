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
import re
from typing import List, Optional

from camel.toolkits import FunctionTool
from camel.toolkits.base import BaseToolkit


class GoogleScholarToolkit(BaseToolkit):
    r"""A toolkit for retrieving information about authors and their
    publications from Google Scholar.

    Attributes:
        author_identifier (Union[str, None]): The author's Google Scholar URL
            or name of the author to search for.
        is_author_name (bool): Flag to indicate if the identifier is a name.
            (default: :obj:`False`)
        scholarly (module): The scholarly module for querying Google Scholar.
    """

    def __init__(
        self, author_identifier: str, is_author_name: bool = False
    ) -> None:
        r"""Initializes the GoogleScholarToolkit with the author's identifier.

        Args:
            author_identifier (str): The author's Google Scholar URL or name
                of the author to search for.
            is_author_name (bool): Flag to indicate if the identifier is a
                name. (default: :obj:`False`)
        """
        from scholarly import scholarly

        self.scholarly = scholarly
        self.author_identifier = author_identifier
        self.is_author_name = is_author_name

    def _extract_author_id(self) -> Optional[str]:
        r"""Extracts the author ID from a Google Scholar URL if provided.

        Returns:
            Optional[str]: The extracted author ID, or None if not found.
        """
        match = re.search(r'user=([A-Za-z0-9-]+)', self.author_identifier)
        return match.group(1) if match else None

    def get_author_detailed_info(
        self,
    ) -> dict:
        r"""Retrieves detailed information about the author.

        Returns:
            dict: A dictionary containing detailed information about the
                author.
        """
        if self.is_author_name:
            search_query = self.scholarly.search_author(self.author_identifier)
            # Retrieve the first result from the iterator
            first_author_result = next(search_query)
        else:
            author_id = self._extract_author_id()
            first_author_result = self.scholarly.search_author_id(id=author_id)

        author = self.scholarly.fill(first_author_result)
        return author

    def get_author_publications(
        self, author: Optional[dict] = None
    ) -> List[str]:
        r"""Retrieves the titles of the author's publications.

        Args:
            author (Optional[dict]): The author's detailed information.

        Returns:
            List[str]: A list of publication titles authored by the author.
        """
        if author is None:
            author = self.get_author_detailed_info()
        publication_titles = [
            pub['bib']['title'] for pub in author['publications']
        ]
        return publication_titles

    def get_publication_by_title(
        self, publication_title: str, author: Optional[dict] = None
    ) -> Optional[dict]:
        r"""Retrieves detailed information about a specific publication by its
        title. Note that this method cannot retrieve the full content of the
        paper.

        Args:
            publication_title (str): The title of the publication to search
                for.
            author (Optional[dict]): The author's detailed information.

        Returns:
            Optional[dict]: A dictionary containing detailed information about
                the publication if found; otherwise, `None`.
        """
        if author is None:
            author = self.get_author_detailed_info()
        publications = author['publications']
        for publication in publications:
            if publication['bib']['title'] == publication_title:
                return self.scholarly.fill(publication)
        return None  # Return None if not found

    def get_full_paper_content_by_link(self, pdf_url: str) -> Optional[str]:
        r"""Retrieves the full paper content from a given PDF URL using the
        arxiv2text tool.

        Args:
            pdf_url (str): The URL of the PDF file.

        Returns:
            Optional[str]: The full text extracted from the PDF, or `None` if
                an error occurs.
        """
        from arxiv2text import arxiv_to_text

        try:
            return arxiv_to_text(pdf_url)
        except Exception:
            return None  # Return None in case of any error

    def get_tools(self) -> List[FunctionTool]:
        r"""Returns a list of FunctionTool objects representing the
        functions in the toolkit.

        Returns:
            List[FunctionTool]: A list of FunctionTool objects
                representing the functions in the toolkit.
        """
        return [
            FunctionTool(self.get_author_detailed_info),
            FunctionTool(self.get_author_publications),
            FunctionTool(self.get_publication_by_title),
            FunctionTool(self.get_full_paper_content_by_link),
        ]
