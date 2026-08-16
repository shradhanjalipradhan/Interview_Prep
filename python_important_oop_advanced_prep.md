# Python Important Concepts, OOP & Advanced Intro — Interview Prep (Part 2)

---

# SECTION A: Important Concepts

## 1. Mutable vs Immutable

**Basics**
- Mutable: can change in place — `list`, `dict`, `set`, custom objects by default. `x.append(1)` changes `x` itself.
- Immutable: cannot change in place — `int`, `float`, `str`, `tuple`, `frozenset`, `bool`. Any "change" creates a new object.

**Advanced**
- Immutability → hashability (usually) → usable as dict keys/set members.
- Function default arguments are evaluated **once** at definition time — mutable defaults (`def f(x=[])`) persist across calls and are a classic bug source.
- Passing arguments: Python is "pass by object reference." Mutating a mutable argument inside a function affects the caller's object; reassigning the parameter name does not.
- String immutability means repeated concatenation in a loop (`s += chunk`) is O(n²) — each `+=` creates a new string. Use `"".join(list_of_strings)` instead, which is O(n).

**Interview traps**
```python
def append_item(item, target=[]):   # BUG: default list is shared across calls
    target.append(item)
    return target

append_item(1)  # [1]
append_item(2)  # [1, 2]  <- unexpected!
```

**Why it mattered in my work**
- This is a real bug class I've hit and had to fix in shared preprocessing utilities — a mutable default in a helper function silently accumulated state across dataset batches. Now I always default to `None` and initialize inside the function.
- Optimization angle: swapping loop-based string concatenation for `"".join()` when building large text outputs (e.g., constructing prompts or serializing logs) is a real, measurable speedup on large inputs.

```python
def safe_append(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

---

## 2. Shallow Copy vs Deep Copy

**Basics**
- **Shallow copy** (`list.copy()`, `dict.copy()`, `copy.copy()`, slicing `[:]`): copies the container, but nested objects are still shared references.
- **Deep copy** (`copy.deepcopy()`): recursively copies everything — container and all nested objects, fully independent.

**Advanced**
- Shallow copy is fine for flat structures (list of ints/strings). It's a trap for nested structures (list of lists, dict of dicts, list of custom objects) — mutating a nested element affects both "copies."
- `deepcopy` is slower and uses more memory — recursion + tracking already-copied objects (to handle cycles) has real cost. Don't reach for it by default; use it only when you genuinely need independence.
- For NumPy/pandas: `.copy()` defaults to a deep copy of the data buffer for arrays/DataFrames — different convention than plain Python containers, worth knowing explicitly.

**Interview traps**
```python
import copy
original = [[1, 2], [3, 4]]
shallow = original.copy()
shallow[0].append(99)
print(original)  # [[1, 2, 99], [3, 4]] <- original mutated too!

deep = copy.deepcopy(original)
deep[0].append(100)
print(original)  # unaffected
```

**Why it mattered in my work**
- Config dictionaries in hyperparameter sweeps: if I shallow-copy a base config and mutate a nested dict (e.g., `optimizer_config`) for one experiment, it silently corrupts the base config used by other experiments running in the same loop. I now explicitly `deepcopy` config templates before mutating per-run.
- Debugging a hard-to-trace bug where augmented training batches were bleeding state between epochs because of a shallow copy of a nested list of tensors.

```python
base_config = {"model": {"layers": [64, 32]}, "lr": 0.01}
for lr in [0.01, 0.001]:
    run_config = copy.deepcopy(base_config)  # safe, independent
    run_config["lr"] = lr
    train(run_config)
```

---

## 3. `is` vs `==`

**Basics**
- `==` compares **value** equality (calls `__eq__`).
- `is` compares **identity** — are these the exact same object in memory (same `id()`).

**Advanced**
- Always use `is` for `None`, `True`, `False` checks — these are singletons: `if x is None:` not `if x == None:`.
- CPython caches small integers (-5 to 256) and short strings — `a = 5; b = 5; a is b` is `True` due to interning, but this is an implementation detail, **never rely on it** for larger numbers/strings (`a = 1000; b = 1000; a is b` is often `False`).
- `is` is O(1) (pointer comparison); `==` can be arbitrarily expensive depending on `__eq__` (e.g., comparing large arrays/objects).

**Interview traps**
```python
a = [1, 2, 3]
b = [1, 2, 3]
a == b   # True  (same values)
a is b   # False (different objects)

