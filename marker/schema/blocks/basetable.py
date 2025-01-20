from typing import List

from marker.schema import BlockTypes
from marker.schema.blocks import Block, BlockOutput
from marker.schema.blocks.tablecell import TableCell


class BaseTable(Block):
    block_type: BlockTypes | None = None
    html: str | None = None

    def format_cells(self, document, child_blocks):
        child_cells: List[TableCell] = [document.get_block(c.id) for c in child_blocks]
        unique_rows = sorted(list(set([c.row_id for c in child_cells])))
        html_repr = "<table><tbody>"
        for row_id in unique_rows:
            row_cells = sorted([c for c in child_cells if c.row_id == row_id], key=lambda x: x.col_id)
            html_repr += "<tr>"
            for cell in row_cells:
                html_repr += cell.assemble_html(document, child_blocks, None)
            html_repr += "</tr>"
        html_repr += "</tbody></table>"
        return html_repr


    def assemble_html(self, document, child_blocks: List[BlockOutput], parent_structure=None):
        # Filter out the table cells, so they don't render twice
        child_ref_blocks = [block for block in child_blocks if block.id.block_type == BlockTypes.Reference]
        template = super().assemble_html(document, child_ref_blocks, parent_structure)

        if self.html:
            # LLM processor
            return template + self.html
        elif len(child_blocks) > 0 and child_blocks[0].id.block_type == BlockTypes.TableCell:
            # Table processor
            return template + self.format_cells(document, child_blocks)
        else:
            # Default text lines and spans
            return f"<p>{template}</p>"
