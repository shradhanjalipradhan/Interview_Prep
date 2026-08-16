# Core Python for ML Engineering Interviews

A working reference covering basics → advanced, with the "why it matters" framed around ML engineering and code optimization.

---

## 1. Lists

**Basics**
- Ordered, mutable, allow duplicates: `nums = [1, 2, 3]`
- Indexing/slicing: `nums[0]`, `nums[-1]`, `nums[1:3]`, `nums[::-1]`
- Common ops: `.append()`, `.extend()`, `.pop()`, `.sort()`, `.remove()`

**Advanced**
- **Implementation**: dynamic array (over-allocates capacity so `append` is amortized O(1); inserting at index 0 is O(n))
- **Copying**: `list.copy()` / `list[:]` is shallow — nested lists still share references. Use `copy.deepcopy()` for nested mutable structures.
- **Memory**: lists store pointers to objects, not the objects themselves — this is why NumPy arrays (contiguous, typed memory) crush Python lists for numeric work.
- **List vs generator**: building a full list when you only need to iterate once wastes memory — prefer a generator for large/streaming data.
- **Sorting**: `sorted(data, key=lambda x: x[1], reverse=True)` — Timsort, O(n log n), stable.

**Interview traps**
- Mutable default argument bug: `def f(x=[]):` — the list persists across calls.
- `a = b = []` vs `a, b = [], []` — aliasing vs independent objects.

**Why it mattered in my work**
- Batching data for model input, holding intermediate predictions before converting to `np.array`/tensor, and building preprocessing pipelines where order matters (e.g., token sequences).
- Optimization angle: I've swapped list-based loops for vectorized NumPy/PyTorch ops when profiling showed list iteration was the bottleneck in a data pipeline — Python-level loops over lists are the first thing to suspect when throughput is low.

```python
# Example: batching predictions before converting to tensor
raw_scores = []
for row in dataset:
    raw_scores.append(model.predict_proba(row))
scores_tensor = torch.tensor(raw_scores)  # convert once, not per-row
```

---

## 2. Tuples

**Basics**
- Ordered, **immutable**, allow duplicates: `point = (3, 4)`
- Unpacking: `x, y = point`

**Advanced**
- Immutability → **hashable** (if all elements are hashable) → usable as dict keys / set members. Lists cannot be.
- Slightly faster to create and iterate than lists (fixed size, no over-allocation), and communicates intent: "this won't change."
- `namedtuple` / `typing.NamedTuple` for lightweight, self-documenting structured data without full class overhead.
- Tuple packing/unpacking is used heavily for function returns with multiple values (`return loss, accuracy`).

**Interview traps**
- A tuple containing a mutable object (e.g., a list) is technically immutable in structure but its contents can still change — and it becomes unhashable if that mutable element is present.
- `(1)` is an int, `(1,)` is a tuple — trailing comma required for single-element tuples.

**Why it mattered in my work**
- Using tuples as dictionary keys for caching — e.g., memoizing results keyed by `(model_name, input_hash)` or caching feature computations keyed by `(user_id, timestamp_bucket)`.
- Returning fixed-shape values like `(loss, accuracy, f1)` from training loops — immutability signals "don't reassign this mid-function," which reduces bugs during refactors/optimization passes.

```python
cache = {}
def get_embedding(text, model_version):
    key = (text, model_version)  # tuple as dict key
    if key not in cache:
        cache[key] = embed(text, model_version)
    return cache[key]
```

---

## 3. Sets

**Basics**
- Unordered, mutable, **no duplicates**: `s = {1, 2, 3}`
- Ops: `.add()`, `.remove()`, `.union()` (`|`), `.intersection()` (`&`), `.difference()` (`-`), `.symmetric_difference()` (`^`)

**Advanced**
- Implemented as a hash table → O(1) average membership check (`x in s`), vs O(n) for a list.
- `frozenset` — immutable, hashable version; usable as a dict key or set element.
- Set comprehensions: `{x**2 for x in range(10) if x % 2 == 0}`
- Deduplication while preserving *some* structure: `set()` loses order — use `dict.fromkeys(lst)` (Python 3.7+) if you need dedup + order preservation.

