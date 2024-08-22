# turn yosys json into a circuit.sim that CircuitSim can open
import json
import itertools
import os
from yowasp_yosys import run_yosys
from dataclasses import dataclass, field

run_yosys(["script.ys"])  # TODO: don't depend on CWD

with open("out.json") as f:
  data = json.load(f)

assert len(data["modules"]) == 1, "unable to detect top level module"
top = next(iter(data["modules"].values()))

circuit = {
  "name": "verilog output",
  "components": [],
  "wires": []
}

y_level = itertools.count()
assert next(y_level) == 0

allocated_wires = {}  # wire -> (start x, y level)
START_AT = 10
initial_x = START_AT + 1

for name, port in sorted(top["ports"].items()):  # sort by names
  # layout the port and the wire, maybe with a splitter
  size = len(port["bits"])

  y = next(y_level)  # top
  next(y_level)  # middle
  next(y_level)  # bottom

  # place the input or output
  circuit["components"].append({
    "name": "com.ra4king.circuitsim.gui.peers.wiring.PinPeer",
    "x": START_AT,
    "y": y,
    "properties": {
      "Label location": "WEST",
      "Label": name,
      "Is input?": "Yes" if port["direction"] == "input" else "No",
      "Bitsize": str(size)
    }
  })

  # place 1bit wires
  if size == 1:
    initial_x = max(initial_x, size + START_AT + 1)
    allocated_wires[port["bits"][0]] = (size + START_AT, y + 1)
  else:
    # the above *would* work, but I want 1bit wires.
    initial_x = max(initial_x, size + START_AT + 3)
    for bit in port["bits"]:
      allocated_wires[bit] = (size + START_AT + 2, next(y_level))

    properties = {
      "Input location": "Left/Top",
      "Direction": "EAST",
      "Bitsize": str(size),
      "Fanouts": str(size),
      **{f"Bit {i}": str(i) for i in range(size)}
    }

    circuit["components"].append({
      "name": "com.ra4king.circuitsim.gui.peers.wiring.SplitterPeer",
      "x": size + START_AT,
      "y": y + 1,
      "properties": properties,
    })

for wire in top["netnames"].values():
  for bit in wire["bits"]:
    if bit not in allocated_wires:
      allocated_wires[bit] = (START_AT, next(y_level))

x_level = itertools.count()
for _ in range(initial_x):
  next(x_level)

# now, add the gates
y = next(y_level)

