import logging
import os
from typing import Optional

import lxml.etree

from benjaminhamon_book_distribution_toolkit.documents import document_operations
from benjaminhamon_book_distribution_toolkit.documents.root_element import RootElement
from benjaminhamon_book_distribution_toolkit.epub.epub_xhtml_builder import EpubXhtmlBuilder


logger = logging.getLogger("EpubXhtmlWriter")


class EpubXhtmlWriter:


    def __init__(self) -> None:
        self.pretty_print = True
        self.encoding = "utf-8"


    def write_to_file(self, output_file_path: str, document: lxml.etree._ElementTree, simulate: bool = False) -> None:
        logger.debug("Writing '%s'", output_file_path)

        content_as_string = self._serialize_to_xml(document)

        if not simulate:
            with open(output_file_path + ".tmp", mode = "w", encoding = self.encoding) as output_file:
                output_file.write(content_as_string)
            os.replace(output_file_path + ".tmp", output_file_path)


    def write_as_single_document(self,
            output_file_path: str, document_content: RootElement,
            template_file_path: Optional[str] = None, simulate: bool = False) -> None:

        raise NotImplementedError


    def write_as_many_documents(self,
            output_directory: str, document_content: RootElement,
            template_file_path: Optional[str] = None, simulate: bool = False) -> None:

        section_count = document_content.get_section_count()

        for section_index, section in enumerate(document_content.enumerate_sections()):
            title = section.get_heading().get_title()

            xhtml_builder = EpubXhtmlBuilder(title, template_file_path)
            xhtml_builder.add_content_from_section(section)

            file_name = document_operations.generate_section_file_name(title, section_index, section_count)
            docx_file_path = os.path.join(output_directory, file_name + ".xhtml")

            self.write_to_file(docx_file_path, xhtml_builder.get_xhtml_document(), simulate = simulate)


    def _serialize_to_xml(self, document: lxml.etree._ElementTree) -> str:
        write_options = {
            "encoding": self.encoding,
            "pretty_print": self.pretty_print,
            "xml_declaration": True,
        }

        content_as_string = lxml.etree.tostring(document, **write_options).decode(self.encoding)
        content_as_string = content_as_string.replace("<?xml version='1.0' encoding='UTF-8'?>", "<?xml version='1.0' encoding='utf-8'?>")

        return content_as_string
