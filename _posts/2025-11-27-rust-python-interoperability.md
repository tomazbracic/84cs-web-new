---
title: "Mixing Rust Into a Python/Flask App (GAE/Lambda) – My Notes"
date: 2025-11-27
tags: [rust, python, flask, pyo3, tokio]
published: true
---

# Mixing Rust Into a Python/Flask App (GAE/Lambda) – My Notes

Lately I've been running a Python app in Google App Engine (and occasionally AWS Lambda), and I ran into a part of the system that I'd really prefer to solve in **Rust**. The logic needs to be fast, async, and probably better handled in a compiled language. But my main service is **Flask**, so the big question I asked myself was:

> Can I write my logic in Rust (with Tokio!) and still use it as a Python module?  
> Or am I stuck with Python being single‑threaded and all that?

Turns out — yes — it works. And it's actually not that terrible once you get the workflow right.

Let me write down how I wrapped my head around it.

---

## Python, Rust, Tokio and the “single‑threaded question”

Python (CPython, specifically) has the GIL — meaning only one thread can really execute Python bytecode at a time. That scared me at first because Tokio is multi‑threaded and async. But here's the trick:

Rust code **does not run under the GIL** unless you make Python calls from it.

So if Rust is doing async IO or CPU work, it can run freely across threads. You just have to handle the boundaries properly. `pyo3` makes this mostly painless.

---

## What does Rust actually produce? Binary? `.so`? `.dylib`?

There are two ways I could approach this:

### 1. Compile Rust as a **separate binary** and call it from Python

```python
subprocess.run(["./my_rust_binary"])
```

This works, but means managing a second process, passing data via stdin/stdout/JSON, etc. Possible — but not elegant.

### 2. Build Rust as a **Python extension module**

This is what I actually want.

The output becomes a shared library (`.so/.pyd/.dylib` depending on OS), and when built as a Python module it ends up as something like:

- Linux: `my_rust_module.cpython-310-x86_64-linux-gnu.so`
- macOS: `my_rust_module.cpython-311-darwin.so`
- Windows: `my_rust_module.cp311-win_amd64.pyd`

And then I can just do:

```python
import my_rust_module
```

Perfect.

One important detail that confused me for a bit:

- In `Cargo.toml` we write `crate-type = ["cdylib"]`.  
- `cdylib` is **not** a file extension, it’s a crate type.  
- On macOS the underlying Rust output is a `.dylib`, but for Python extension modules the final file still ends with `.so` (even on macOS), because that’s what Python expects.

---

## The stack I ended up using

Tools I’m using:

| Purpose | Tool |
|---|---|
| Python bindings for Rust | `pyo3` |
| Build wheels / dev installs | `maturin` |
| Async runtime inside Rust | `tokio` |

---

## Minimal Rust setup (library crate, not binary)

I created a library crate:

```bash
cargo new my_rust_module --lib
cd my_rust_module
```

That gives me a `src/lib.rs` instead of `main.rs`, which is exactly what I want for a Python extension.

### `Cargo.toml`

Here’s my `Cargo.toml`:

```toml
[package]
name = "my_rust_module"
version = "0.1.0"
edition = "2021"

[lib]
name = "my_rust_module"
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.27.1", features = ["extension-module"] }
tokio = { version = "1", features = ["rt-multi-thread", "macros"] }
```

The key line is:

```toml
crate-type = ["cdylib"]
```

This tells Rust to build a C-compatible dynamic library that languages like Python can load.

### `src/lib.rs`

And this is the minimal `lib.rs` I used with pyo3 0.27 and Tokio:

```rust
use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use pyo3::types::PyModule;
use tokio::runtime::Runtime;

// Tiny async function run on Tokio
async fn async_double(x: i32) -> i32 {
    x * 2
}

#[pyfunction]
fn double_in_rust(x: i32) -> PyResult<i32> {
    // Create a Tokio runtime and run the async job
    let rt = Runtime::new()
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to create Tokio runtime: {e}")))?;

    let result = rt.block_on(async_double(x));
    Ok(result)
}

// New-style signature for PyO3 0.27
#[pymodule]
fn my_rust_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(double_in_rust, m)?)?;
    Ok(())
}
```

No Flask, no web anything yet — this is just a plain Python module backed by Rust and Tokio.

---

## Setting up Python and the virtual environment (with `uv`)

For this experiment I used `uv` to manage my Python and virtualenv for the project.

I initialized the project and pinned Python like this:

