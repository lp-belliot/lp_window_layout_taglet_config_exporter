import copy

import tinycss2
from tinycss2.ast import (Comment, CurlyBracketsBlock, HashToken, IdentToken,
                          LiteralToken, WhitespaceToken, FunctionBlock)


class BadCss(Exception):
    pass

class CssRule:
    def __init__(self, rule):
        self.rule = self._clean_comments(rule)
        print(self.rule)
        self.rule = self._remove_whitespace_nodes(self.rule)
        self.rule_types = self._determine_rule_type(self.rule)
        self.typeless_rule = self._remove_type_nodes(self.rule)
        if type(self.typeless_rule[0]) is not HashToken or self.typeless_rule[0].value != "lpChat":
            print("Bad Rule: ", self.typeless_rule)
            raise BadCss("First element in heirarchy should be the '#lpChat' selector.")
        self.selector_string = self._generate_selector_string(self.typeless_rule)
        self.curly_brackets_node = self._get_curly_brackets_block(self.typeless_rule)
        self.css_properties = self._get_css_properties_string(self.curly_brackets_node)

    def _clean_comments(self, rule):
        remove_nodes = []
        for node in rule:
            if type(node) is Comment:
                remove_nodes.append(node)
        for node in remove_nodes:
            rule.remove(node)
        return rule


    def _remove_whitespace_nodes(self, rule):
        remove_nodes = []
        for node in rule:
            if type(node) is WhitespaceToken:
                remove_nodes.append(node)
            else:
                break
        for node in reversed(rule):
            if type(node) is WhitespaceToken:
                remove_nodes.append(node)
            else:
                break
        for node in remove_nodes:
            rule.remove(node)
        return rule
    
    def _set_rule_type(self, rule_types, new_value):
        if new_value not in rule_types:
            rule_types.append(new_value)
        return rule_types
    
    def _determine_rule_type(self, rule):
        rule_types = []
        for token_index in range(len(rule)):
            token = rule[token_index]
            if type(token) is IdentToken:
                if "mobile" in token.value:
                    rule_types = self._set_rule_type(rule_types, "mobile")
                elif "desktop" in token.value:
                    rule_types = self._set_rule_type(rule_types, "desktop")
        if len(rule_types) == 0:
            rule_types = ["mobile", "desktop"]
        return rule_types
    
    def _remove_type_nodes(self, rule):
        remove_nodes = []
        for token_index in range(len(rule)):
            token = rule[token_index]
            if type(token) is IdentToken:
                if "mobile" in token.value or "desktop" in token.value:
                    remove_nodes.append(rule[token_index - 1])
                    remove_nodes.append(token)
                    remove_nodes.append(rule[token_index + 1])
        for node in remove_nodes:
            rule.remove(node)
        return rule

    def _generate_selector_string(self, rule):
        selector_string = ""
        for node in rule:
            if type(node) is HashToken and node.value == "lpChat":
                selector_string += "$lpWindowElementId"
            elif type(node) is not CurlyBracketsBlock:
                selector_string += node.value
        return selector_string

    def _get_curly_brackets_block(self, rule):
        for node in rule:
            if type(node) is CurlyBracketsBlock:
                return node
    
    def _get_css_properties_string(self, curly_brackets):
        print("DEBUG: Curly Brackets Is: ", curly_brackets.content)
        trimmed_content = self._remove_whitespace_nodes(curly_brackets.content)
        css_properties = ""
        for content_index in range(len(trimmed_content)):
            node = trimmed_content[content_index]
            if type(node) is WhitespaceToken:
                css_properties += " "
            else:
                css_properties += node.serialize()
        return css_properties

    def generate_value_objects(self):
        ''' Will take the state of the self.rule attribute and create an array of 
        value objects to add to the base taglet config object '''
                
        base_object = {
            "selector": "",
            "outcomes": {}
        }

        values = []
        for rule_type in self.rule_types:
            temp_value = copy.deepcopy(base_object)
            temp_value["selector"] = self.selector_string
            temp_value["outcomes"][rule_type] = [{
                "type": "style",
                "value": self.css_properties
            }]
            values.append(temp_value)
        return values
