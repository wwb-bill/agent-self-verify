# agent-self-verify

Self-verification harness for AI agents — evidence chains before accepting outputs. Inspired by OpenSquilla's "red-green regression evidence chains."

```bash
pip install agent-self-verify
agent-self-verify quick "hello world" --contains hello
agent-self-verify check spec.json output.txt
```

7 assertion types: contains, not-contains, min-length, max-length, matches, is-json, has-keys. CI-ready exit codes.

MIT
