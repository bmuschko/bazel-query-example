# Bazel Query Example

A multi-module Python project built with **Bazel 9.1.0** that demonstrates how to use the `query`, `cquery`, and `aquery` commands to inspect the dependency graph, configured dependency graph, and action graph.

All examples run automatically in a [GitHub Actions workflow](.github/workflows/bazel-queries.yml).

## Project Structure

```
├── MODULE.bazel             # Bzlmod config: rules_python 1.9.0 + pip deps
├── requirements_lock.txt    # External deps: pyyaml, requests
├── utils/
│   ├── math_utils.py        # py_library - add, multiply, factorial
│   └── string_utils.py      # py_library - capitalize_words, reverse_string, count_vowels
├── data/
│   ├── processor.py         # py_library - depends on math_utils + pyyaml
│   └── validator.py         # py_library - depends on string_utils + requests
├── app/
│   └── main.py              # py_binary - depends on processor, validator, config
├── config/
│   └── settings.yaml        # filegroup - data dependency
└── tests/
    ├── test_processor.py    # py_test
    └── test_validator.py    # py_test
```

## Dependency Graph

```
//app:main
├── //data:processor
│   ├── //utils:math_utils
│   │   └── //utils:utils_pkg
│   ├── //data:data_pkg
│   └── @pip//pyyaml
├── //data:validator
│   ├── //utils:string_utils
│   │   └── //utils:utils_pkg
│   ├── //data:data_pkg
│   └── @pip//requests
└── //config:settings
```

## The Three Query Commands

Bazel provides three query commands, each inspecting a different level of the build graph:

| | **`query`** | **`cquery`** | **`aquery`** |
|---|---|---|---|
| **Graph** | Dependency graph | Configured dependency graph | Action graph |
| **Phase** | Loading | Analysis | Analysis |
| **Nodes** | Targets | Configured targets (target + config) | Actions (subprocesses) |
| **Edges** | Dependencies (`deps`, `srcs`, `data`) | Configured dependencies | Providers (files) |
| **Resolves `select()`?** | No | Yes | Yes |
| **When to use** | Explore project structure, find targets, trace dependency relationships | See what actually gets built for a given platform/config | Debug build actions, inspect compiler flags, find declared inputs/outputs |

## `bazel query` - Dependency Graph

Operates during the **loading phase**. Inspects targets and their dependency relationships before any build configuration is applied. Does not resolve `select()` statements or toolchains.

### Use Cases

- **Target discovery** - find all targets of a specific kind
- **Dependency analysis** - trace transitive and direct dependencies
- **Reverse dependencies** - find what depends on a given target
- **Dependency paths** - understand why target A depends on target B
- **Set operations** - combine queries with `intersect`, `except`, `union`
- **Graph visualization** - output DOT format for graphviz

### Examples

**Find all `py_binary` targets:**

```bash
$ bazel query 'kind(py_binary, //...)'
```

```
//app:main
```

**Find all `py_test` targets:**

```bash
$ bazel query 'kind(py_test, //...)'
```

```
//tests:test_processor
//tests:test_validator
```

**List all transitive dependencies of `//app:main`:**

```bash
$ bazel query 'deps(//app:main)'
```

```
//app:main
//app:main.py
//config:settings
//config:settings.yaml
//data:__init__.py
//data:data_pkg
//data:processor
//data:processor.py
//data:validator
//data:validator.py
//utils:__init__.py
//utils:math_utils
//utils:math_utils.py
//utils:string_utils
//utils:string_utils.py
//utils:utils_pkg
@bazel_tools//src/conditions:windows
...
```

**Find which targets depend on `//utils:math_utils` (reverse deps):**

```bash
$ bazel query 'rdeps(//..., //utils:math_utils)'
```

```
//app:main
//data:processor
//tests:test_processor
//utils:math_utils
```

**Find the dependency path from `//app:main` to `//utils:math_utils`:**

```bash
$ bazel query 'somepath(//app:main, //utils:math_utils)'
```

```
//app:main
//data:processor
//utils:math_utils
```

**Set operations - find deps shared by both test targets:**

```bash
$ bazel query 'deps(//tests:test_processor) intersect deps(//tests:test_validator)'
```

This returns all targets that both tests transitively depend on (e.g. `//data:data_pkg`, `//utils:utils_pkg`).

**Output dependency graph as DOT format (for graphviz):**

```bash
$ bazel query 'deps(//data:processor)' --notool_deps --noimplicit_deps --output graph
```

```dot
digraph mygraph {
  node [shape=box];
  "//data:processor"
  "//data:processor" -> "//data:data_pkg"
  "//data:processor" -> "//utils:math_utils"
  "//data:processor" -> "@pip//pyyaml:pkg"
  "//data:processor" -> "//data:processor.py"
  "//utils:math_utils"
  "//utils:math_utils" -> "//utils:utils_pkg"
  "//utils:math_utils" -> "//utils:math_utils.py"
  "//data:data_pkg"
  "//data:data_pkg" -> "//data:__init__.py"
  ...
}
```

Render with: `xdot <(bazel query 'deps(//data:processor)' --notool_deps --noimplicit_deps --output graph)`

## `bazel cquery` - Configured Dependency Graph

