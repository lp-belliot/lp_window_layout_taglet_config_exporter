import json

import tinycss2
from css_parser import CssRule
from tinycss2.ast import CurlyBracketsBlock, HashToken, IdentToken

with open("custom-window.css", "r") as f:
    css = tinycss2.parse_component_value_list(f.read())

rules = []
working_list = []
for token in css:
    if type(token) is CurlyBracketsBlock:
        working_list.append(token)
        rules.append(working_list)
        working_list = []
    else:
        working_list.append(token)

taglet_values = [CssRule(rule).generate_value_objects() for rule in rules]
print("\n")
export = [
    {
        "id": "layouts",
        "value": [x for arr in taglet_values for x in arr]
    }
]
with open("export.json", "w") as f:
    f.write(json.dumps(export))