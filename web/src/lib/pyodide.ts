import { useCallback, useEffect, useRef, useState } from "react";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type PyodideInterface = any;

let pyodidePromise: Promise<PyodideInterface> | null = null;

async function loadPyodide(): Promise<PyodideInterface> {
  const mod = await import("pyodide");
  return mod.loadPyodide({ indexURL: "https://cdn.jsdelivr.net/npm/pyodide@314.0.1/" });
}

function getPyodide(): Promise<PyodideInterface> {
  if (!pyodidePromise) {
    pyodidePromise = loadPyodide();
  }
  return pyodidePromise;
}

export function usePyodide() {
  const [ready, setReady] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pyodideRef = useRef<PyodideInterface | null>(null);

  useEffect(() => {
    if (pyodideRef.current) {
      setReady(true);
      return;
    }
    setLoading(true);
    getPyodide()
      .then((py) => {
        pyodideRef.current = py;
        setReady(true);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  const runCode = useCallback(async (code: string): Promise<string> => {
    const py = pyodideRef.current;
    if (!py) return "Pyodide 尚未加载完成";
    try {
      py.runPython("import sys; from io import StringIO; _stdout = StringIO(); sys.stdout = _stdout");
      await py.runPythonAsync(code);
      const output = py.runPython("_stdout.getvalue()");
      py.runPython("sys.stdout = sys.__stdout__");
      return output ? String(output) : "";
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      return `错误: ${msg}`;
    }
  }, []);

  return { ready, loading, error, runCode };
}