Operates during the **analysis phase**. Like `query`, but evaluates build configuration first. This means `select()` statements are resolved, toolchains are bound, and each target label includes a **configuration hash** (e.g. `(91e2498)`).

Use `cquery` when you need to see what **actually gets built** for a given platform and set of build flags.

### Use Cases

- **Configured target discovery** - find targets with their resolved configurations
- **Configuration inspection** - see which config hash applies to each target
- **Resolved dependencies** - deps after `select()` evaluation
- **Output format control** - `label_kind`, `starlark` for custom extraction
- **Filtering** - regex-based filtering on target labels

### Examples

**Find all binary targets (note the config hash in output):**

```bash
$ bazel cquery 'kind(.*_binary, //...)'
```

```
//app:main (91e2498)
```

**Show direct deps with label and rule kind:**

```bash
$ bazel cquery 'deps(//app:main, 1)' --output=label_kind
```

```
py_binary rule //app:main (91e2498)
py_library rule //data:processor (91e2498)
py_library rule //data:validator (91e2498)
filegroup rule //config:settings (91e2498)
source file //app:main.py (null)
cc_toolchain rule @@rules_cc++cc_configure_extension+local_config_cc//:cc-compiler-k8 (91e2498)
...
```

Notice how each target has a configuration hash. Source files show `(null)` because they have no configuration.

**Use Starlark output to extract target labels:**

```bash
$ bazel cquery 'deps(//app:main)' --output=starlark --starlark:expr="str(target.label)"
```

```
@@//app:main
@@//data:processor
@@//data:validator
@@//utils:math_utils
@@//utils:string_utils
...
```

**Use Starlark output to show files produced by each target:**

```bash
$ bazel cquery 'kind(rule, deps(//app:main))' \
  --output=starlark \
  --starlark:expr="'%s -> %s' % (target.label, [f.path for f in target.files.to_list()])"
```

**Filter deps by package:**

```bash
$ bazel cquery 'filter("//data", deps(//app:main))'
```

## `bazel aquery` - Action Graph

Operates during the **analysis phase**, one level deeper than `cquery`. Instead of targets and dependencies, `aquery` shows the actual build **actions** -- subprocesses that Bazel will spawn (compilers, precompilers, file writers, etc.) with their full command lines, inputs, and outputs.

**Key insight**: The dependency graph and the action graph are **NOT one-to-one**. A single target can produce multiple actions, and actions operate on files (artifacts), not on targets.

### Use Cases

- **Action inspection** - see what subprocesses a build will spawn
- **Mnemonic filtering** - find specific action types (e.g. `PyCompile`, `FileWrite`)
- **Input/output analysis** - see declared inputs and outputs of each action
- **Command line inspection** - see the exact flags passed to tools
- **Machine-readable output** - `textproto`, `jsonproto` for tooling

### Examples

**Show all actions for `//data:processor`:**

```bash
$ bazel aquery '//data:processor'
```

```
action 'Python precompiling data/processor.py into data/__pycache__/processor.cpython-311.pyc'
  Mnemonic: PyCompile
  Target: //data:processor
  Configuration: k8-fastbuild
  Execution platform: @@platforms//host:host
  ActionKey: efe377033942e52fa63d52c7d09576787c2c7622906e45ace0044fae3b074071
  Inputs: [bazel-out/k8-opt-exec/bin/external/rules_python+/python/private/python3, ..., data/processor.py]
  Outputs: [bazel-out/k8-fastbuild/bin/data/__pycache__/processor.cpython-311.pyc]
  Environment: [PYTHONHASHSEED=0, PYTHONNOUSERSITE=1, PYTHONSAFEPATH=1]
  Command Line: (exec .../python3 \
    .../precompiler_.py \
    --invalidation_mode checked_hash \
    --src data/processor.py \
    --pyc bazel-out/k8-fastbuild/bin/data/__pycache__/processor.cpython-311.pyc \
    --python_version 3.11)
```

**List all unique action mnemonics for `//app:main`:**

```bash
$ bazel aquery '//app:main' 2>/dev/null | grep "Mnemonic:" | sort -u
```

```
  Mnemonic: FileWrite
  Mnemonic: PyCompile
  Mnemonic: PyWriteBuildData
  Mnemonic: PythonZipper
  Mnemonic: RepoMappingManifest
  Mnemonic: RunfilesTree
  Mnemonic: SourceSymlinkManifest
  Mnemonic: SymlinkTree
  Mnemonic: TemplateExpand
```

**Filter actions by mnemonic:**

```bash
$ bazel aquery 'mnemonic("SourceSymlinkManifest", //app:main)'
```

**Show action graph as JSON (machine-readable):**

```bash
$ bazel aquery '//data:processor' --output=jsonproto
```

**Extract mnemonics and output IDs with `jq`:**

```bash
$ bazel aquery '//app:main' --output=jsonproto | jq -r '.actions[] | "\(.mnemonic) -> outputIds: \(.outputIds)"'
```

## Documentation References

- [Bazel Query Language](https://bazel.build/query/language) - full query language reference
- [Bazel Query Guide](https://bazel.build/query/guide) - practical guide with examples
- [cquery Documentation](https://bazel.build/query/cquery) - configured query specifics
- [aquery Documentation](https://bazel.build/query/aquery) - action graph query specifics
- [rules_python](https://github.com/bazel-contrib/rules_python) - Python rules for Bazel
