# Sieve of Eratosthenes

Introduction.

```python <<main.py>>
from sieve import sieve

print(sieve(100))
```

```python <<sieve>>
def sieve(n):
    numbers = [True] * (n + 1)

    <<cross_out>>

    return [i for i in range(2, n + 1) if numbers[i]]
```

```python <<cross_out>>
for p in range(2, n + 1):
    if numbers[p]:
        for i in range(p * p, n + 1, p):
            numbers[i] = False
```