**Interview traps**
- Sets are unordered — never rely on iteration order for correctness (even though CPython dict preserves insertion order, sets do not guarantee it).
- Checking `x in list_of_10000` repeatedly in a loop is a classic performance bug — convert to a set once, then check membership.

**Why it mattered in my work**
- **This is one of my go-to optimizations.** Replacing `if item in some_list:` inside a hot loop with `if item in some_set:` turned an O(n·m) filtering step into O(n) — noticeable on large feature-engineering jobs (e.g., filtering out a blocklist of tokens/IDs from millions of rows).
- Deduplicating training examples, comparing label sets between train/val/test splits (`set(train_labels) - set(val_labels)` to catch label leakage or missing classes).

```python
# O(n*m) -> O(n): the single most common "quick win" optimization I make
blocklist = set(blocklist_ids)  # convert once
filtered = [row for row in dataset if row.id not in blocklist]
```

---

## 4. Dictionaries

**Basics**
- Key-value pairs, mutable, keys must be hashable: `d = {"lr": 0.01, "epochs": 10}`
- Access: `d["lr"]`, `d.get("lr", default)`, `.keys()`, `.values()`, `.items()`

**Advanced**
- Implemented as a hash table → O(1) average lookup/insert/delete.
- Since Python 3.7, insertion order is preserved (implementation detail turned language guarantee).
- `collections.defaultdict(list)` — avoids manual key-existence checks when grouping/aggregating.
- `collections.Counter` — subclass of dict purpose-built for counting (`Counter(labels).most_common(5)`).
- `collections.OrderedDict` — mostly legacy now that regular dicts preserve order, but still useful for `.move_to_end()` (e.g., LRU cache logic).
- Merging: `{**d1, **d2}` or (3.9+) `d1 | d2`.
- `dict.setdefault(key, default)` for one-line "insert if missing."

**Interview traps**
- Dict keys must be immutable/hashable — you can't use a list as a key (but a tuple works).
- Modifying a dict while iterating over it raises `RuntimeError` — iterate over `list(d.items())` if you need to mutate during iteration.

**Why it mattered in my work**
- Config management (hyperparameter dicts passed into training functions), storing model metrics per epoch (`{"epoch": 3, "loss": 0.21, "acc": 0.94}`), building vocabulary/token-to-index mappings (`word2idx`), and caching (dict as a memo table, as above).
- Optimization: using `Counter` instead of manually looping to build frequency tables — cleaner and implemented in C under the hood, so faster than a hand-rolled loop.

```python
from collections import Counter, defaultdict

label_counts = Counter(all_labels)                # class distribution check
grouped = defaultdict(list)
for row in dataset:
    grouped[row.category].append(row)              # no "if key not in d" boilerplate
```

---

## 5. List Comprehensions

**Basics**
```python
squares = [x**2 for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]
```

**Advanced**
- Nested comprehensions: `flat = [x for row in matrix for x in row]`
- Comprehensions are generally faster than equivalent `for` loops with `.append()` because the loop runs in optimized C-level bytecode (`LIST_APPEND`) rather than repeated attribute lookups for `.append`.
- Readability cutoff: if it needs a nested `if/else` and two levels of nesting, switch to a regular loop or a generator function — a comprehension that needs a comment to explain itself has failed its own purpose.
- Comprehension variables don't leak into the enclosing scope (Python 3 behavior, unlike `for` loops).

**Why it mattered in my work**
- Fast, readable preprocessing: normalizing text, filtering rows, extracting a single field from a list of dicts (`[row["label"] for row in dataset]`) before feeding into `sklearn`/`pandas`/`numpy`.
- Optimization lens: swapping a `for` loop + `.append()` for a comprehension is a small but real speedup, and it's usually the first micro-optimization I make when reviewing someone else's preprocessing code.

```python
# Building a filtered, transformed feature list in one readable line
tokens = [tok.lower() for tok in raw_tokens if tok not in stopwords]
```

---

## 6. Dictionary Comprehensions

**Basics**
```python
squares = {x: x**2 for x in range(5)}
```