x = None
x == None  # True, but not idiomatic
x is None  # True, correct/Pythonic
```

**Why it mattered in my work**
- Constantly used in guard clauses: `if config.get("threshold") is None:` to distinguish "not provided" from "explicitly set to 0/False" — a real bug source in ML configs where `0` and `None` mean very different things (e.g., `dropout=0` vs `dropout` unset).

---

## 4. `None`

**Basics**
- `None` is Python's null/absence-of-value singleton, type `NoneType`.
- Default return value of any function without an explicit `return`.

**Advanced**
- Used as a sentinel for "not yet computed" / "not provided" — critical to distinguish from falsy-but-meaningful values like `0`, `""`, `[]`, `False`.
- `Optional[X]` in type hints (`from typing import Optional`) is shorthand for `Union[X, None]` — signals to both readers and static type checkers that a value may be absent.
- Common pattern: `value = value or default` is **dangerous** if `0`/`""`/`False` are valid values — use `value if value is not None else default` instead.

**Why it mattered in my work**
- Handling missing/NaN values in ML pipelines: distinguishing "feature not present" (`None`) from "feature present but zero" is critical for correct imputation logic — conflating them silently corrupts model input.
- API/model outputs where a prediction function may return `None` for "no confident prediction" vs. an actual score of `0.0`.

```python
def get_prediction(x, threshold=None):
    score = model.predict(x)
    if threshold is not None and score < threshold:
        return None  # explicitly "no confident prediction"
    return score
```

---

## 5. Exception Handling

**Basics**
```python
try:
    risky()
except ValueError as e:
    print(f"Bad value: {e}")
except (TypeError, KeyError) as e:
    print(f"Other issue: {e}")
else:
    print("ran if no exception")
finally:
    print("always runs")
```

**Advanced**
- Catch the **most specific** exception possible — bare `except:` (or `except Exception:` used too broadly) hides real bugs and makes debugging painful. Reserve broad catches for top-level boundaries (e.g., an API handler) where you must not crash, and log the full traceback there.
- Custom exceptions for domain-specific error signaling: `class DataValidationError(Exception): pass` — makes calling code able to catch precisely what it expects.
- `raise ... from e` preserves the original traceback context when re-raising as a different exception type — invaluable for debugging chained failures.
- `finally` runs even if you `return` inside `try`/`except` — used for guaranteed cleanup (closing files, releasing GPU memory, closing DB connections).
- Exceptions have real performance cost only when *raised* — a `try` block with no exception raised is nearly free in CPython, so "try/except as control flow" (EAFP — "easier to ask forgiveness than permission") is idiomatic Python and often faster than pre-checking (LBYL) when the exceptional path is rare.

**Why it mattered in my work**
- Training pipelines that process large datasets need to survive a handful of malformed rows without crashing a multi-hour job — I wrap per-row processing in narrow `try/except` blocks, log the failure with context, and continue, rather than letting one bad record kill the whole run.
- GPU/resource cleanup: using `finally` (or better, context managers — see below) to guarantee `torch.cuda.empty_cache()` or file/connection closing happens even on failure.

```python
class DataValidationError(Exception):
    pass

def process_row(row):
    try:
        return transform(row)
    except (KeyError, ValueError) as e:
        raise DataValidationError(f"Row {row.get('id')} failed: {e}") from e

results, failures = [], []
for row in dataset:
    try:
        results.append(process_row(row))
    except DataValidationError as e:
        failures.append(str(e))  # log and continue, don't crash the whole job
```

---

## 6. Iterators

**Basics**
- An **iterable** is anything you can loop over (`list`, `dict`, `str`, ...) — it implements `__iter__`.
- An **iterator** is the object that does the actual stepping — it implements `__next__` and raises `StopIteration` when exhausted.
- `for x in y:` internally calls `iter(y)` to get an iterator, then repeatedly calls `next()` on it.

**Advanced**
- Building a custom iterator:
```python
class CountUp:
    def __init__(self, n):
        self.n = n
        self.i = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.i >= self.n:
            raise StopIteration
        self.i += 1
        return self.i