for gate in top["cells"].values():
  if gate["type"] == "NAND":
    x = next(x_level)
    for _ in range(6):
      next(x_level)
    A = gate["connections"]["A"]
    assert len(A) == 1
    A = A[0]

    B = gate["connections"]["B"]
    assert len(B) == 1
    B = B[0]

    Y = gate["connections"]["Y"]
    assert len(Y) == 1
    Y = Y[0]

    circuit["wires"].append({
      "x": x,
      "y": allocated_wires[A][1],
      "length": y + 1 - allocated_wires[A][1],
      "isHorizontal": False
    })
    circuit["wires"].append({
      "x": x,
      "y": y + 1,
      "length": 2,
      "isHorizontal": True
    })
    circuit["wires"].append({
      "x": x + 1,
      "y": allocated_wires[B][1],
      "length": y + 3 - allocated_wires[B][1],
      "isHorizontal": False
    })
    circuit["wires"].append({
      "x": x + 1,
      "y": y + 3,
      "length": 1,
      "isHorizontal": True
    })
    circuit["components"].append({
      "name": "com.ra4king.circuitsim.gui.peers.gates.NandGatePeer",
      "x": x + 2,
      "y": y,
      "properties": {
        "Bitsize": "1"
      }
    })
    circuit["wires"].append({
      "x": x + 6,
      "y": allocated_wires[Y][1],
      "length": y + 2 - allocated_wires[Y][1],
      "isHorizontal": False
    })
  elif gate["type"] == "NOR":
    x = next(x_level)
    for _ in range(6):
      next(x_level)
    A = gate["connections"]["A"]
    assert len(A) == 1
    A = A[0]

    B = gate["connections"]["B"]
    assert len(B) == 1
    B = B[0]

    Y = gate["connections"]["Y"]
    assert len(Y) == 1
    Y = Y[0]

    circuit["wires"].append({
      "x": x,
      "y": allocated_wires[A][1],
      "length": y + 1 - allocated_wires[A][1],
      "isHorizontal": False
    })
    circuit["wires"].append({
      "x": x,
      "y": y + 1,
      "length": 2,
      "isHorizontal": True
    })
    circuit["wires"].append({
      "x": x + 1,
      "y": allocated_wires[B][1],
      "length": y + 3 - allocated_wires[B][1],
      "isHorizontal": False
    })
    circuit["wires"].append({
      "x": x + 1,
      "y": y + 3,
      "length": 1,
      "isHorizontal": True
    })
    circuit["components"].append({
      "name": "com.ra4king.circuitsim.gui.peers.gates.NorGatePeer",
      "x": x + 2,
      "y": y,
      "properties": {
        "Bitsize": "1"
      }
    })
    circuit["wires"].append({
      "x": x + 6,
      "y": allocated_wires[Y][1],
      "length": y + 2 - allocated_wires[Y][1],
      "isHorizontal": False
    })
  elif gate["type"] == "NOT":
    x = next(x_level)
    for _ in range(4):
      next(x_level)
    A = gate["connections"]["A"]
    assert len(A) == 1
    A = A[0]

    Y = gate["connections"]["Y"]
    assert len(Y) == 1
    Y = Y[0]

    circuit["wires"].append({
      "x": x,
      "y": allocated_wires[A][1],
      "length": y + 1 - allocated_wires[A][1],
      "isHorizontal": False
    })
    circuit["wires"].append({
      "x": x,
      "y": y + 1,
      "length": 1,
      "isHorizontal": True
    })
    circuit["components"].append({
      "name": "com.ra4king.circuitsim.gui.peers.gates.NotGatePeer",
      "x": x + 1,
      "y": y,
      "properties": {
        "Bitsize": "1"
      }
    })
    circuit["wires"].append({
      "x": x + 4,
      "y": allocated_wires[Y][1],
      "length": y + 1 - allocated_wires[Y][1],
      "isHorizontal": False
    })
  elif gate["type"] == "DFF":
    x = next(x_level)
    for _ in range(6):
      next(x_level)
    C = gate["connections"]["C"]
    assert len(C) == 1
    C = C[0]

    D = gate["connections"]["D"]
    assert len(D) == 1
    D = D[0]

    Q = gate["connections"]["Q"]
    assert len(Q) == 1
    Q = Q[0]

    circuit["wires"].append({
      "x": x,
      "y": allocated_wires[C][1],
      "length": y + 1 - allocated_wires[C][1],
      "isHorizontal": False
    })
    circuit["wires"].append({
      "x": x,
      "y": y + 1,
      "length": 2,
      "isHorizontal": True
    })
    circuit["wires"].append({
      "x": x + 1,
      "y": allocated_wires[D][1],
      "length": y + 3 - allocated_wires[D][1],
      "isHorizontal": False
    })
    circuit["wires"].append({
      "x": x + 1,
      "y": y + 3,
      "length": 1,
      "isHorizontal": True
    })
    circuit["components"].append({
      "name": "com.ra4king.circuitsim.gui.peers.memory.DFlipFlopPeer",
      "x": x + 2,
      "y": y
    })
    circuit["wires"].append({
      "x": x + 6,
      "y": allocated_wires[Q][1],
      "length": y + 1 - allocated_wires[Q][1],
      "isHorizontal": False
    })
  else:
    # not sure what buffers are useful for... (do they need the "enable" key?)
    raise AssertionError(f"unknown gate type {gate['type']}")

upto = next(x_level)
for wire in allocated_wires.values():
  circuit["wires"].append({
    "x": wire[0],
    "y": wire[1],
    "length": upto - wire[0],
    "isHorizontal": True
  })

with open("circuit.sim", "w") as f:
  json.dump({
    "version": "1.9.1",
    "circuits": [circuit]
  }, f)