**Advanced**
- Inverting a mapping: `inv = {v: k for k, v in d.items()}` (only safe if values are unique).
- Conditional dict comprehension: `{k: v for k, v in d.items() if v is not None}` — a common pattern for cleaning config dicts or model outputs before logging.
- Combine with `zip()` to build lookup tables in one line: `{k: v for k, v in zip(keys, values)}`.

**Why it mattered in my work**
- Building `label2id` / `id2label` mappings for classification models, filtering `None`/NaN values out of a results dict before writing to a metrics store, and quickly restructuring API/JSON responses.

```python
label2id = {label: idx for idx, label in enumerate(sorted(set(all_labels)))}
id2label = {idx: label for label, idx in label2id.items()}
```

---

## 7. `*args`

**Basics**
- Collects extra **positional** arguments into a tuple.
```python
def add_all(*args):
    return sum(args)
add_all(1, 2, 3)  # args = (1, 2, 3)
```

**Advanced**
- Unpacking on the call side: `add_all(*my_list)` spreads a list/tuple into positional args.
- Used to write wrapper functions/decorators that forward arguments without knowing the wrapped function's signature: `def wrapper(*args, **kwargs): return fn(*args, **kwargs)`.
- Order matters: `def f(a, b, *args, **kwargs)` — positional-or-keyword, then `*args`, then keyword-only, then `**kwargs`.

**Why it mattered in my work**
- Writing generic training/logging decorators (e.g., a `@log_execution_time` decorator that wraps arbitrary training functions), and utility functions that need to accept a variable number of tensors/arrays (e.g., a custom `concat_all(*tensors)` helper).

```python
def log_execution_time(fn):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)
        print(f"{fn.__name__} took {time.time() - start:.3f}s")
        return result
    return wrapper
```

---

## 8. `**kwargs`

**Basics**
- Collects extra **keyword** arguments into a dict.
```python
def configure(**kwargs):
    print(kwargs)
configure(lr=0.01, batch_size=32)  # {'lr': 0.01, 'batch_size': 32}
```

**Advanced**
- Unpacking on the call side: `model_fn(**config_dict)` — spreads a dict as keyword arguments, extremely common with ML config objects.
- Combined with `*args` for maximally flexible function signatures (decorators, wrapper/adapter functions around library APIs).
- Enables "pass-through" configs — you can accept a superset of kwargs and forward only what's relevant to an inner function.

**Why it mattered in my work**
- **Huge** in ML work: `sklearn`/`xgboost`/`torch` optimizers all accept config as kwargs. I regularly load a YAML/JSON hyperparameter config into a dict and call `Model(**config)` or `optimizer_cls(model.parameters(), **opt_config)` instead of hardcoding every parameter — makes hyperparameter sweeps trivial to wire up (e.g., with Optuna or a grid search loop).

```python
def build_optimizer(params, **kwargs):
    return torch.optim.Adam(params, **kwargs)

config = {"lr": 3e-4, "weight_decay": 1e-5, "betas": (0.9, 0.999)}
optimizer = build_optimizer(model.parameters(), **config)
```

---

## 9. Lambda Functions

**Basics**
- Anonymous, single-expression function: `square = lambda x: x**2`

**Advanced**
- No statements, no multi-line logic, implicit return — if it needs more than one expression, write a `def` instead.
- Most useful as a throwaway `key=` function (`sorted`, `max`, `min`) rather than assigned to a variable — PEP 8 explicitly discourages `f = lambda: ...`, prefer `def f(): ...` for anything named.
- Captures variables by reference (closures), not by value — the classic loop-closure bug:
```python
funcs = [lambda: i for i in range(3)]
[f() for f in funcs]  # [2, 2, 2], not [0, 1, 2] — all reference the same i
```
Fix with a default arg: `lambda i=i: i`.

**Why it mattered in my work**
- Sorting model results/leaderboards by a metric field, quick one-off transforms passed to `pandas.apply()` or `map()`, defining simple custom loss weighting or key functions without cluttering the module with named one-off functions.

```python
results.sort(key=lambda r: r["val_accuracy"], reverse=True)
df["clean_text"] = df["text"].apply(lambda t: t.strip().lower())
```

---

## 10. `map`

**Basics**
```python
list(map(str.upper, ["a", "b", "c"]))  # ['A', 'B', 'C']
```

