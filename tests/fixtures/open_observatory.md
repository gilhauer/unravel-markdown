# Open Observatory Network

The concepts are introduced before the generated file layout.

```python <<observation model>>
STATIONS = ["Reykjavík", "Nairobi"]
```

```python <<test body>>
from observatory import STATIONS

def test_stations():
    assert STATIONS == ["Reykjavík", "Nairobi"]
```

```python <<application/observatory.py>>
"""Tiny, offline observatory model."""
<<observation model>>
```

```python <<tests/test_observation.py>>
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "application"))
<<test body>>
```

```yaml <<inventory concepts>>
all:
  hosts:
    station:
      ansible_host: 192.0.2.10
```

```yaml <<ansible/inventory.yml>>
<<inventory concepts>>
```

```yaml <<ansible/playbooks/site.yml>>
- hosts: all
  roles:
    - observatory
```

```yaml <<ansible task>>
- name: Install observatory
  ansible.builtin.debug:
    msg: ready
```

```yaml <<ansible/roles/observatory/tasks/main.yml>>
<<ansible task>>
```

```hcl <<terraform provider>>
terraform {
  required_version = ">= 1.5"
}
```

```hcl <<terraform/main.tf>>
<<terraform provider>>

module "station" {
  source = "./modules/station"
}
```

```hcl <<terraform/variables.tf>>
variable "station_name" {
  type = string
}
```

```hcl <<terraform/outputs.tf>>
output "station" {
  value = var.station_name
}
```

```hcl <<terraform/modules/station/main.tf>>
locals {
  enabled = true
}
```

The helper is deliberately continued after its first use.

```python <<observation model>>
NETWORK = "open-observatory"
```