```
- Iterators are **stateful and single-use** — once exhausted, you can't restart without creating a new one. This trips people up with generators consumed twice.
- `iter()` with a sentinel: `iter(callable, sentinel)` — calls `callable()` repeatedly until it returns `sentinel`. Niche but shows up in "read until EOF" style code.

**Why it mattered in my work**
- Understanding the iterator protocol explains *why* PyTorch's `DataLoader` behaves the way it does (it's an iterable that produces a fresh iterator each epoch) — knowing this saved me from a bug where I accidentally exhausted a data iterator once and then wondered why subsequent epochs yielded nothing.

---

## 7. Generators

**Basics**
- A function using `yield` instead of `return` becomes a generator — calling it returns a generator object (an iterator) without running the body immediately.
```python
def count_up(n):
    i = 1
    while i <= n:
        yield i
        i += 1
```
- Generator expressions: `(x**2 for x in range(1000000))` — same syntax as a list comprehension but with `()` instead of `[]`, and it's lazy.

**Advanced**
- **Lazy evaluation**: values are computed one at a time, on demand — massive memory savings for large/streaming datasets vs. building a full list upfront.
- Execution pauses at `yield` and resumes exactly there on the next `next()` call — state (local variables, loop position) is preserved between calls automatically, which is much simpler than hand-rolling a stateful iterator class.
- `yield from` delegates to a sub-generator/sub-iterable — useful for composing generator pipelines.
- Generators can receive values too via `.send()`, and support `.throw()`/`.close()` — rarely needed day-to-day but shows depth if asked.
- A generator is exhausted after one full pass — if you need to iterate multiple times, either recreate it or materialize to a list (trading memory for reusability).

**Interview traps**
- `sum(gen)` after already consuming `gen` once returns `0` / empty — generators don't reset.
- Generators don't support `len()` or random indexing — only sequential access.

**Why it mattered in my work**
- **This is central to ML data pipelines.** Loading a huge dataset (e.g., millions of text/image records) into a Python list would blow memory — instead I write generator-based data loaders that read, preprocess, and yield one batch at a time, keeping memory flat regardless of dataset size. This is exactly the pattern behind PyTorch's `IterableDataset` and TensorFlow's `tf.data` pipelines.
- Optimization framing: generators let me build multi-stage lazy pipelines (`read → filter → tokenize → batch`) where nothing is computed until the final consumer pulls a batch — no wasted work, no intermediate full-dataset materialization.

```python
def stream_batches(file_path, batch_size=32):
    batch = []
    with open(file_path) as f:
        for line in f:                     # lazy, one line at a time
            batch.append(preprocess(line))
            if len(batch) == batch_size:
                yield batch
                batch = []
    if batch:
        yield batch  # last partial batch

for batch in stream_batches("huge_dataset.txt"):
    train_step(batch)   # constant memory, regardless of file size
```

---

# SECTION B: OOP

## 1. Class & Object

**Basics**
- A **class** is a blueprint; an **object** (instance) is a concrete thing built from that blueprint.
```python
class Model:
    def __init__(self, name):
        self.name = name

m = Model("resnet")  # m is an instance/object of class Model
```

**Advanced**
- Class attributes (shared across all instances) vs instance attributes (per-object) — a common bug is mutating a class-level *mutable* attribute (like a list) thinking it's per-instance.
- `@classmethod` (operates on the class, `cls`) vs `@staticmethod` (no implicit first arg, just namespaced under the class) vs instance methods (operate on `self`).
- `@property` — expose a method as if it were an attribute, useful for computed/validated fields without breaking the public interface if implementation changes later.

**Why it mattered in my work**
- Every custom PyTorch `nn.Module`, `sklearn`-style estimator, or data pipeline component I write is a class — understanding instance vs. class state prevents subtle bugs like accidentally sharing a mutable buffer across multiple model instances in a multi-model serving setup.

---

## 2. Inheritance

**Basics**
```python
class BaseModel:
    def predict(self, x):
        raise NotImplementedError

class LogisticModel(BaseModel):
    def predict(self, x):
        return sigmoid(self.weights @ x)