**Advanced**
- Lazy — `map()` returns an iterator, not a list; nothing is computed until you iterate (or wrap in `list()`).
- Can take multiple iterables: `map(lambda x, y: x + y, list1, list2)` — stops at the shortest.
- Modern Python style generally prefers list/generator comprehensions over `map`+`lambda` for readability — but `map(func, iterable)` with a *named* function (not lambda) is still idiomatic and can be marginally faster since it avoids a Python-level loop, calling the function in a tight C loop.

**Why it mattered in my work**
- Applying a preprocessing function (e.g., a tokenizer or normalization function) across a large iterable without materializing an intermediate list, especially when chained into further lazy processing (`map` → `filter` → consumed once).

```python
cleaned = map(normalize_text, raw_documents)  # lazy, memory-efficient
```

---

## 11. `filter`

**Basics**
```python
list(filter(lambda x: x % 2 == 0, range(10)))
```

**Advanced**
- Also lazy, returns an iterator.
- `filter(None, iterable)` is a common idiom to drop all falsy values (`0`, `""`, `None`, `False`) in one call.
- Like `map`, mostly superseded by comprehensions/generator expressions for readability (`[x for x in data if predicate(x)]`) — but useful in a functional/lazy pipeline where you're chaining operations without materializing intermediate lists.

**Why it mattered in my work**
- Filtering out malformed or empty records from a raw dataset before featurization, especially when composed in a streaming pipeline where memory matters (e.g., filtering a generator of log lines before parsing).

```python
valid_rows = filter(lambda r: r.get("label") is not None, raw_rows)
```

---

## 12. `zip`

**Basics**
```python
list(zip([1,2,3], ["a","b","c"]))  # [(1,'a'), (2,'b'), (3,'c')]
```

**Advanced**
- Lazy iterator, stops at the shortest input — use `itertools.zip_longest(fillvalue=...)` if you need to pad instead of truncate.
- `zip(*matrix)` transposes a list of lists — a neat, no-numpy way to pivot rows/columns.
- Extremely common for pairing predictions with ground truth, feature names with values, or building dicts: `dict(zip(keys, values))`.
- Unzipping: `xs, ys = zip(*pairs)`.

**Why it mattered in my work**
- Pairing `y_true` and `y_pred` when computing custom metrics or writing error analysis (`for true, pred in zip(y_true, y_pred): ...`), zipping feature names with a row of values for logging/debugging, and building quick lookup dicts from two parallel lists returned by an API.

```python
errors = [(t, p) for t, p in zip(y_true, y_pred) if t != p]  # misclassified pairs
feature_dict = dict(zip(feature_names, row_values))
```

---

## 13. `enumerate`

**Basics**
```python
for i, val in enumerate(["a", "b", "c"]):
    print(i, val)
```

**Advanced**
- `enumerate(iterable, start=1)` — custom starting index, handy for human-readable logging (epoch 1, not epoch 0).
- Avoids the anti-pattern `for i in range(len(lst)): item = lst[i]` — `enumerate` is more Pythonic and slightly faster since it avoids repeated indexing.
- Works with any iterable (files, generators), not just lists — e.g., `for i, line in enumerate(open("log.txt")):` for reading large files line by line with a counter, without loading the whole file.

**Why it mattered in my work**
- Logging progress during training loops (`for step, batch in enumerate(dataloader):`), tracking indices for error analysis (knowing *which* row in the original dataset a bad prediction came from), and batch-numbering in custom data loaders.

```python
for step, (batch_x, batch_y) in enumerate(dataloader, start=1):
    loss = train_step(batch_x, batch_y)
    if step % 100 == 0:
        print(f"step {step}: loss={loss:.4f}")
```

---

## Quick-fire interview soundbite (tie it all together)

If asked to summarize your philosophy in one line:

> "I default to the right data structure for the access pattern — sets/dicts for O(1) lookups instead of scanning lists, comprehensions and lazy iterators (`map`/`filter`/generators) to avoid materializing data I don't need, and `*args`/`**kwargs` to keep config-driven ML code (models, optimizers, sweeps) flexible without rewriting function signatures every time a hyperparameter changes."

This framing signals both fundamentals *and* the optimization mindset interviewers are probing for in an ML engineering role.
