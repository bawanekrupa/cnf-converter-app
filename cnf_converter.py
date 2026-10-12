from itertools import combinations


class CNFConverter:
    """
    Chomsky Normal Form Converter

    Supported input examples:

        S -> AB
        A -> aA | ε
        B -> bB | b

    Symbols can also be separated by spaces:

        S -> A B
        A -> a
        B -> b
    """

    EPSILON = "ε"

    def __init__(self, grammar_text):
        self.grammar_text = grammar_text
        self.grammar = {}
        self.variables = set()
        self.terminals = set()
        self.steps = []

        self.original_start = None
        self.start_symbol = None

    # ---------------------------------------------------------
    # BASIC UTILITIES
    # ---------------------------------------------------------

    def clone_grammar(self, grammar):
        return {
            variable: [production[:] for production in productions]
            for variable, productions in grammar.items()
        }

    def format_production(self, symbols):
        if not symbols:
            return self.EPSILON
        return " ".join(symbols)

    def format_grammar(self, grammar):
        lines = []

        for variable, productions in grammar.items():
            formatted = []

            for production in productions:
                formatted.append(self.format_production(production))

            lines.append(
                f"{variable} -> " + " | ".join(formatted)
            )

        return "\n".join(lines)

    def add_step(self, number, title, description, grammar):
        self.steps.append({
            "number": number,
            "title": title,
            "description": description,
            "grammar": self.format_grammar(grammar)
        })

    # ---------------------------------------------------------
    # TOKENIZATION
    # ---------------------------------------------------------

    def tokenize(self, text):
        """
        Convert RHS into symbols.

        If spaces exist:
            A B C -> ["A", "B", "C"]

        Without spaces:
            ABC -> ["A", "B", "C"]
        """

        text = text.strip()

        if text == "" or text == self.EPSILON or text.lower() in {
            "epsilon",
            "eps",
            "null"
        }:
            return []

        if " " in text:
            return text.split()

        return list(text)

    # ---------------------------------------------------------
    # PARSING
    # ---------------------------------------------------------

    def parse_grammar(self):
        self.grammar = {}
        self.variables = set()

        lines = self.grammar_text.strip().splitlines()

        for line_number, line in enumerate(lines, start=1):

            line = line.strip()

            if not line:
                continue

            if "->" not in line:
                raise ValueError(
                    f"Invalid grammar at line {line_number}: "
                    f"Missing '->'."
                )

            left, right = line.split("->", 1)

            left = left.strip()
            right = right.strip()

            if not left:
                raise ValueError(
                    f"Invalid grammar at line {line_number}: "
                    f"Missing left-hand variable."
                )

            self.variables.add(left)

            if left not in self.grammar:
                self.grammar[left] = []

            alternatives = right.split("|")

            for alternative in alternatives:

                symbols = self.tokenize(alternative)

                if symbols not in self.grammar[left]:
                    self.grammar[left].append(symbols)

        if not self.grammar:
            raise ValueError("Grammar is empty.")

        self.original_start = next(iter(self.grammar))
        self.start_symbol = self.original_start

        self.update_terminals()

    # ---------------------------------------------------------
    # TERMINALS
    # ---------------------------------------------------------

    def update_terminals(self):
        self.terminals = set()

        for productions in self.grammar.values():
            for production in productions:
                for symbol in production:
                    if symbol not in self.variables:
                        self.terminals.add(symbol)

    # ---------------------------------------------------------
    # STEP 1
    # ---------------------------------------------------------

    def add_new_start_symbol(self):
        old_start = self.start_symbol

        new_start = "S0"

        while new_start in self.variables:
            new_start += "0"

        new_grammar = {
            variable: [production[:] for production in productions]
            for variable, productions in self.grammar.items()
        }

        new_grammar = {
            new_start: [[old_start]],
            **new_grammar
        }

        self.grammar = new_grammar
        self.variables.add(new_start)
        self.start_symbol = new_start

        self.add_step(
            1,
            "Start Symbol Setup",
            f"New start symbol {new_start} was introduced.",
            self.grammar
        )

    # ---------------------------------------------------------
    # STEP 2 - NULL / EPSILON PRODUCTIONS
    # ---------------------------------------------------------

    def find_nullable_variables(self):
        nullable = set()

        changed = True

        while changed:
            changed = False

            for variable, productions in self.grammar.items():

                for production in productions:

                    if len(production) == 0:
                        if variable not in nullable:
                            nullable.add(variable)
                            changed = True

                    elif all(
                        symbol in nullable
                        for symbol in production
                        if symbol in self.variables
                    ) and all(
                        symbol in nullable
                        for symbol in production
                    ):
                        if variable not in nullable:
                            nullable.add(variable)
                            changed = True

        return nullable

    def remove_epsilon_productions(self):

        nullable = self.find_nullable_variables()

        new_grammar = {
            variable: []
            for variable in self.grammar
        }

        for variable, productions in self.grammar.items():

            for production in productions:

                if len(production) == 0:
                    continue

                nullable_positions = [
                    index
                    for index, symbol in enumerate(production)
                    if symbol in nullable
                ]

                generated = set()

                total = len(nullable_positions)

                for remove_count in range(total + 1):

                    for combination in combinations(
                        nullable_positions,
                        remove_count
                    ):

                        remove_set = set(combination)

                        new_production = [
                            symbol
                            for index, symbol in enumerate(production)
                            if index not in remove_set
                        ]

                        if len(new_production) == 0:
                            if variable == self.start_symbol:
                                generated.add(tuple())
                        else:
                            generated.add(tuple(new_production))

                for production_tuple in generated:
                    production_list = list(production_tuple)

                    if production_list not in new_grammar[variable]:
                        new_grammar[variable].append(production_list)

        self.grammar = new_grammar

        self.add_step(
            2,
            "Remove ε Productions",
            (
                "Nullable variables were identified and "
                "ε-productions were eliminated."
            ),
            self.grammar
        )

    # ---------------------------------------------------------
    # STEP 3 - UNIT PRODUCTIONS
    # ---------------------------------------------------------

    def remove_unit_productions(self):

        new_grammar = {
            variable: []
            for variable in self.grammar
        }

        for variable in self.grammar:

            closure = {variable}
            queue = [variable]

            while queue:

                current = queue.pop(0)

                for production in self.grammar.get(current, []):

                    if (
                        len(production) == 1
                        and production[0] in self.variables
                    ):

                        target = production[0]

                        if target not in closure:
                            closure.add(target)
                            queue.append(target)

            for reachable in closure:

                for production in self.grammar.get(
                    reachable,
                    []
                ):

                    is_unit = (
                        len(production) == 1
                        and production[0] in self.variables
                    )

                    if not is_unit:

                        if production not in new_grammar[variable]:
                            new_grammar[variable].append(
                                production[:]
                            )

        self.grammar = new_grammar

        self.add_step(
            3,
            "Remove Unit Productions",
            (
                "Unit-production chains were removed using "
                "transitive closure."
            ),
            self.grammar
        )

    # ---------------------------------------------------------
    # STEP 4 - TERMINAL REPLACEMENT
    # ---------------------------------------------------------

    def create_terminal_variables(self):

        new_grammar = self.clone_grammar(self.grammar)

        terminal_variables = {}

        used_variables = set(self.variables)

        for productions in self.grammar.values():

            for production in productions:

                if len(production) < 2:
                    continue

                for terminal in production:

                    if terminal in self.variables:
                        continue

                    if terminal not in terminal_variables:

                        base_name = f"T_{terminal}"

                        candidate = base_name
                        counter = 1

                        while candidate in used_variables:

                            candidate = (
                                f"{base_name}_{counter}"
                            )

                            counter += 1

                        terminal_variables[terminal] = candidate
                        used_variables.add(candidate)

        for terminal, variable in terminal_variables.items():

            new_grammar[variable] = [[terminal]]

        for variable, productions in list(
            self.grammar.items()
        ):

            updated = []

            for production in productions:

                if len(production) >= 2:

                    replaced = []

                    for symbol in production:

                        if symbol in terminal_variables:
                            replaced.append(
                                terminal_variables[symbol]
                            )
                        else:
                            replaced.append(symbol)

                    updated.append(replaced)

                else:
                    updated.append(production[:])

            new_grammar[variable] = updated

        self.grammar = new_grammar

        self.variables = set(new_grammar.keys())

        self.update_terminals()

        self.add_step(
            4,
            "Replace Terminals",
            (
                "Terminals appearing inside long productions "
                "were replaced by helper variables."
            ),
            self.grammar
        )

    # ---------------------------------------------------------
    # STEP 5 - BINARY DECOMPOSITION
    # ---------------------------------------------------------

    def binary_decomposition(self):

        new_grammar = {}

        for variable in self.grammar:
            new_grammar[variable] = []

        used_variables = set(self.variables)

        counter = 1

        for variable, productions in self.grammar.items():

            for production in productions:

                if len(production) <= 2:

                    if production not in new_grammar[variable]:
                        new_grammar[variable].append(
                            production[:]
                        )

                    continue

                current_left = variable

                remaining = production[:]

                while len(remaining) > 2:

                    first = remaining[0]
                    second = remaining[1]

                    helper = f"X{counter}"

                    while helper in used_variables:
                        counter += 1
                        helper = f"X{counter}"

                    counter += 1

                    used_variables.add(helper)

                    new_grammar.setdefault(
                        current_left,
                        []
                    )

                    new_grammar[current_left].append(
                        [first, helper]
                    )

                    new_grammar[helper] = []

                    current_left = helper
                    remaining = remaining[1:]

                new_grammar[current_left].append(
                    remaining
                )

        self.grammar = new_grammar

        self.variables = set(new_grammar.keys())

        self.update_terminals()

        self.add_step(
            5,
            "Binary Decomposition",
            (
                "Productions containing more than two symbols "
                "were converted into binary productions."
            ),
            self.grammar
        )

    # ---------------------------------------------------------
    # FINAL VALIDATION
    # ---------------------------------------------------------

    def validate_cnf(self):

        for variable, productions in self.grammar.items():

            for production in productions:

                # S0 -> ε is allowed
                if len(production) == 0:

                    if variable != self.start_symbol:
                        return False

                    continue

                # A -> a
                if len(production) == 1:

                    if production[0] in self.variables:
                        return False

                # A -> BC
                elif len(production) == 2:

                    if (
                        production[0] not in self.variables
                        or
                        production[1] not in self.variables
                    ):
                        return False

                else:
                    return False

        return True

    # ---------------------------------------------------------
    # MAIN CONVERSION
    # ---------------------------------------------------------

    def convert(self):

        self.parse_grammar()

        # Step 1
        self.add_new_start_symbol()

        # Step 2
        self.remove_epsilon_productions()

        # Step 3
        self.remove_unit_productions()

        # Step 4
        self.create_terminal_variables()

        # Step 5
        self.binary_decomposition()

        valid = self.validate_cnf()

        if not valid:
            raise ValueError(
                "The generated grammar could not be validated as CNF."
            )

        final_text = self.format_grammar(self.grammar)

        return {
            "final": final_text,
            "steps": self.steps,
            "grammar": self.grammar
        }