```

**Advanced**
- `super().__init__(...)` calls the parent constructor — essential when the child needs to extend, not replace, parent initialization.
- Multiple inheritance and **MRO** (Method Resolution Order, via C3 linearization) — Python resolves ambiguity through a defined, inspectable order (`ClassName.__mro__`).
- Mixins: small classes meant to be combined via multiple inheritance to add a specific capability (e.g., a `LoggingMixin`) without a rigid single-parent hierarchy.
- Favor **composition over inheritance** when the relationship isn't a true "is-a" — deep inheritance chains get brittle fast, especially in ML codebases with many model variants.

**Why it mattered in my work**
- Building a `BaseModel` abstract interface (`fit`, `predict`, `save`, `load`) and having every concrete model (logistic regression wrapper, transformer wrapper, ensemble) inherit from it — this let downstream serving/evaluation code treat all models polymorphically without knowing the concrete type.

```python
class BaseModel:
    def fit(self, X, y): raise NotImplementedError
    def predict(self, X): raise NotImplementedError

class SklearnWrapper(BaseModel):
    def __init__(self, estimator):
        self.estimator = estimator
    def fit(self, X, y):
        self.estimator.fit(X, y)
    def predict(self, X):
        return self.estimator.predict(X)
```

---

## 3. Encapsulation

**Basics**
- Bundling data + methods together, and restricting direct external access to internal state.
- Python convention (not enforcement): `_var` = "internal, don't touch" (soft convention), `__var` = name-mangled (harder to access accidentally, not truly private).

**Advanced**
- Python has **no true private access modifiers** (unlike Java/C++) — it relies on convention and discipline ("we're all consenting adults here").
- `@property` + a private-ish backing attribute is the idiomatic way to add validation/computed logic while keeping a clean public API:
```python
class Model:
    def __init__(self, lr):
        self._lr = lr
    @property
    def lr(self):
        return self._lr
    @lr.setter
    def lr(self, value):
        if value <= 0:
            raise ValueError("lr must be positive")
        self._lr = value
```

**Why it mattered in my work**
- Wrapping model configuration objects so invalid hyperparameters (negative learning rate, out-of-range dropout) fail fast at assignment time rather than silently producing garbage results hours into a training run.

---

## 4. Polymorphism

**Basics**
- Different classes respond to the same method call in their own way.
```python
for model in [LogisticModel(), TreeModel(), NeuralModel()]:
    print(model.predict(x))  # each implements predict() differently
```

**Advanced**
- **Duck typing**: Python doesn't require a shared base class for polymorphism to work — "if it walks like a duck and quacks like a duck." Any object with a `.predict()` method works in the loop above; inheritance is a convenience, not a requirement.
- Operator overloading is a form of polymorphism (`__add__`, `__eq__`, etc.) — lets custom objects work naturally with `+`, `==`, etc.

**Why it mattered in my work**
- The `BaseModel` interface example above is polymorphism in action: evaluation/serving code calls `.predict()` on any model without caring whether it's sklearn, PyTorch, or a custom rule-based baseline — this made A/B testing different model types trivial to wire into the same pipeline.

---

## 5. Abstraction

**Basics**
- Hiding implementation complexity behind a simple interface — the caller knows *what* a method does, not *how*.

**Advanced**
- `abc.ABC` + `@abstractmethod` — enforce that subclasses *must* implement certain methods, raising `TypeError` at instantiation if they don't (stronger guarantee than a plain `NotImplementedError` in a base method, which only fails at call time).
```python
from abc import ABC, abstractmethod

class BaseModel(ABC):
    @abstractmethod
    def predict(self, x): ...
```
- Abstraction in ML often shows up as interface design: a `DataLoader` abstraction hides *how* data is fetched (disk, DB, S3) from the training loop that just calls `next(batch)`.

**Why it mattered in my work**
- Using `ABC`/`@abstractmethod` for a base pipeline interface caught a teammate's incomplete model wrapper (missing `predict`) at import/instantiation time in CI, instead of failing deep into a training run — cheap bug to catch early, expensive to catch late.

---

## 6. `__init__`

**Basics**
- The constructor — runs automatically when an object is created, sets up initial state.
```python
class Dataset:
    def __init__(self, path, transform=None):
        self.path = path
        self.transform = transform
