import re
from collections import defaultdict

class LL1Parser:
    def __init__(self, grammar_file):
        self.grammar = {}
        self.first = defaultdict(set)
        self.follow = defaultdict(set)
        self.table = {}
        self.start_symbol = ""
        self.load_grammar(grammar_file)
        self.build_first()
        self.build_follow()
        if not self.build_parsing_table():
            print("Error: The grammar is not LL(1) and cannot be parsed by this parser.")
            exit()

    def load_grammar(self, grammar_file):
        with open(grammar_file, "r") as file:
            for line in file:
                line = line.strip()
                if line:
                    lhs, rhs = line.split("->")
                    lhs = lhs.strip()
                    rhs = [term.strip().split() for term in rhs.split("|")]
                    if not self.start_symbol:
                        self.start_symbol = lhs
                    self.grammar[lhs] = rhs

    def build_first(self):
        def first_of(symbol, visited=set()):
            if symbol not in self.grammar:  # Terminal
                return {symbol}
            if symbol in visited:  # Avoid recursion loop
                return self.first[symbol]
            if self.first[symbol]:  # Already computed
                return self.first[symbol]

            visited.add(symbol)
            first_set = set()
            for production in self.grammar[symbol]:
                for sym in production:
                    first_sym = first_of(sym, visited)
                    first_set.update(first_sym - {'ε'})
                    if 'ε' not in first_sym:
                        break
                else:
                    first_set.add('ε')
            self.first[symbol] = first_set
            visited.remove(symbol)
            return first_set

        for non_terminal in self.grammar:
            first_of(non_terminal)

    def build_follow(self):
        self.follow[self.start_symbol].add('$')  # Add end-of-input marker to start symbol's follow set

        def follow_of(non_terminal):
            for lhs, productions in self.grammar.items():
                for production in productions:
                    for i, symbol in enumerate(production):
                        if symbol == non_terminal:
                            follow_symbols = production[i + 1:]
                            if follow_symbols:
                                first_of_follow = set()
                                for sym in follow_symbols:
                                    first_of_follow.update(self.first[sym] - {'ε'})
                                    if 'ε' not in self.first[sym]:
                                        break
                                else:
                                    self.follow[symbol].update(self.follow[lhs])
                                self.follow[symbol].update(first_of_follow)
                            else:
                                self.follow[symbol].update(self.follow[lhs])

        for _ in range(len(self.grammar)):
            for non_terminal in self.grammar:
                follow_of(non_terminal)

    def build_parsing_table(self):
        is_ll1 = True
        for non_terminal, productions in self.grammar.items():
            for production in productions:
                first_set = set()
                for symbol in production:
                    first_set.update(self.first[symbol] - {'ε'})
                    if 'ε' not in self.first[symbol]:
                        break
                else:
                    first_set.add('ε')

                for terminal in first_set:
                    if terminal != 'ε':
                        if (non_terminal, terminal) in self.table:
                            print(f"Conflict: Multiple entries for [{non_terminal}, {terminal}] in parsing table.")
                            is_ll1 = False
                        self.table[(non_terminal, terminal)] = production

                if 'ε' in first_set:
                    for terminal in self.follow[non_terminal]:
                        if (non_terminal, terminal) in self.table:
                            print(f"Conflict: Multiple entries for [{non_terminal}, {terminal}] in parsing table.")
                            is_ll1 = False
                        self.table[(non_terminal, terminal)] = production

        return is_ll1  # Return False if any conflicts were found

    def parse(self, input_string):
        stack = [self.start_symbol, '$']
        input_tokens = list(input_string) + ['$']
        index = 0
        parse_tree = []

        while stack:
            top = stack.pop()
            current_token = input_tokens[index]

            if top in self.grammar:  # Non-terminal
                if (top, current_token) in self.table:
                    production = self.table[(top, current_token)]
                    parse_tree.append((top, production))
                    for symbol in reversed(production):
                        if symbol != 'ε':  # Skip epsilon productions
                            stack.append(symbol)
                else:
                    return f"Error: Parsing failed at token '{current_token}'."
            elif top == current_token:  # Terminal matches input
                index += 1
            else:
                return f"Error: Unexpected token '{current_token}'."

        if index == len(input_tokens) - 1:
            return parse_tree
        else:
            return "Error: Incomplete parsing."

# Utility to print parse tree
def print_parse_tree(parse_tree):
    print("Visual of the Resulting Parse Tree:")
    for parent, production in parse_tree:
        print(f"{parent} -> {' '.join(production)}")

# Main function to handle input and output
def main():
    print("***THIS IS A SIMPLE LL(1) PARSER***")
    grammar_file = "C:\\Users\\user\\Desktop\\SEM 5\\Comptech\\ASSIGNMENT\\grammar.txt"
    input_string = input("Please, input the string         : ")

    parser = LL1Parser(grammar_file)
    result = parser.parse(input_string)

    if isinstance(result, str):
        print(result)  # Display error message
    else:
        print_parse_tree(result)  # Display parse tree

if __name__ == "__main__":
    main()
