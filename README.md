`enum_linter.py`:
- Caches all *.xml files into a variable
- Searches every `*.cpp` and `*.h` file in a given list of directories for enums
- Marks documentation as missing if either the enum name doesn't occur in the `*.xml` files, or if one of the members of the enum does not occur
- (this means that this linter is not very context aware, as there are lots of enum naming clashes between classes)
- Furthermore, this linter does not know if enums are public / private / local to a function etc. For these reasons many of the flagged enums aren't ones that need to be documented.

Currently there are some extra conditions to make this linting more accurate:
- only flag enums with more than 1 capital letter (removes lots of short, private enums like `Mode` or `Flags`)
- don't flag enums which include the string `MAX` (there are a lot of enums whose max value isn't documented but IMO this is extremely low priority and rly doesn't matter)
- some subdirectories are ignored as they contain lots of internal classes (which have no documentation page) (e.g. `modules/gdscript`)