```

**Advanced**
- `__init__` doesn't *create* the object (that's `__new__`) — it *initializes* an already-created instance. You almost never need to touch `__new__` unless doing something exotic (metaclasses, immutable subclassing).
- Validation belongs in `__init__` when possible — fail fast on bad construction rather than deep into later method calls.
- `dataclasses.dataclass` auto-generates `__init__` (plus `__repr__`, `__eq__`) from type-annotated class attributes — reduces boilerplate for simple data-holding classes (very common for config objects).

**Why it mattered in my work**
- Using `@dataclass` for training config objects instead of hand-writing `__init__` boilerplate — less code, fewer typos, and free `__repr__`/`__eq__` for debugging and testing config equality between runs.

```python
from dataclasses import dataclass

@dataclass
class TrainConfig:
    lr: float = 1e-3
    batch_size: int = 32
    epochs: int = 10
```

---

## 7. `__str__` and `__repr__`

**Basics**
- `__str__`: "informal", human-readable — called by `print(obj)` and `str(obj)`.
- `__repr__`: "official", unambiguous — called by the REPL, inside containers (`print([obj])` uses `repr`, not `str`), and by `repr(obj)`.

**Advanced**
- Rule of thumb: `__repr__` should ideally be valid Python that could recreate the object (`Model(name='resnet', lr=0.01)`), or at least be precise/debuggable. `__str__` can be friendlier/looser.
- If only `__repr__` is defined, Python falls back to it for `str()` too — so at minimum, always define `__repr__`.
- Default `__repr__` (if neither is defined) is unhelpful: `<Model object at 0x7f8b2c0a3d90>` — makes debugging painful, especially when a list of these objects gets logged.

**Why it mattered in my work**
- Defining `__repr__` on model/config/result objects means logs and stack traces are immediately readable (`TrainConfig(lr=0.001, batch_size=32, epochs=10)` vs. a memory address) — this alone has saved real debugging time when triaging failed training runs from logs.

```python
class TrainResult:
    def __init__(self, loss, acc):
        self.loss, self.acc = loss, acc
    def __repr__(self):
        return f"TrainResult(loss={self.loss:.4f}, acc={self.acc:.4f})"
    def __str__(self):
        return f"Loss: {self.loss:.4f}, Accuracy: {self.acc:.2%}"
```

---

# SECTION C: Advanced Python (Intro Level)

## 1. Decorators

**Basics**
- A decorator wraps a function to extend its behavior without modifying its source: `@decorator` above a `def`.
```python
def my_decorator(fn):
    def wrapper(*args, **kwargs):
        print("before")
        result = fn(*args, **kwargs)
        print("after")
        return result
    return wrapper

@my_decorator
def greet():
    print("hello")
```

**Advanced (intro level)**
- `functools.wraps` should always be used inside a decorator's inner function to preserve the original function's `__name__`/`__doc__` — without it, debugging/introspection tools see the wrapper's identity instead of the real function's.
- Decorators with arguments require an extra layer of nesting (a decorator factory): `@retry(times=3)`.
- Built-ins you already use constantly: `@staticmethod`, `@classmethod`, `@property`, `@functools.lru_cache`.

**Why it mattered in my work**
- Writing `@timing` and `@retry` decorators for training/data pipeline functions — timing decorators for profiling which pipeline stage is the bottleneck (directly tied to my optimization habit), retry decorators for flaky network calls (downloading datasets/model weights).

```python
import functools, time

def timing(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        print(f"{fn.__name__}: {time.perf_counter() - start:.3f}s")
        return result
    return wrapper

@timing
def load_and_preprocess(path):
    ...
```

---

## 2. Context Managers

**Basics**
- `with` blocks guarantee setup/teardown even if an exception occurs — most familiar as `with open("f.txt") as f: ...` (file auto-closes).

**Advanced (intro level)**
- Implement the protocol via `__enter__`/`__exit__` on a class, or more simply with `@contextlib.contextmanager` on a generator function (code before `yield` is setup, code after is teardown/cleanup, wrapped in `try/finally` implicitly).
```python
from contextlib import contextmanager

@contextmanager
def timer(label):
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"{label}: {time.perf_counter() - start:.3f}s")

with timer("preprocessing"):
    preprocess(data)