```bash
➜  RUST-PYTHON-interoperability uv init           
Initialized project `rust-python-interoperability`

➜  RUST-PYTHON-interoperability git:(master) ✗ uv python pin 3.14 
Updated `.python-version` from `3.13` -> `3.14`

➜  RUST-PYTHON-interoperability git:(master) ✗ cat .python-version 
3.14

➜  RUST-PYTHON-interoperability git:(master) ✗ uv venv --python 3.14
Using CPython 3.14.0 interpreter at: /opt/homebrew/opt/python@3.14/bin/python3.14
Creating virtual environment at: .venv
Activate with: source .venv/bin/activate

➜  RUST-PYTHON-interoperability git:(master) ✗ source .venv/bin/activate
(RUST-PYTHON-interoperability) ➜  RUST-PYTHON-interoperability git:(master) ✗ python --version
Python 3.14.0
```

So at this point I have:

- A project directory `RUST-PYTHON-interoperability`
- A `.python-version` file pinned to 3.14
- A virtualenv in `.venv` activated with Python 3.14

Inside that project I have the Rust crate `my_rust_module/` with the code above.

---

## The important bit: using `maturin` (not plain `cargo build`)

This is the part that tripped me up the most.

If you run `cargo build` directly on this crate, you’ll hit linker errors on macOS (things like `_PyBool_Type` undefined). That’s because `cargo` alone doesn’t know which Python to link against, and how.

For a **pyo3-based Python extension module**, the trick is:

> Use **maturin** to drive the build, not bare `cargo build`.

So from inside the Rust crate directory:

```bash
cd my_rust_module
```

I ran:

```bash
(RUST-PYTHON-interoperability) ➜  my_rust_module git:(master) ✗ maturin develop
  Downloaded portable-atomic v1.11.1
  Downloaded 1 crate (181.2KiB) in 0.40s
🔗 Found pyo3 bindings
🐍 Found CPython 3.14 at /Users/tomaz/razvoj/PYTHON_PROJECTS/RUST-PYTHON-interoperability/.venv/bin/python
   Compiling pyo3-build-config v0.27.1
   Compiling pyo3-macros-backend v0.27.1
   Compiling pyo3-ffi v0.27.1
   Compiling pyo3 v0.27.1
   Compiling pyo3-macros v0.27.1
   Compiling my_rust_module v0.1.0 (/Users/tomaz/razvoj/PYTHON_PROJECTS/RUST-PYTHON-interoperability/my_rust_module)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 4.00s
📦 Built wheel for CPython 3.14 to /var/folders/3r/7tps3c8n6yzgvk7vwrvzsl_r0000gn/T/.tmpCGpPKx/my_rust_module-0.1.0-cp314-cp314-macosx_11_0_arm64.whl
✏️ Setting installed package as editable
🛠 Installed my_rust_module-0.1.0
```

A few things are happening here:

- `maturin` detects pyo3 and the active Python interpreter in my `.venv`.
- It builds a proper wheel for that Python version and platform.
- It installs it **editable** into the current environment, so I can immediately import it from Python.

This completely sidesteps the linker errors I was getting with `cargo build` alone.

---

## Testing the Rust module from Python

Back in the project root (`RUST-PYTHON-interoperability`), I created a `main.py`:

```python
# main.py
import my_rust_module

def main():
    value = 21
    result = my_rust_module.double_in_rust(value)
    print(f"Rust async_double({value}) = {result}")

if __name__ == "__main__":
    main()
```

And then ran it:

```bash
(RUST-PYTHON-interoperability) ➜  my_rust_module git:(master) ✗ nano ../main.py 
(RUST-PYTHON-interoperability) ➜  my_rust_module git:(master) ✗ cd ..
(RUST-PYTHON-interoperability) ➜  RUST-PYTHON-interoperability git:(master) ✗ python main.py 
Rust async_double(21) = 42
```

That’s the whole round-trip:

- Rust async code with Tokio  
- Exposed to Python via pyo3  
- Built and installed with maturin  
- Imported and used from plain Python

No Flask yet, no GAE/Lambda yet — just the minimal building block working.

---

## Where this fits into Flask / GAE / Lambda

Now that the minimal Rust module works, wiring it into a Flask app is almost boring:

```python
from flask import Flask, jsonify
import my_rust_module

app = Flask(__name__)

@app.get("/calc/<int:n>")
def calc(n: int):
    result = my_rust_module.double_in_rust(n)
    return jsonify({"input": n, "output": result})
```

In GAE or Lambda, the main extra work is just:

- Building the wheel for the **correct platform** (Linux, correct Python version).
- Shipping that wheel with your deployment (or as a layer in Lambda).

But the core idea stays the same: Python is the web layer, Rust is the fast/async logic behind a neat function call.

---

## Why I like this setup

✔ I keep Flask + Python for the web layer  
✔ I move heavy async logic to Rust without rewriting the whole service  
✔ I can scale parts independently later if I want a microservice instead  
✔ And with `maturin`, the dev story is actually pretty smooth

If you’re reading this because you’re thinking *“could I mix Rust and Python like this?”* — then yes, you probably can.

And honestly, it feels pretty great.

—Tomaz