```
- `__exit__` can suppress exceptions by returning `True` — rarely desirable, but good to know it's possible.
- Multiple context managers: `with open(a) as fa, open(b) as fb:` — cleaner than nesting.

**Why it mattered in my work**
- Guaranteed cleanup around GPU memory / DB connections / temporary files — e.g., a context manager wrapping a training run that always logs final metrics and releases resources, even if the run crashes midway. Also used the `timer` pattern above extensively for profiling pipeline stages.

---

## 3. GIL (Global Interpreter Lock)

**Intro-level understanding**
- CPython's GIL allows only **one thread to execute Python bytecode at a time**, even on multi-core machines — it exists to make memory management (reference counting) thread-safe without fine-grained locks everywhere.
- Consequence: pure-Python, CPU-bound multithreading does **not** give you parallel speedup — threads take turns holding the GIL.
- The GIL is released during I/O waits (disk, network) and inside many C-extension operations (NumPy, PyTorch ops release it during heavy computation) — this is *why* threading still helps for I/O-bound work and why NumPy/PyTorch can use multiple cores despite the GIL.

**Why it mattered in my work**
- Explains a real decision I've had to make: for CPU-bound preprocessing (e.g., pure-Python tokenization loops), threading gave no speedup — I switched to `multiprocessing` (separate processes, separate GILs) to actually use multiple cores. For I/O-bound work (downloading files, calling an API), threading was the right, lighter-weight choice.

---

## 4. Threading vs Multiprocessing

**Intro-level understanding**
- **Threading** (`threading` module): lightweight, shares memory space, good for **I/O-bound** tasks (network calls, file I/O, waiting on external services) where the GIL is released during the wait.
- **Multiprocessing** (`multiprocessing` module): separate processes, separate memory (each with its own GIL/interpreter) — true parallelism for **CPU-bound** tasks, but higher overhead (process startup, inter-process communication/serialization via pickling).
- Rule of thumb: I/O-bound → threading (or `asyncio`); CPU-bound → multiprocessing (or push the work into a C-extension like NumPy that releases the GIL internally).

**Why it mattered in my work**
- Used `multiprocessing.Pool` to parallelize CPU-heavy feature engineering across cores on a large dataset — real wall-clock speedup proportional to core count, unlike an equivalent threaded version which showed almost no improvement due to the GIL.
- Used threading (or `concurrent.futures.ThreadPoolExecutor`) for concurrent API calls (e.g., fetching data from multiple endpoints) — I/O-bound, so threads overlap wait time effectively without process overhead.

```python
from multiprocessing import Pool

def heavy_feature_engineering(row):
    ...  # CPU-bound work

with Pool(processes=8) as pool:
    results = pool.map(heavy_feature_engineering, dataset)  # true parallel speedup
```

---

## 5. Async/Await

**Intro-level understanding**
- `asyncio` provides **cooperative concurrency** on a single thread — an `async def` function (coroutine) voluntarily yields control at each `await` point, letting other coroutines run while it's waiting (e.g., on network I/O).
- Different from threading/multiprocessing: no real parallelism, no GIL contention, just efficient interleaving of I/O-bound waits — can handle thousands of concurrent I/O-bound tasks far more cheaply than thousands of threads.
- Requires `await`-compatible ("async") libraries throughout the call chain — mixing blocking synchronous calls inside an `async def` blocks the whole event loop, defeating the purpose.
- `asyncio.gather(*tasks)` runs multiple coroutines concurrently and waits for all to finish.

**Why it mattered in my work**
- Useful for concurrently calling multiple external model/API endpoints (e.g., an ensemble that queries several hosted model APIs, or fetching data from several sources before a batch job) — awaiting all of them concurrently is far faster than sequential calls, and lighter-weight than spinning up threads for the same job.

```python
import asyncio, aiohttp

async def fetch(session, url):
    async with session.get(url) as resp:
        return await resp.json()

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(*[fetch(session, u) for u in urls])
```

---

## Quick-fire interview soundbite

> "I reach for the right concurrency model based on the bottleneck: threading or async for I/O-bound waits, multiprocessing for CPU-bound work that needs real parallelism across cores — because the GIL means pure-Python threads won't speed up CPU-heavy code. At the object level, I lean on abstraction (ABCs) and polymorphism to build ML pipelines where model types are swappable, with `__repr__`/dataclasses making everything debuggable from logs alone."
